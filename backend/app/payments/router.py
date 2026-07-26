"""GCash checkout API — pay in the app, Pro turns on automatically.

    GET  /api/v1/payments/config              plans + gateway info
    POST /api/v1/payments/checkout            -> hosted GCash checkout URL
    GET  /api/v1/payments/status/{reference}  poll (also reconciles with gateway)
    POST /api/v1/payments/webhook             gateway callback (signed)
    GET  /api/v1/payments/entitlement         current Pro state for an email

The customer is never blocked on a human: the webhook grants Pro the moment
the gateway confirms the payment, and `/status` re-checks the gateway itself
so activation still happens if the callback is lost.
"""
from __future__ import annotations

import logging
import re
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.config import settings
from app.payments import entitlements, plans as plan_catalog
from app.payments.providers import (
    EXPIRED,
    FAILED,
    MockProvider,
    PAID,
    PENDING,
    PaymentError,
    get_provider,
)

log = logging.getLogger("payments")

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ------------------------------------------------------------------ models
class PlanOut(BaseModel):
    id: str
    name: str
    price: int
    currency: str
    days: Optional[int]
    description: str
    badge: str
    display_price: str


class PaymentConfig(BaseModel):
    enabled: bool
    provider: str
    methods: List[str]
    currency: str = "PHP"
    #: True when running the built-in fake gateway (development only).
    sandbox: bool = False
    plans: List[PlanOut]


class CheckoutRequest(BaseModel):
    plan_id: str = Field(..., description="Plan id from /config")
    email: str = Field(..., description="Account email that gets Pro")
    uid: str = ""
    #: Firebase ID token. Required when PAYMENTS_REQUIRE_ID_TOKEN=true.
    id_token: str = ""


class CheckoutResponse(BaseModel):
    reference: str
    checkout_url: str
    session_id: str
    plan_id: str
    plan_name: str
    amount: int
    currency: str
    provider: str


class PaymentStatus(BaseModel):
    reference: str
    status: str
    plan_id: str = ""
    plan_name: str = ""
    email: str = ""
    premium: bool = False
    premium_until: Optional[str] = None
    message: str = ""


class EntitlementOut(BaseModel):
    email: str
    premium: bool
    plan: str = ""
    expires_at: Optional[str] = None
    source: str = ""


# ------------------------------------------------------------------ helpers
def _plan_out(plan: plan_catalog.Plan) -> PlanOut:
    return PlanOut(
        id=plan.id,
        name=plan.name,
        price=plan.price,
        currency=plan.currency,
        days=plan.days,
        description=plan.description,
        badge=plan.badge,
        display_price=plan.display_price,
    )


def _new_reference() -> str:
    return f"aes-{uuid.uuid4().hex[:16]}"


def _status_payload(reference: str, payment: Dict[str, Any]) -> PaymentStatus:
    paid = payment.get("status") == PAID
    return PaymentStatus(
        reference=reference,
        status=payment.get("status", PENDING),
        plan_id=payment.get("plan", ""),
        plan_name=payment.get("planName", ""),
        email=payment.get("email", ""),
        premium=paid,
        premium_until=payment.get("premiumUntil"),
        message=(
            "Pro is active on your account."
            if paid
            else "Waiting for GCash to confirm the payment."
        ),
    )


def _activate(reference: str, payment: Dict[str, Any]) -> Dict[str, Any]:
    """Grant Pro for a confirmed payment (idempotent)."""
    plan = plan_catalog.get_plan(payment.get("plan", ""))
    if plan is None:
        log.error("Payment %s references unknown plan %r", reference, payment.get("plan"))
        raise HTTPException(status_code=500, detail="Unknown plan on this payment.")
    entitlements.get_store().activate(reference, plan)
    return entitlements.get_store().get_payment(reference) or payment


