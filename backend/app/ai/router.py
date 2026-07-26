"""AI identification API — the fallback for parts the catalog doesn't know.

    GET  /api/v1/ai/status                -> is AI identification available?
    POST /api/v1/ai/identify              -> identify a component from a photo
    GET  /api/v1/ai/components            -> everything the AI has identified so far
    GET  /api/v1/ai/components/{id}       -> one AI-identified component

Identification is a Pro feature (it costs real money per call); serving a
cached component is free, because someone already paid for it.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.ai import cache as component_cache
from app.ai import identifier
from app.config import settings
from app.security import require_premium

log = logging.getLogger("ai")

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class AiStatus(BaseModel):
    available: bool
    model: str
    cached_components: int


class Identification(BaseModel):
    identified: bool
    confidence: float
    detected_text: str = ""
    reasoning: str = ""
    advice: str = ""
    #: True when this came from the shared cache (no model call, no cost).
    cached: bool = False
    #: Catalog-shaped entry: pins, per-board wiring with SVG, and code.
    component: Dict[str, Any]


@router.get("/status", response_model=AiStatus)
def status() -> AiStatus:
    try:
        count = len(component_cache.get_cache().all_entries())
    except Exception:  # cache backend unavailable — not fatal
        count = 0
    return AiStatus(
        available=identifier.is_available(),
        model=settings.ai_model if identifier.is_available() else "",
        cached_components=count,
    )


@router.post("/identify", response_model=Identification)
async def identify(
    image: UploadFile = File(..., description="Photo of the component"),
    ocr_text: str = Form(default="", description="Text the on-device OCR read"),
    hint: str = Form(default="", description="Anything the user knows about the part"),
    _: None = Depends(require_premium),
) -> Identification:
    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image upload.")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image too large.")

    # Free path first: if the OCR text matches something the AI already
    # identified for someone else, serve it without calling the model.
    if ocr_text.strip():
        for token in {ocr_text.strip().lower(), *ocr_text.lower().split()}:
            hit = identifier.lookup_cached(token)
            if hit is not None:
                return Identification(
                    identified=True,
                    confidence=0.9,
                    detected_text=ocr_text.strip()[:200],
                    reasoning=f"Matched {hit.get('name')} from a previous "
                    "AI identification.",
                    cached=True,
                    component=hit,
                )

    try:
        result, entry = identifier.identify(
            data, ocr_text=ocr_text, hint=hint
        )
    except identifier.AiUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except identifier.AiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Only cache confident identifications — a guess shouldn't become the
    # answer everyone else gets.
    if result["identified"] and result["confidence"] >= settings.ai_cache_threshold:
        try:
            entry = identifier.remember(entry)
        except Exception as exc:
            log.warning("Could not cache %s: %s", entry.get("id"), exc)

    return Identification(component=entry, **{
        k: v for k, v in result.items() if k != "usage"
    })


@router.get("/components", response_model=List[Dict[str, Any]])
def list_ai_components() -> List[Dict[str, Any]]:
    return component_cache.get_cache().all_entries()


@router.get("/components/{component_id}", response_model=Dict[str, Any])
def get_ai_component(component_id: str) -> Dict[str, Any]:
    entry: Optional[Dict[str, Any]] = component_cache.get_cache().get(
        component_cache.normalise_id(component_id)
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Not identified yet.")
    return entry
