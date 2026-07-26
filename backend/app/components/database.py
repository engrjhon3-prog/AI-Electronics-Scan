"""Built-in component knowledge base.

This is the "brain" behind pinouts, wiring diagrams, and code generation.
Each entry contains everything needed to help a maker wire the part up and
get working firmware, for Arduino (AVR) and ESP32/ESP8266 targets.

The data itself lives in `app/components/catalog/`, one module per category
(passives, semiconductors, ICs, sensors, wireless/IoT, displays, actuators,
power, boards, audio, interface). Adding a component is a matter of appending
a dict to the relevant category module — this file only indexes them.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from app.components.catalog import ALL as _RAW, CATEGORIES
from app.models import (
    Board,
    CodeSnippet,
    Component,
    ComponentType,
    Connection,
    Pin,
    PinType,
    WiringDiagram,
)


# ---------------------------------------------------------------------------
# Build typed objects and lookup indexes at import time.
# ---------------------------------------------------------------------------


def _build_component(raw: dict) -> Component:
    pins = [Pin(**p) for p in raw.get("pins", [])]
    boards = [Board(b) for b in raw.get("wiring", {}).keys()]
    return Component(
        id=raw["id"],
        type=ComponentType(raw["type"]),
        name=raw["name"],
        aliases=raw.get("aliases", []),
        description=raw.get("description", ""),
        package=raw.get("package", ""),
        datasheet_url=raw.get("datasheet_url"),
        pins=pins,
        supported_boards=boards,
        tags=raw.get("tags", []),
        category=raw.get("category", ""),
    )


_COMPONENTS: Dict[str, Component] = {}
_RAW_BY_ID: Dict[str, dict] = {}
_ALIAS_INDEX: Dict[str, str] = {}

for _raw in _RAW:
    comp = _build_component(_raw)
    _COMPONENTS[comp.id] = comp
    _RAW_BY_ID[comp.id] = _raw
    _ALIAS_INDEX[comp.id.lower()] = comp.id
    _ALIAS_INDEX[comp.name.lower()] = comp.id
    for alias in comp.aliases:
        _ALIAS_INDEX[alias.lower()] = comp.id


def all_components() -> List[Component]:
    return list(_COMPONENTS.values())


def categories() -> Dict[str, int]:
    """Catalog section -> number of components in it."""
    return {name: len(entries) for name, entries in CATEGORIES.items()}


def get_component(component_id: str) -> Optional[Component]:
    return _COMPONENTS.get(component_id)


def find_by_alias(text: str) -> Optional[str]:
    """Return a component id whose name/alias appears in `text`, if any."""
    t = text.lower()
    # Exact alias hit first.
    if t in _ALIAS_INDEX:
        return _ALIAS_INDEX[t]
    # Otherwise substring match, preferring the longest alias.
    best: Optional[str] = None
    best_len = 0
    for alias, cid in _ALIAS_INDEX.items():
        if len(alias) >= 3 and alias in t and len(alias) > best_len:
            best = cid
            best_len = len(alias)
    return best


def get_wiring(component_id: str, board: Board) -> Optional[WiringDiagram]:
    raw = _RAW_BY_ID.get(component_id)
    if not raw:
        return None
    wiring = raw.get("wiring", {}).get(board.value)
    if not wiring:
        return None
    connections = [Connection(**c) for c in wiring.get("connections", [])]
    return WiringDiagram(
        component_id=component_id,
        board=board,
        connections=connections,
        notes=wiring.get("notes", []),
    )


def get_code(component_id: str, board: Board) -> Optional[CodeSnippet]:
    raw = _RAW_BY_ID.get(component_id)
    if not raw:
        return None
    code = raw.get("code", {}).get(board.value)
    if not code:
        return None
    return CodeSnippet(
        component_id=component_id,
        board=board,
        title=code.get("title", ""),
        description=code.get("description", ""),
        libraries=code.get("libraries", []),
        code=code.get("code", ""),
    )
