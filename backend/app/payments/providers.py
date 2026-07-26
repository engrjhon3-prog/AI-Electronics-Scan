"""Payment gateways that can charge a GCash wallet.

The app never talks to GCash directly: a licensed gateway (PayMongo by
default) hosts the checkout page, the customer approves the payment inside
GCash, and the gateway tells us — by webhook and/or by polling — that the
money arrived. Only then does the backend grant Pro. No human in the loop.

Providers implement a tiny interface so a different gateway (Xendit, Maya
Business, Dragonpay …) can be dropped in without touching the API layer:

    create_checkout()  -> hosted checkout URL for the customer
    fetch_status()     -> "pending" | "paid" | "failed" | "expired"
    parse_webhook()    -> verified (reference, status) from a gateway callback
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional

import httpx

from app.config import settings
from app.payments.plans import Plan

log = logging.getLogger("payments")

PENDING = "pending"
PAID = "paid"
FAILED = "failed"
EXPIRED = "expired"


class PaymentError(RuntimeError):
    """The gateway rejected a request or is unreachable."""


@dataclass
class CheckoutSession:
    """A hosted checkout the customer is sent to."""

    id: str
    url: str
    reference: str
    amount: int  # centavos
    currency: str = "PHP"
    status: str = PENDING
    raw: dict = field(default_factory=dict)


@dataclass
class WebhookEvent:
    """A verified gateway callback."""

    reference: str
    status: str
    session_id: str = ""
    event_id: str = ""
    raw: dict = field(default_factory=dict)


class PaymentProvider:
    name = "none"
    #: Wallets/rails the provider is configured to accept.
    methods: list[str] = []

    @property
    def available(self) -> bool:
        return False

    def create_checkout(
        self,
        *,
        plan: Plan,
        reference: str,
        email: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> CheckoutSession:
        raise NotImplementedError

    def fetch_status(self, session_id: str) -> str:
        raise NotImplementedError

    def parse_webhook(self, headers: Mapping[str, str], body: bytes) -> Optional[WebhookEvent]:
        raise NotImplementedError


# ---------------------------------------------------------------- PayMongo
class PayMongoProvider(PaymentProvider):
    """PayMongo Checkout Sessions with GCash as a payment method.

    Docs: https://developers.paymongo.com/docs/checkout-session
    Only the secret key ever lives on the server; the app receives a URL.
    """

    name = "paymongo"
    base_url = "https://api.paymongo.com/v1"

    def __init__(
        self,
        secret_key: str = "",
        webhook_secret: str = "",
        methods: Optional[list[str]] = None,
        timeout: float = 20.0,
    ) -> None:
        self.secret_key = secret_key or settings.paymongo_secret_key
        self.webhook_secret = webhook_secret or settings.paymongo_webhook_secret
        self.methods = methods or settings.payment_methods
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self.secret_key)

    # -- helpers ---------------------------------------------------------
    @property
    def _auth_header(self) -> str:
        token = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        return f"Basic {token}"

    def _request(self, method: str, path: str, payload: Optional[dict] = None) -> dict:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.request(
                    method,
                    f"{self.base_url}{path}",
                    headers={
                        "Authorization": self._auth_header,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    content=json.dumps(payload) if payload is not None else None,
                )
        except httpx.HTTPError as exc:  # network / DNS / timeout
            raise PaymentError(f"Could not reach PayMongo: {exc}") from exc

        if res.status_code >= 400:
            detail = ""
            try:
                errors = res.json().get("errors") or []
                detail = "; ".join(e.get("detail", "") for e in errors)
            except ValueError:
                detail = res.text[:200]
            raise PaymentError(f"PayMongo error {res.status_code}: {detail}")
        return res.json()

    @staticmethod
    def _session_status(attributes: dict) -> str:
        """Derive a simple status from a checkout-session resource."""
        payments = attributes.get("payments") or []
        for payment in payments:
            status = (payment.get("attributes") or {}).get("status")
            if status == "paid":
                return PAID
            if status in {"failed", "cancelled"}:
                return FAILED
        intent = (attributes.get("payment_intent") or {}).get("attributes") or {}
        if intent.get("status") == "succeeded":
            return PAID
        if attributes.get("status") == "expired":
            return EXPIRED
        return PENDING

    # -- interface -------------------------------------------------------
    def create_checkout(
        self,
        *,
        plan: Plan,
        reference: str,
        email: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> CheckoutSession:
        body = {
            "data": {
                "attributes": {
                    "line_items": [
                        {
                            "name": plan.name,
                            "quantity": 1,
                            "amount": plan.amount_centavos,
                            "currency": plan.currency,
                            "description": plan.description[:255] or plan.name,
                        }
                    ],
                    "payment_method_types": self.methods,
                    "description": f"{settings.app_name} — {plan.name}",
                    "reference_number": reference,
                    "success_url": f"{settings.payments_success_url}?ref={reference}",
                    "cancel_url": f"{settings.payments_cancel_url}?ref={reference}",
                    "send_email_receipt": bool(email),
                    "show_description": True,
                    "show_line_items": True,
                    "billing": {"email": email} if email else None,
                    "metadata": {k: str(v) for k, v in (metadata or {}).items()},
                }
            }
        }
        attrs = body["data"]["attributes"]
        body["data"]["attributes"] = {k: v for k, v in attrs.items() if v is not None}

        data = self._request("POST", "/checkout_sessions", body).get("data", {})
        attributes = data.get("attributes", {})
        url = attributes.get("checkout_url")
        if not url:
            raise PaymentError("PayMongo did not return a checkout URL.")
        return CheckoutSession(
            id=data.get("id", ""),
            url=url,
            reference=reference,
            amount=plan.amount_centavos,
            currency=plan.currency,
            status=self._session_status(attributes),
            raw=data,
        )

    def fetch_status(self, session_id: str) -> str:
        data = self._request("GET", f"/checkout_sessions/{session_id}").get("data", {})
        return self._session_status(data.get("attributes", {}))

    def parse_webhook(self, headers: Mapping[str, str], body: bytes) -> Optional[WebhookEvent]:
        if not self._verify_signature(headers, body):
            raise PaymentError("Invalid webhook signature.")
        try:
            payload = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise PaymentError("Webhook body is not valid JSON.") from exc

        event = payload.get("data", {})
        event_attrs = event.get("attributes", {})
        event_type = event_attrs.get("type", "")
        resource = event_attrs.get("data", {}) or {}
        resource_attrs = resource.get("attributes", {}) or {}

        # `checkout_session.payment.paid` carries the session; `payment.paid`
        # and `payment.failed` carry the payment itself.
        reference = (
            resource_attrs.get("reference_number")
            or (resource_attrs.get("metadata") or {}).get("reference")
            or ((resource_attrs.get("data") or {}).get("attributes") or {}).get(
                "reference_number", ""
            )
            or ""
        )
        if event_type.endswith("payment.paid"):
            status = PAID
        elif event_type.endswith("payment.failed"):
            status = FAILED
        elif event_type.endswith("expired"):
            status = EXPIRED
        else:
            return None
        if not reference:
            return None
        return WebhookEvent(
            reference=reference,
            status=status,
            session_id=resource.get("id", ""),
            event_id=event.get("id", ""),
            raw=payload,
        )

    def _verify_signature(self, headers: Mapping[str, str], body: bytes) -> bool:
        """Verify the `Paymongo-Signature: t=…,te=…,li=…` header.

        The signed payload is `<timestamp>.<raw body>`; `te` is used in test
        mode and `li` in live mode.
        """
        if not self.webhook_secret:
            # Refuse to trust unverifiable callbacks — a missing secret would
            # otherwise let anyone grant themselves Pro.
            log.warning("PAYMONGO_WEBHOOK_SECRET is not set; rejecting webhook.")
            return False
        raw = ""
        for key, value in headers.items():
            if key.lower() == "paymongo-signature":
                raw = value
                break
        if not raw:
            return False
        parts = dict(
            piece.split("=", 1) for piece in raw.split(",") if "=" in piece
        )
        timestamp = parts.get("t", "")
        if not timestamp:
            return False
        if settings.webhook_tolerance_seconds > 0:
            try:
                age = abs(time.time() - int(timestamp))
            except ValueError:
                return False
            if age > settings.webhook_tolerance_seconds:
                log.warning("Rejecting webhook: timestamp is %.0fs old.", age)
                return False
        expected = hmac.new(
            self.webhook_secret.encode(),
            f"{timestamp}.".encode() + body,
            hashlib.sha256,
        ).hexdigest()
        return any(
            hmac.compare_digest(expected, parts.get(key, ""))
            for key in ("te", "li")
        )


# -------------------------------------------------------------------- mock
class MockProvider(PaymentProvider):
    """In-process gateway for local development and tests.

    Creates a checkout that is marked paid by calling
    `POST /api/v1/payments/mock/pay/{reference}` — the same code path a real
    GCash payment takes, minus the money.
    """

    name = "mock"
    methods = ["gcash"]

    def __init__(self) -> None:
        self._sessions: Dict[str, str] = {}
        self._by_reference: Dict[str, str] = {}

    @property
    def available(self) -> bool:
        return True

    def create_checkout(
        self,
        *,
        plan: Plan,
        reference: str,
        email: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> CheckoutSession:
        session_id = f"cs_mock_{reference}"
        self._sessions[session_id] = PENDING
        self._by_reference[reference] = session_id
        return CheckoutSession(
            id=session_id,
            url=f"{settings.payments_success_url}?ref={reference}&mock=1",
            reference=reference,
            amount=plan.amount_centavos,
            currency=plan.currency,
        )

    def fetch_status(self, session_id: str) -> str:
        return self._sessions.get(session_id, PENDING)

    def mark_paid(self, reference: str) -> bool:
        session_id = self._by_reference.get(reference)
        if not session_id:
            return False
        self._sessions[session_id] = PAID
        return True

    def parse_webhook(self, headers: Mapping[str, str], body: bytes) -> Optional[WebhookEvent]:
        payload = json.loads(body.decode("utf-8") or "{}")
        reference = payload.get("reference", "")
        if not reference:
            return None
        return WebhookEvent(
            reference=reference,
            status=payload.get("status", PAID),
            session_id=self._by_reference.get(reference, ""),
            raw=payload,
        )


# ------------------------------------------------------------------ lookup
_provider: Optional[PaymentProvider] = None


def get_provider() -> PaymentProvider:
    """Return the configured gateway (cached)."""
    global _provider
    if _provider is not None:
        return _provider
    choice = settings.payment_provider.lower()
    if choice in {"auto", "paymongo"}:
        paymongo = PayMongoProvider()
        if paymongo.available:
            _provider = paymongo
            return _provider
        if choice == "paymongo":
            log.warning("PAYMENT_PROVIDER=paymongo but PAYMONGO_SECRET_KEY is unset.")
    _provider = MockProvider()
    if choice not in {"mock", "auto"}:
        log.warning("Unknown PAYMENT_PROVIDER=%r — falling back to mock.", choice)
    return _provider


def reset_provider() -> None:
    """Drop the cached provider (used by tests after changing settings)."""
    global _provider
    _provider = None
