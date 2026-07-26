"""Shared access control for paid endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException

from app.config import settings
from app.payments import entitlements


def require_premium(
    x_premium_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> None:
    """Gate premium features.

    Accepts, in order:
      1. A Firebase ID token (`Authorization: Bearer …`) whose account holds a
         live entitlement — which is exactly what a paid GCash checkout writes.
      2. The development token in `X-Premium-Token`.
    """
    if not settings.require_premium:
        return
    if x_premium_token and x_premium_token == settings.premium_dev_token:
        return
    if authorization and authorization.lower().startswith("bearer "):
        claims = entitlements.verify_id_token(authorization.split(" ", 1)[1].strip())
        if claims:
            if claims.get("premium") is True or claims.get("admin") is True:
                return
            email = (claims.get("email") or "").lower()
            record = entitlements.get_store().get_entitlement(email) if email else None
            if record and record.get("premium"):
                expires = entitlements._parse_dt(record.get("expiresAt"))
                if expires is None or expires > entitlements._now():
                    return
    raise HTTPException(
        status_code=402,
        detail="This feature requires a Pro subscription. Subscribe with GCash "
        "in the app, then retry with your account token.",
    )
