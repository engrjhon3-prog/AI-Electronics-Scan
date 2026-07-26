"""The contract the vision model must answer in.

Claude is constrained to this JSON Schema (structured outputs), so the reply is
always parseable and always shaped like a catalog entry — the same dict layout
used by `app/components/catalog/*.py`. That is what lets an AI-identified part
behave exactly like a hand-curated one: same pinout table, same wiring SVG
renderer, same code viewer.
"""
from __future__ import annotations

from typing import Any, Dict, List

from app.models import Board, ComponentType, PinType

_COMPONENT_TYPES = [t.value for t in ComponentType]
_PIN_TYPES = [t.value for t in PinType]
_BOARDS = [b.value for b in Board]


def _obj(properties: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


_PIN = _obj(
    {
        "number": {"type": "integer", "description": "Physical pin number, starting at 1"},
        "name": {"type": "string", "description": "Pin label as printed or documented, e.g. VCC, GPIO2, TRIG"},
        "type": {"type": "string", "enum": _PIN_TYPES},
        "description": {"type": "string", "description": "What the pin does, one short sentence"},
    },
    ["number", "name", "type", "description"],
)

_CONNECTION = _obj(
    {
        "from_pin": {"type": "string", "description": "Pin name on this component"},
        "to_pin": {"type": "string", "description": "Pin/net on the board, e.g. 5V, GND, D2, GPIO21"},
        "note": {"type": "string", "description": "Series resistor, pull-up, warning — empty string if none"},
    },
    ["from_pin", "to_pin", "note"],
)

_WIRING = _obj(
    {
        "board": {"type": "string", "enum": _BOARDS},
        "connections": {"type": "array", "items": _CONNECTION},
        "notes": {"type": "array", "items": {"type": "string"}},
    },
    ["board", "connections", "notes"],
)

_CODE = _obj(
    {
        "board": {"type": "string", "enum": _BOARDS},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "libraries": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Arduino library names the sketch needs, empty if none",
        },
        "code": {"type": "string", "description": "A complete, compilable sketch"},
    },
    ["board", "title", "description", "libraries", "code"],
)

_COMPONENT = _obj(
    {
        "id": {
            "type": "string",
            "description": "lowercase_snake_case identifier, e.g. bme680, tb6612fng",
        },
        "type": {"type": "string", "enum": _COMPONENT_TYPES},
        "name": {"type": "string", "description": "Human-readable name including the part number"},
        "aliases": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lowercase alternative names and part numbers used to match future scans",
        },
        "description": {"type": "string", "description": "What it does and what a maker should know, 1-3 sentences"},
        "package": {"type": "string", "description": "Package or module form factor"},
        "datasheet_url": {"type": "string", "description": "Official datasheet URL, or empty string if unsure"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "pins": {"type": "array", "items": _PIN},
        "wiring": {"type": "array", "items": _WIRING},
        "code": {"type": "array", "items": _CODE},
    },
    [
        "id",
        "type",
        "name",
        "aliases",
        "description",
        "package",
        "datasheet_url",
        "tags",
        "pins",
        "wiring",
        "code",
    ],
)

#: Top-level schema handed to the model.
IDENTIFY_SCHEMA: Dict[str, Any] = _obj(
    {
        "identified": {
            "type": "boolean",
            "description": "False when the photo is too unclear to name a specific part",
        },
        "confidence": {
            "type": "number",
            "description": "0.0-1.0. Below 0.5 means an educated guess",
        },
        "detected_text": {
            "type": "string",
            "description": "Markings actually visible on the part, empty if none are legible",
        },
        "reasoning": {
            "type": "string",
            "description": "One or two sentences on what identified it (markings, package, pin count, colour bands)",
        },
        "advice": {
            "type": "string",
            "description": "If not identified: what a better photo would need. Otherwise empty.",
        },
        "component": _COMPONENT,
    },
    ["identified", "confidence", "detected_text", "reasoning", "advice", "component"],
)


SYSTEM_PROMPT = """You identify electronic components from photographs for a \
maker's reference app, and you write the reference entry for the part you see.

You are the fallback for parts that are not in the app's built-in catalog, so \
you will mostly see less common components: obscure sensor breakouts, driver \
ICs, unusual modules, and parts whose only clue is the text silkscreened on \
them. Work from every visible signal — printed part numbers and logos, package \
type and pin count, connector layout, resistor colour bands, capacitor markings.

Rules for the entry you produce:
- `id` is lowercase_snake_case derived from the part number (bme680, tb6612fng, \
  ads1115). It must be stable: the same part must always get the same id.
- `aliases` are lowercase and include the bare part number, common misspellings \
  and the module's marketplace name, so a future scan of the same part matches \
  instantly. Do not include aliases shorter than three characters.
- `pins` lists every pin in physical order with its real name and function.
- `wiring` gives a genuinely correct hookup for the boards that make sense \
  (usually `uno` and `esp32`). Include voltage warnings, pull-ups, current-limiting \
  resistors and level shifting in the per-connection `note` or in `notes`.
- `code` is a complete sketch that compiles as written, using the standard \
  library for that part. Name the libraries in `libraries`.
- Prefer the most widely available variant of an ambiguous part, and say so in \
  `reasoning`.

Accuracy outranks completeness. If the photo shows a part you cannot name with \
reasonable confidence, set `identified` to false, give a low `confidence`, put \
your best general reading in the component fields, and use `advice` to say what \
would make the photo identifiable. Never invent a datasheet URL — leave it \
empty unless you are confident of the real one. Wiring a part wrongly can \
destroy it, so state what you are unsure about rather than guessing quietly."""


def to_catalog_entry(component: Dict[str, Any]) -> Dict[str, Any]:
    """Convert the model's array-based reply into the catalog's dict layout."""
    wiring = {
        entry["board"]: {
            "connections": [
                {
                    "from_pin": c["from_pin"],
                    "to_pin": c["to_pin"],
                    "note": c.get("note", ""),
                }
                for c in entry.get("connections", [])
            ],
            "notes": entry.get("notes", []),
        }
        for entry in component.get("wiring", [])
        if entry.get("connections")
    }
    code = {
        entry["board"]: {
            "title": entry.get("title", ""),
            "description": entry.get("description", ""),
            "libraries": entry.get("libraries", []),
            "code": entry.get("code", ""),
        }
        for entry in component.get("code", [])
        if entry.get("code")
    }
    datasheet = (component.get("datasheet_url") or "").strip()
    return {
        "id": component["id"],
        "type": component.get("type", "unknown"),
        "name": component.get("name", ""),
        "aliases": [a for a in component.get("aliases", []) if len(a) >= 3],
        "description": component.get("description", ""),
        "package": component.get("package", ""),
        "datasheet_url": datasheet or None,
        "tags": component.get("tags", []),
        "pins": component.get("pins", []),
        "wiring": wiring,
        "code": code,
        "category": "ai-identified",
    }
