"""Export the component knowledge base to a Flutter asset.

Bundles everything the app needs to work fully offline: component metadata,
pinouts, per-board wiring (with pre-rendered SVG diagrams), and code snippets.

Usage:  python scripts/export_assets.py
Writes: ../frontend/assets/components.json
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.components import database as db  # noqa: E402
from app.generators import wiring_svg  # noqa: E402


def main() -> None:
    out = []
    for comp in db.all_components():
        wiring = {}
        code = {}
        for board in comp.supported_boards:
            diagram = db.get_wiring(comp.id, board)
            if diagram is not None:
                wiring[board.value] = {
                    "connections": [
                        {"from_pin": c.from_pin, "to_pin": c.to_pin, "note": c.note}
                        for c in diagram.connections
                    ],
                    "notes": diagram.notes,
                    "svg": wiring_svg.render(diagram, comp.name),
                }
            snippet = db.get_code(comp.id, board)
            if snippet is not None:
                code[board.value] = {
                    "title": snippet.title,
                    "description": snippet.description,
                    "libraries": snippet.libraries,
                    "code": snippet.code,
                }
        out.append(
            {
                "id": comp.id,
                "type": comp.type.value,
                "name": comp.name,
                "aliases": comp.aliases,
                "description": comp.description,
                "package": comp.package,
                "datasheet_url": comp.datasheet_url,
                "pins": [p.model_dump() for p in comp.pins],
                "supported_boards": [b.value for b in comp.supported_boards],
                "tags": comp.tags,
                "category": comp.category,
                "wiring": wiring,
                "code": code,
            }
        )

    dest = os.path.join(
        os.path.dirname(__file__), "..", "..", "frontend", "assets", "components.json"
    )
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "components": out}, f, ensure_ascii=False, indent=1)
    print(f"Wrote {len(out)} components -> {os.path.abspath(dest)}")


if __name__ == "__main__":
    main()
