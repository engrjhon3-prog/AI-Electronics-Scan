"""The component knowledge base, split by category.

Every module exports `ITEMS`, a list of plain dicts. Adding a part is just a
matter of appending one dict to the right category — nothing else to register.

Each entry may declare:
    id, type, name, aliases, description, package, datasheet_url, tags, pins,
    wiring   -> {board: {connections, notes}}
    code     -> {board: {title, description, libraries, code}}

Boards are the values of `app.models.Board` ("uno", "nano", "esp32", "esp8266").
"""
from __future__ import annotations

from typing import Dict, List

from app.components.catalog import (
    actuators,
    audio,
    boards,
    displays,
    ics,
    interface,
    passives,
    power,
    semiconductors,
    sensors_env,
    sensors_motion,
    wireless,
)

#: Category label -> entries, in the order they are presented.
CATEGORIES: Dict[str, List[dict]] = {
    "passives": passives.ITEMS,
    "semiconductors": semiconductors.ITEMS,
    "ics": ics.ITEMS,
    "sensors-environment": sensors_env.ITEMS,
    "sensors-motion": sensors_motion.ITEMS,
    "wireless": wireless.ITEMS,
    "displays": displays.ITEMS,
    "actuators": actuators.ITEMS,
    "power": power.ITEMS,
    "boards": boards.ITEMS,
    "audio": audio.ITEMS,
    "interface": interface.ITEMS,
}


def _flatten() -> List[dict]:
    seen: Dict[str, str] = {}
    items: List[dict] = []
    for category, entries in CATEGORIES.items():
        for entry in entries:
            component_id = entry["id"]
            if component_id in seen:
                raise ValueError(
                    f"Duplicate component id {component_id!r} in {category} "
                    f"(already defined in {seen[component_id]})"
                )
            seen[component_id] = category
            entry.setdefault("category", category)
            items.append(entry)
    return items


ALL: List[dict] = _flatten()
