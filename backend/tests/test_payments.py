"""GCash payment flow tests — checkout, webhook, reconciliation, entitlement.

These run against the built-in mock gateway (no network, no keys), which
exercises exactly the same activation path a real PayMongo payment takes.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.payments import entitlements, plans
from app.payments.providers import PayMongoProvider, get_provider, reset_provider

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_store(tmp_path, monkeypatch):
    """Isolate each test behind its own ledger file and gateway instance."""
    monkeypatch.setattr(settings, "payments_db_path", str(tmp_path / "payments.json"))
    monkeypatch.setattr(settings, "payment_provider", "mock")
    monkeypatch.setattr(settings, "payments_require_id_token", False)
    entitlements.reset_store()
    reset_provider()
    yield
    entitlements.reset_store()
    reset_provider()


def _checkout(plan_id: str = "monthly", email: str = "maker@example.com"):
    res = client.post(
        "/api/v1/payments/checkout", json={"plan_id": plan_id, "email": email}
    )
    assert res.status_code == 200, res.text
    return res.json()


# ---------------------------------------------------------------- config
def test_config_lists_plans_in_pesos():
    body = client.get("/api/v1/payments/config").json()
    assert body["enabled"] is True
    assert body["sandbox"] is True  # mock gateway
    assert body["methods"] == ["gcash"]
    ids = {p["id"] for p in body["plans"]}
    assert {"monthly", "yearly", "lifetime"} <= ids
    monthly = next(p for p in body["plans"] if p["id"] == "monthly")
    assert monthly["currency"] == "PHP"
    assert monthly["display_price"].startswith("₱")


# -------------------------------------------------------------- checkout
def test_checkout_returns_a_payable_url():
    body = _checkout()
    assert body["reference"].startswith("aes-")
    assert body["checkout_url"].startswith("http")
    assert body["plan_id"] == "monthly"
    assert body["amount"] == plans.get_plan("monthly").price


def test_checkout_rejects_unknown_plan_and_bad_email():
    assert (
        client.post(
            "/api/v1/payments/checkout",
            json={"plan_id": "nope", "email": "maker@example.com"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/payments/checkout",
            json={"plan_id": "monthly", "email": "not-an-email"},
        ).status_code
        == 400
    )


def test_checkout_requires_verified_token_when_enabled(monkeypatch):
    monkeypatch.setattr(settings, "payments_require_id_token", True)
    res = client.post(
        "/api/v1/payments/checkout",
        json={"plan_id": "monthly", "email": "maker@example.com", "id_token": "bogus"},
    )
    assert res.status_code == 401


# ------------------------------------------------------- payment -> Pro
def test_payment_activates_pro_without_any_admin_step():
    body = _checkout()
    reference = body["reference"]

    pending = client.get(f"/api/v1/payments/status/{reference}").json()
    assert pending["status"] == "pending"
    assert pending["premium"] is False

    paid = client.post(f"/api/v1/payments/mock/pay/{reference}").json()
    assert paid["status"] == "paid"
    assert paid["premium"] is True

    ent = client.get(
        "/api/v1/payments/entitlement", params={"email": "maker@example.com"}
    ).json()
    assert ent["premium"] is True
    assert ent["plan"] == "monthly"
    assert ent["source"] == "gcash"
    expires = datetime.fromisoformat(ent["expires_at"])
    assert timedelta(days=29) < expires - datetime.now(timezone.utc) <= timedelta(days=30)


def test_status_polling_reconciles_a_missed_webhook():
    reference = _checkout()["reference"]
    # The gateway confirms the payment but the callback never arrives.
    assert get_provider().mark_paid(reference) is True

    status = client.get(f"/api/v1/payments/status/{reference}").json()
    assert status["status"] == "paid"
    assert status["premium"] is True


def test_webhook_activates_and_is_idempotent():
    reference = _checkout()["reference"]
    payload = {"reference": reference, "status": "paid"}

    first = client.post("/api/v1/payments/webhook", json=payload).json()
    assert first == {"received": True, "handled": True}
    activated_at = client.get(f"/api/v1/payments/status/{reference}").json()

    client.post("/api/v1/payments/webhook", json=payload)
    again = client.get(f"/api/v1/payments/status/{reference}").json()
    assert again["premium_until"] == activated_at["premium_until"]


def test_webhook_for_unknown_reference_is_ignored():
    res = client.post(
        "/api/v1/payments/webhook", json={"reference": "aes-nope", "status": "paid"}
    )
    assert res.json() == {"received": True, "handled": False}


def test_lifetime_plan_never_expires():
    reference = _checkout(plan_id="lifetime", email="forever@example.com")["reference"]
    client.post(f"/api/v1/payments/mock/pay/{reference}")
    ent = client.get(
        "/api/v1/payments/entitlement", params={"email": "forever@example.com"}
    ).json()
    assert ent["premium"] is True
    assert ent["expires_at"] is None


def test_renewal_stacks_on_remaining_time():
    email = "renewer@example.com"
    first = _checkout(email=email)["reference"]
    client.post(f"/api/v1/payments/mock/pay/{first}")
    second = _checkout(email=email)["reference"]
    client.post(f"/api/v1/payments/mock/pay/{second}")

    ent = client.get("/api/v1/payments/entitlement", params={"email": email}).json()
    remaining = datetime.fromisoformat(ent["expires_at"]) - datetime.now(timezone.utc)
    assert timedelta(days=59) < remaining <= timedelta(days=60)


def test_expired_entitlement_reports_not_premium():
    email = "lapsed@example.com"
    store = entitlements.get_store()
    store.put_entitlement(
        email,
        {
            "premium": True,
            "plan": "monthly",
            "expiresAt": datetime.now(timezone.utc) - timedelta(days=1),
        },
    )
    ent = client.get("/api/v1/payments/entitlement", params={"email": email}).json()
    assert ent["premium"] is False


def test_unknown_reference_status_is_404():
    assert client.get("/api/v1/payments/status/aes-missing").status_code == 404


# ------------------------------------------------------ PayMongo specifics
def _signed_headers(secret: str, body: bytes, timestamp: str) -> dict:
    digest = hmac.new(
        secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256
    ).hexdigest()
    return {"Paymongo-Signature": f"t={timestamp},te={digest},li={digest}"}


def test_paymongo_webhook_signature_is_enforced():
    provider = PayMongoProvider(secret_key="sk_test_x", webhook_secret="whsk_test")
    body = json.dumps(
        {
            "data": {
                "id": "evt_1",
                "attributes": {
                    "type": "checkout_session.payment.paid",
                    "data": {
                        "id": "cs_1",
                        "attributes": {"reference_number": "aes-abc"},
                    },
                },
            }
        }
    ).encode()
    now = str(int(time.time()))

    event = provider.parse_webhook(_signed_headers("whsk_test", body, now), body)
    assert event is not None
    assert event.reference == "aes-abc"
    assert event.status == "paid"

    with pytest.raises(Exception):
        provider.parse_webhook(_signed_headers("wrong-secret", body, now), body)
    with pytest.raises(Exception):
        provider.parse_webhook({}, body)


def test_paymongo_webhook_rejects_stale_timestamps():
    provider = PayMongoProvider(secret_key="sk_test_x", webhook_secret="whsk_test")
    body = b'{"data":{"attributes":{"type":"payment.paid","data":{"attributes":{}}}}}'
    stale = str(int(time.time()) - 3600)
    with pytest.raises(Exception):
        provider.parse_webhook(_signed_headers("whsk_test", body, stale), body)


def test_paymongo_reads_paid_state_from_a_session_resource():
    attrs = {"payments": [{"attributes": {"status": "paid"}}]}
    assert PayMongoProvider._session_status(attrs) == "paid"
    assert PayMongoProvider._session_status({"status": "expired"}) == "expired"
    assert PayMongoProvider._session_status({}) == "pending"
    assert (
        PayMongoProvider._session_status(
            {"payment_intent": {"attributes": {"status": "succeeded"}}}
        )
        == "paid"
    )


def test_provider_selection_prefers_paymongo_when_keyed(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "auto")
    monkeypatch.setattr(settings, "paymongo_secret_key", "sk_live_dummy")
    reset_provider()
    assert get_provider().name == "paymongo"
