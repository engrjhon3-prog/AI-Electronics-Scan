"""Identify any component from a photo, using Claude's vision model.

This is the half of the app that isn't a lookup table. The bundled catalog
covers the parts a maker meets most often; when a scan falls outside it, the
photo and whatever the on-device OCR read are sent here, and the model writes a
full catalog entry — pinout, per-board wiring, and a working sketch — for a part
nobody wrote down in advance.

The reply is constrained by a JSON Schema (structured outputs), so it always
lands in the same shape as a hand-curated entry, and every result is cached so
the next person who scans that part gets it instantly and for free.
"""
from __future__ import annotations

import base64
import json
import logging
from typing import Any, Dict, Optional, Tuple

from app.ai import cache as component_cache
from app.ai.schema import IDENTIFY_SCHEMA, SYSTEM_PROMPT, to_catalog_entry
from app.config import settings
from app.generators import wiring_svg
from app.models import Board, Component, ComponentType, Connection, Pin, WiringDiagram

log = logging.getLogger("ai")

_MEDIA_TYPES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"GIF8": "image/gif",
    b"RIFF": "image/webp",
}


class AiUnavailable(RuntimeError):
    """No API key configured, or the SDK isn't installed."""


class AiError(RuntimeError):
    """The model call failed or returned something unusable."""


def is_available() -> bool:
    if not settings.anthropic_api_key:
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def _media_type(data: bytes) -> str:
    for magic, media_type in _MEDIA_TYPES.items():
        if data.startswith(magic):
            return media_type
    return "image/jpeg"


def _client():
    if not settings.anthropic_api_key:
        raise AiUnavailable(
            "AI identification is not configured on this server "
            "(ANTHROPIC_API_KEY is unset)."
        )
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - depends on deployment
        raise AiUnavailable(
            "The anthropic package is not installed on this server."
        ) from exc
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _user_prompt(ocr_text: str, hint: str) -> str:
    parts = [
        "Identify the electronic component in this photo and write its "
        "reference entry."
    ]
    if ocr_text.strip():
        parts.append(
            "The app's on-device OCR read this text off the part — treat it as "
            "a strong but not infallible signal, since OCR misreads characters:\n"
            f"{ocr_text.strip()[:600]}"
        )
    else:
        parts.append("The on-device OCR could not read any text off the part.")
    if hint.strip():
        parts.append(f"The user adds: {hint.strip()[:300]}")
    parts.append(
        "The app already covers the common basics (LEDs, resistors, NE555, "
        "DHT11/22, HC-SR04, SG90, SSD1306, MPU-6050, ESP32, popular radios). "
        "You are being asked because this part was not matched, so look "
        "carefully before concluding it is one of those."
    )
    return "\n\n".join(parts)


def identify(
    image: bytes,
    *,
    ocr_text: str = "",
    hint: str = "",
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Identify a component from `image`.

    Returns `(result, entry)` where `result` carries the model's confidence and
    reasoning, and `entry` is a catalog-shaped component (with rendered wiring
    SVGs) ready for the app to display and store.
    """
    client = _client()
    encoded = base64.standard_b64encode(image).decode("ascii")

    try:
        with client.messages.stream(
            model=settings.ai_model,
            max_tokens=settings.ai_max_tokens,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    # The prompt is identical on every scan — cache it so only
                    # the photo is billed at full rate.
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            output_config={
                "effort": settings.ai_effort,
                "format": {"type": "json_schema", "schema": IDENTIFY_SCHEMA},
            },
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": _media_type(image),
                                "data": encoded,
                            },
                        },
                        {"type": "text", "text": _user_prompt(ocr_text, hint)},
                    ],
                }
            ],
        ) as stream:
            message = stream.get_final_message()
    except AiUnavailable:
        raise
    except Exception as exc:  # network, auth, rate limit …
        log.error("Vision call failed: %s", exc)
        raise AiError(f"The AI service could not be reached: {exc}") from exc

    if message.stop_reason == "refusal":
        raise AiError(
            "The AI declined to analyse this image. Try a photo of just the "
            "component."
        )
    if message.stop_reason == "max_tokens":
        raise AiError("The AI response was cut short — please try again.")

    text = next((b.text for b in message.content if b.type == "text"), "")
    try:
        payload = json.loads(text)
    except ValueError as exc:
        log.error("Unparseable model reply: %.400s", text)
        raise AiError("The AI returned an unreadable answer.") from exc

    entry = to_catalog_entry(payload["component"])
    entry["id"] = component_cache.normalise_id(entry["id"]) or "unknown_component"
    _validate(entry)
    _render_diagrams(entry)

    result = {
        "identified": bool(payload.get("identified")),
        "confidence": float(payload.get("confidence") or 0.0),
        "detected_text": payload.get("detected_text", ""),
        "reasoning": payload.get("reasoning", ""),
        "advice": payload.get("advice", ""),
        "usage": {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
            "cache_read_input_tokens": getattr(
                message.usage, "cache_read_input_tokens", 0
            ),
        },
    }
    return result, entry


def _validate(entry: Dict[str, Any]) -> None:
    """Reject anything the app couldn't render, before it reaches the cache."""
    try:
        ComponentType(entry["type"])
    except ValueError:
        entry["type"] = "unknown"
    entry["pins"] = [
        pin for pin in entry.get("pins", []) if Pin(**pin) is not None
    ]
    for board in list(entry.get("wiring", {})):
        try:
            Board(board)
        except ValueError:
            entry["wiring"].pop(board)
    for board in list(entry.get("code", {})):
        try:
            Board(board)
        except ValueError:
            entry["code"].pop(board)
    entry["supported_boards"] = list(entry.get("wiring", {}).keys())
    if not entry.get("name"):
        raise AiError("The AI did not name the component.")


def _render_diagrams(entry: Dict[str, Any]) -> None:
    """Pre-render wiring SVGs so the app displays them exactly like built-ins."""
    for board, wiring in entry.get("wiring", {}).items():
        diagram = WiringDiagram(
            component_id=entry["id"],
            board=Board(board),
            connections=[Connection(**c) for c in wiring.get("connections", [])],
            notes=wiring.get("notes", []),
        )
        wiring["svg"] = wiring_svg.render(diagram, entry["name"])


def lookup_cached(token: str) -> Optional[Dict[str, Any]]:
    """Return a previously identified component matching `token`, if any."""
    return component_cache.get_cache().find_by_alias(token)


def remember(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Store an identification so everyone else gets it instantly."""
    stamped = component_cache.stamp(entry, model=settings.ai_model)
    component_cache.get_cache().put(stamped)
    return stamped


def as_component(entry: Dict[str, Any]) -> Component:
    """Typed view of a cached entry, for the REST response model."""
    return Component(
        id=entry["id"],
        type=ComponentType(entry.get("type", "unknown")),
        name=entry.get("name", ""),
        aliases=entry.get("aliases", []),
        description=entry.get("description", ""),
        package=entry.get("package", ""),
        datasheet_url=entry.get("datasheet_url"),
        pins=[Pin(**p) for p in entry.get("pins", [])],
        supported_boards=[Board(b) for b in entry.get("wiring", {})],
        tags=entry.get("tags", []),
        category=entry.get("category", "ai-identified"),
    )
