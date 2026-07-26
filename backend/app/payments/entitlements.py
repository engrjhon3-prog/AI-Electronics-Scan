"""Where a paid subscription is recorded — and how Pro turns on by itself.

When a GCash payment is confirmed, the backend writes two documents:

    payments/{reference}     the ledger entry (idempotency + support history)
    entitlements/{email}     {premium: true, expiresAt: …}  <- the app reads this

The app already listens to `entitlements/{email}` (see AuthService), so the
write flips the user to Pro within a second, with nobody approving anything.

Firestore is used when the Firebase Admin SDK is configured; otherwise the
same data lands in a local JSON file so the service still runs (and tests
pass) without credentials.
"""
from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.config import settings
from app.payments.plans import Plan

log = logging.getLogger("payments")

PAYMENTS_COLLECTION = "payments"
ENTITLEMENTS_COLLECTION = "entitlements"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


class EntitlementStore:
    """Common behaviour: renewals extend, lifetime never expires."""

    backend = "none"

    # -- to implement ----------------------------------------------------
    def get_payment(self, reference: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def put_payment(self, reference: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    def get_entitlement(self, email: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def put_entitlement(self, email: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    # -- shared ----------------------------------------------------------
    def record_checkout(
        self,
        *,
        reference: str,
        email: str,
        uid: str,
        plan: Plan,
        session_id: str,
        provider: str,
        checkout_url: str,
    ) -> None:
        self.put_payment(
            reference,
            {
                "reference": reference,
                "email": email.lower(),
                "uid": uid,
                "plan": plan.id,
                "planName": plan.name,
                "amount": plan.price,
                "currency": plan.currency,
                "status": "pending",
                "provider": provider,
                "sessionId": session_id,
                "checkoutUrl": checkout_url,
                "createdAt": _iso(_now()),
            },
        )

    def activate(self, reference: str, plan: Plan) -> Dict[str, Any]:
        """Mark a payment paid and grant/extend Pro. Safe to call twice."""
        payment = self.get_payment(reference)
        if payment is None:
            raise KeyError(reference)
        email = (payment.get("email") or "").lower()

        if payment.get("status") == "paid":
            return {
                "already": True,
                "email": email,
                "expiresAt": payment.get("premiumUntil"),
            }

        expires_at: Optional[datetime] = None
        if plan.days is not None:
            base = _now()
            current = self.get_entitlement(email) or {}
            existing = current.get("expiresAt")
            if current.get("premium") and existing:
                parsed = _parse_dt(existing)
                # Renewing early stacks onto the remaining time.
                if parsed and parsed > base:
                    base = parsed
            expires_at = base + timedelta(days=plan.days)

        self.put_entitlement(
            email,
            {
                "premium": True,
                "plan": plan.id,
                "planName": plan.name,
                "expiresAt": expires_at,  # None = lifetime
                "source": "gcash",
                "provider": payment.get("provider", ""),
                "reference": reference,
                "grantedBy": "auto-payment",
                "activatedAt": _now(),
            },
        )
        payment.update(
            {
                "status": "paid",
                "paidAt": _iso(_now()),
                "premiumUntil": _iso(expires_at),
            }
        )
        self.put_payment(reference, payment)
        log.info("Activated Pro for %s (plan=%s, ref=%s)", email, plan.id, reference)
        return {"already": False, "email": email, "expiresAt": _iso(expires_at)}

    def fail(self, reference: str, status: str) -> None:
        payment = self.get_payment(reference)
        if payment is None or payment.get("status") == "paid":
            return
        payment.update({"status": status, "updatedAt": _iso(_now())})
        self.put_payment(reference, payment)


def _parse_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


# --------------------------------------------------------------- Firestore
class FirestoreStore(EntitlementStore):
    backend = "firestore"

    def __init__(self, client: Any) -> None:
        self._db = client

    def get_payment(self, reference: str) -> Optional[Dict[str, Any]]:
        snap = self._db.collection(PAYMENTS_COLLECTION).document(reference).get()
        return snap.to_dict() if snap.exists else None

    def put_payment(self, reference: str, data: Dict[str, Any]) -> None:
        self._db.collection(PAYMENTS_COLLECTION).document(reference).set(data)

    def get_entitlement(self, email: str) -> Optional[Dict[str, Any]]:
        snap = (
            self._db.collection(ENTITLEMENTS_COLLECTION).document(email.lower()).get()
        )
        return snap.to_dict() if snap.exists else None

    def put_entitlement(self, email: str, data: Dict[str, Any]) -> None:
        self._db.collection(ENTITLEMENTS_COLLECTION).document(email.lower()).set(
            data, merge=True
        )


# -------------------------------------------------------------- JSON file
class JsonFileStore(EntitlementStore):
    """Credential-free fallback. Fine for dev; use Firestore in production."""

    backend = "json"

    def __init__(self, path: str) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._data: Dict[str, Dict[str, Any]] = {"payments": {}, "entitlements": {}}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    self._data.update(loaded)
            except (OSError, ValueError):
                log.warning("Could not read payments file %s; starting empty.", path)

    def _flush(self) -> None:
        try:
            directory = os.path.dirname(os.path.abspath(self._path))
            os.makedirs(directory, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as handle:
                json.dump(self._data, handle, indent=1, default=str)
        except OSError as exc:
            log.warning("Could not persist payments file: %s", exc)

    def get_payment(self, reference: str) -> Optional[Dict[str, Any]]:
        return self._data["payments"].get(reference)

    def put_payment(self, reference: str, data: Dict[str, Any]) -> None:
        with self._lock:
            self._data["payments"][reference] = data
            self._flush()

    def get_entitlement(self, email: str) -> Optional[Dict[str, Any]]:
        return self._data["entitlements"].get(email.lower())

    def put_entitlement(self, email: str, data: Dict[str, Any]) -> None:
        with self._lock:
            current = self._data["entitlements"].get(email.lower(), {})
            current.update({k: (_iso(v) if isinstance(v, datetime) else v)
                            for k, v in data.items()})
            self._data["entitlements"][email.lower()] = current
            self._flush()


# ---------------------------------------------------------------- Firebase
_firebase_app: Any = None
_store: Optional[EntitlementStore] = None


def _credentials() -> Any:
    """Build Admin SDK credentials from env, without ever hard-coding keys.

    Accepts either a path (`FIREBASE_SERVICE_ACCOUNT` /
    `GOOGLE_APPLICATION_CREDENTIALS`) or the JSON itself
    (`FIREBASE_SERVICE_ACCOUNT_JSON`), which suits container secrets.
    """
    from firebase_admin import credentials  # imported lazily

    inline = settings.firebase_service_account_json
    if inline:
        return credentials.Certificate(json.loads(inline))
    path = settings.firebase_service_account or os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS", ""
    )
    if path and os.path.exists(path):
        return credentials.Certificate(path)
    return None


def firebase_app() -> Any:
    """Initialise (once) and return the Firebase Admin app, or None."""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app
    try:
        import firebase_admin
    except ImportError:
        log.warning("firebase-admin is not installed — entitlements stay local.")
        return None
    try:
        if firebase_admin._apps:  # already initialised elsewhere
            _firebase_app = firebase_admin.get_app()
            return _firebase_app
        cred = _credentials()
        if cred is None:
            if not settings.firebase_project_id:
                log.warning(
                    "No Firebase credentials configured — entitlements stay local."
                )
                return None
            _firebase_app = firebase_admin.initialize_app(
                options={"projectId": settings.firebase_project_id}
            )
        else:
            options = (
                {"projectId": settings.firebase_project_id}
                if settings.firebase_project_id
                else None
            )
            _firebase_app = firebase_admin.initialize_app(cred, options)
        return _firebase_app
    except Exception as exc:  # bad key, wrong project, clock skew…
        log.warning("Firebase Admin init failed (%s) — entitlements stay local.", exc)
        return None


def get_store() -> EntitlementStore:
    """Return the entitlement store (Firestore when configured)."""
    global _store
    if _store is not None:
        return _store
    app = firebase_app()
    if app is not None:
        try:
            from firebase_admin import firestore

            _store = FirestoreStore(firestore.client(app))
            log.info("Entitlements will be written to Firestore.")
            return _store
        except Exception as exc:
            log.warning("Firestore client unavailable (%s) — using local store.", exc)
    _store = JsonFileStore(settings.payments_db_path)
    return _store


def reset_store() -> None:
    """Drop the cached store (used by tests)."""
    global _store
    _store = None


def verify_id_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a Firebase ID token. Returns claims, or None if unverifiable."""
    app = firebase_app()
    if app is None or not token:
        return None
    try:
        from firebase_admin import auth as fb_auth

        return fb_auth.verify_id_token(token, app=app)
    except Exception as exc:
        log.info("ID token rejected: %s", exc)
        return None
