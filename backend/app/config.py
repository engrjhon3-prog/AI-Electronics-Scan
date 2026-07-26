"""Runtime configuration, read from environment variables.

Nothing secret is hard-coded. On Vast.ai (or any host) set these via the
environment. Sensible defaults keep local development friction-free.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


def _split_env(name: str, default: str) -> List[str]:
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass
class Settings:
    app_name: str = "AI Electronics Scanner API"
    version: str = "0.1.0"

    # Comma-separated list of allowed CORS origins ("*" allows all).
    cors_origins: List[str] = field(default_factory=lambda: _split_env("CORS_ORIGINS", "*"))

    # Max upload size in bytes (default 8 MB) to protect the server.
    max_upload_bytes: int = int(os.environ.get("MAX_UPLOAD_BYTES", 8 * 1024 * 1024))

    # Freemium: free tier gets scans + pinouts. Wiring diagrams and code
    # generation require a premium entitlement. In production this flag comes
    # from a verified receipt / Firebase custom claim; here we accept a header
    # for testing. Set REQUIRE_PREMIUM=false to unlock everything (dev mode).
    require_premium: bool = os.environ.get("REQUIRE_PREMIUM", "true").lower() == "true"

    # Shared secret that marks a request as premium during development/testing.
    # In production, replace this check with real receipt/claim verification.
    premium_dev_token: str = os.environ.get("PREMIUM_DEV_TOKEN", "premium-dev")

    # ---------------------------------------------------------- payments
    # Gateway that charges the customer's GCash wallet.
    #   auto (default) -> PayMongo when a key is set, otherwise the mock gateway
    #   paymongo | mock
    payment_provider: str = os.environ.get("PAYMENT_PROVIDER", "auto")

    # PayMongo keys. Never commit these — set them in the host environment.
    paymongo_secret_key: str = os.environ.get("PAYMONGO_SECRET_KEY", "")
    paymongo_webhook_secret: str = os.environ.get("PAYMONGO_WEBHOOK_SECRET", "")

    # Rails offered on the hosted checkout page. GCash only by default.
    payment_methods: List[str] = field(
        default_factory=lambda: _split_env("PAYMENT_METHODS", "gcash")
    )

    # Where the gateway sends the customer after paying / cancelling.
    payments_success_url: str = os.environ.get(
        "PAYMENTS_SUCCESS_URL",
        "https://engrjhon3-prog.github.io/AI-Electronics-Scan/payment-success.html",
    )
    payments_cancel_url: str = os.environ.get(
        "PAYMENTS_CANCEL_URL",
        "https://engrjhon3-prog.github.io/AI-Electronics-Scan/payment-cancelled.html",
    )

    # Reject webhook callbacks whose signed timestamp is older than this
    # (replay protection). Set to 0 to disable the check.
    webhook_tolerance_seconds: int = int(
        os.environ.get("WEBHOOK_TOLERANCE_SECONDS", 5 * 60)
    )

    # Require a valid Firebase ID token when starting a checkout.
    payments_require_id_token: bool = (
        os.environ.get("PAYMENTS_REQUIRE_ID_TOKEN", "false").lower() == "true"
    )

    # Firebase Admin credentials used to grant Pro automatically. Provide a
    # file path *or* the JSON itself (handy for container secrets). Keep the
    # key out of the repository — see docs/GCASH_PAYMENTS.md.
    firebase_service_account: str = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "")
    firebase_service_account_json: str = os.environ.get(
        "FIREBASE_SERVICE_ACCOUNT_JSON", ""
    )
    firebase_project_id: str = os.environ.get("FIREBASE_PROJECT_ID", "")

    # Fallback ledger used when Firebase is not configured (dev / tests).
    payments_db_path: str = os.environ.get("PAYMENTS_DB_PATH", "payments-db.json")


settings = Settings()
