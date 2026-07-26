"""Render a wiring diagram to a self-contained SVG string.

The frontend renders this SVG directly (Flutter's flutter_svg). We draw the
board on the left, the component on the right, and coloured wires between the
mapped pins with labels. It is schematic, not photo-realistic — the goal is a
clear "connect this to that" reference.
"""
from __future__ import annotations

from html import escape
from typing import Dict

from app.models import WiringDiagram

# Wire colour per net type — matches common breadboard conventions.
_NET_COLORS: Dict[str, str] = {
    "5v": "#e53935",
    "3v3": "#e53935",
    "3.3v": "#e53935",
    "vin": "#e53935",
    "gnd": "#212121",
    "ground": "#212121",
}
_DEFAULT_WIRE = "#1e88e5"


def _wire_color(to_pin: str) -> str:
    key = to_pin.strip().lower()
    for token, color in _NET_COLORS.items():
        if token in key:
            return color
    return _DEFAULT_WIRE


def render(diagram: WiringDiagram, component_name: str) -> str:
    conns = diagram.connections
    row_h = 46
    top = 90
    height = top + max(len(conns), 1) * row_h + 40
    width = 520

    board_x = 40
    comp_x = width - 220
    box_w = 180

    parts = []
    parts.append(
        # Note: no width/height attributes — flutter_svg sizes via viewBox,
        # and percentage dimensions are not reliably supported by renderers.
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="Segoe UI, Roboto, sans-serif">'
    )
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#fafafa"/>')

    board_label = diagram.board.value.upper()
    # Board box.
    parts.append(
        f'<rect x="{board_x}" y="{top - 40}" width="{box_w}" height="{len(conns) * row_h + 20}" '
        f'rx="10" fill="#e3f2fd" stroke="#1565c0" stroke-width="2"/>'
    )
    parts.append(
        f'<text x="{board_x + box_w / 2}" y="{top - 18}" text-anchor="middle" '
        f'font-size="16" font-weight="700" fill="#0d47a1">{escape(board_label)}</text>'
    )
    # Component box.
    parts.append(
        f'<rect x="{comp_x}" y="{top - 40}" width="{box_w}" height="{len(conns) * row_h + 20}" '
        f'rx="10" fill="#f1f8e9" stroke="#2e7d32" stroke-width="2"/>'
    )
    parts.append(
        f'<text x="{comp_x + box_w / 2}" y="{top - 18}" text-anchor="middle" '
        f'font-size="14" font-weight="700" fill="#1b5e20">{escape(component_name[:22])}</text>'
    )

    for i, conn in enumerate(conns):
        y = top + i * row_h + 12
        color = _wire_color(conn.to_pin)
        bx = board_x + box_w
        cx = comp_x
        # Wire.
        midx = (bx + cx) / 2
        parts.append(
            f'<path d="M {bx} {y} C {midx} {y}, {midx} {y}, {cx} {y}" '
            f'stroke="{color}" stroke-width="3" fill="none"/>'
        )
        parts.append(f'<circle cx="{bx}" cy="{y}" r="4" fill="{color}"/>')
        parts.append(f'<circle cx="{cx}" cy="{y}" r="4" fill="{color}"/>')
        # Board-side pin label.
        parts.append(
            f'<text x="{bx - 8}" y="{y - 6}" text-anchor="end" font-size="13" '
            f'font-weight="600" fill="#0d47a1">{escape(conn.to_pin)}</text>'
        )
        # Component-side pin label.
        parts.append(
            f'<text x="{cx + 8}" y="{y - 6}" font-size="13" font-weight="600" '
            f'fill="#1b5e20">{escape(conn.from_pin)}</text>'
        )
        # Note under the wire.
        if conn.note:
            parts.append(
                f'<text x="{midx}" y="{y + 14}" text-anchor="middle" font-size="10" '
                f'fill="#616161">{escape(conn.note)}</text>'
            )

    parts.append("</svg>")
    return "".join(parts)
