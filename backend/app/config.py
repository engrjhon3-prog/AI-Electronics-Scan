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


settings = Settings()
