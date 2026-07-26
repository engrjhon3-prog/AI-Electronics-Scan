"""Subscription plans sold through GCash.

Prices are in Philippine pesos. Everything here can be overridden at runtime
with the `PAYMENT_PLANS` environment variable (JSON list), so you can change
pricing without shipping a new build:

    PAYMENT_PLANS='[{"id":"monthly","name":"Pro Monthly","price":149,"days":30}]'
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from pydantic import BaseModel


class Plan(BaseModel):
    id: str
    name: str
    #: Price in whole pesos (gateways are charged in centavos).
    price: int
    #: Access length in days. `None` means lifetime.
    days: Optional[int] = None
    description: str = ""
    #: Marketing badge shown on the paywall ("Best value").
    badge: str = ""
    currency: str = "PHP"

    @property
    def amount_centavos(self) -> int:
        return self.price * 100

    @property
    def display_price(self) -> str:
        suffix = {30: "/mo", 365: "/yr"}.get(self.days or 0, "")
        return f"₱{self.price:,}{suffix}"


_DEFAULT_PLANS: List[dict] = [
    {
        "id": "monthly",
        "name": "Pro Monthly",
        "price": 199,
        "days": 30,
        "description": "Unlimited scans, wiring diagrams, code generation and "
        "7-day cloud storage. Renew any time.",
    },
    {
        "id": "yearly",
        "name": "Pro Yearly",
        "price": 1499,
        "days": 365,
        "description": "Twelve months of Pro — the same as paying for 7½ months.",
        "badge": "Best value",
    },
    {
        "id": "lifetime",
        "name": "Pro Lifetime",
        "price": 2999,
        "days": None,
        "description": "One payment, Pro forever on this account.",
    },
]


def _load() -> Dict[str, Plan]:
    raw = os.environ.get("PAYMENT_PLANS")
    items = _DEFAULT_PLANS
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and parsed:
                items = parsed
        except (ValueError, TypeError):
            # Malformed override — fall back to the built-in price list rather
            # than taking the whole payment service down.
            items = _DEFAULT_PLANS
    plans: Dict[str, Plan] = {}
    for item in items:
        try:
            plan = Plan(**item)
        except Exception:
            continue
        plans[plan.id] = plan
    return plans or {p["id"]: Plan(**p) for p in _DEFAULT_PLANS}


PLANS: Dict[str, Plan] = _load()


def all_plans() -> List[Plan]:
    return list(PLANS.values())


def get_plan(plan_id: str) -> Optional[Plan]:
    return PLANS.get(plan_id)