# ------------------------------------------------------------------ routes
@router.get("/config", response_model=PaymentConfig)
def payment_config() -> PaymentConfig:
    provider = get_provider()
    return PaymentConfig(
        enabled=provider.available,
        provider=provider.name,
        methods=list(provider.methods),
        sandbox=isinstance(provider, MockProvider),
        plans=[_plan_out(p) for p in plan_catalog.all_plans()],
    )


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(body: CheckoutRequest) -> CheckoutResponse:
    plan = plan_catalog.get_plan(body.plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Unknown plan '{body.plan_id}'.")

    email = body.email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise HTTPException(
            status_code=400,
            detail="A valid account email is required so Pro can be activated.",
        )

    uid = body.uid
    if settings.payments_require_id_token:
        claims = entitlements.verify_id_token(body.id_token)
        if not claims:
            raise HTTPException(
                status_code=401, detail="Sign in again — your session has expired."
            )
        token_email = (claims.get("email") or "").lower()
        if token_email and token_email != email:
            raise HTTPException(
                status_code=403, detail="Email does not match the signed-in account."
            )
        uid = claims.get("uid") or claims.get("sub") or uid

    provider = get_provider()
    reference = _new_reference()
    try:
        session = provider.create_checkout(
            plan=plan,
            reference=reference,
            email=email,
            metadata={"reference": reference, "email": email, "plan": plan.id, "uid": uid},
        )
    except PaymentError as exc:
        log.error("Checkout failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    entitlements.get_store().record_checkout(
        reference=reference,
        email=email,
        uid=uid,
        plan=plan,
        session_id=session.id,
        provider=provider.name,
        checkout_url=session.url,
    )
    return CheckoutResponse(
        reference=reference,
        checkout_url=session.url,
        session_id=session.id,
        plan_id=plan.id,
        plan_name=plan.name,
        amount=plan.price,
        currency=plan.currency,
        provider=provider.name,
    )


@router.get("/status/{reference}", response_model=PaymentStatus)
def payment_status(reference: str) -> PaymentStatus:
    store = entitlements.get_store()
    payment = store.get_payment(reference)
    if payment is None:
        raise HTTPException(status_code=404, detail="Unknown payment reference.")

    if payment.get("status") == PENDING and payment.get("sessionId"):
        # Reconcile with the gateway so a lost webhook never strands a payer.
        try:
            remote = get_provider().fetch_status(payment["sessionId"])
        except PaymentError as exc:
            log.warning("Could not reconcile %s: %s", reference, exc)
            remote = PENDING
        if remote == PAID:
            payment = _activate(reference, payment)
        elif remote in {FAILED, EXPIRED}:
            store.fail(reference, remote)
            payment = store.get_payment(reference) or payment

    return _status_payload(reference, payment)


@router.post("/webhook")
async def webhook(request: Request) -> dict:
    body = await request.body()
    provider = get_provider()
    try:
        event = provider.parse_webhook(request.headers, body)
    except PaymentError as exc:
        log.warning("Rejected webhook: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if event is None:
        return {"received": True, "handled": False}

    store = entitlements.get_store()
    payment = store.get_payment(event.reference)
    if payment is None:
        log.warning("Webhook for unknown reference %s", event.reference)
        return {"received": True, "handled": False}

    if event.status == PAID:
        _activate(event.reference, payment)
    elif event.status in {FAILED, EXPIRED}:
        store.fail(event.reference, event.status)
    return {"received": True, "handled": True}


@router.get("/entitlement", response_model=EntitlementOut)
def entitlement(email: str = Query(..., description="Account email")) -> EntitlementOut:
    record = entitlements.get_store().get_entitlement(email.strip().lower()) or {}
    expires = entitlements._parse_dt(record.get("expiresAt"))
    premium = bool(record.get("premium"))
    if premium and expires is not None and expires <= entitlements._now():
        premium = False
    return EntitlementOut(
        email=email.strip().lower(),
        premium=premium,
        plan=record.get("plan", "") or "",
        expires_at=expires.isoformat() if expires else None,
        source=record.get("source", "") or "",
    )


@router.post("/mock/pay/{reference}", response_model=PaymentStatus)
def mock_pay(reference: str) -> PaymentStatus:
    """Simulate a successful GCash payment (development gateway only)."""
    provider = get_provider()
    if not isinstance(provider, MockProvider):
        raise HTTPException(status_code=404, detail="Not available.")
    store = entitlements.get_store()
    payment = store.get_payment(reference)
    if payment is None:
        raise HTTPException(status_code=404, detail="Unknown payment reference.")
    provider.mark_paid(reference)
    payment = _activate(reference, payment)
    return _status_payload(reference, payment)
