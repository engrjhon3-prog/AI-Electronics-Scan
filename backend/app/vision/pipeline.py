"""The component-recognition pipeline.

Given a raw image, produce a ranked list of `DetectionCandidate`s. The pipeline
combines three signals, each of which contributes candidates:

1. OCR of silk-screen part numbers, matched against the component database.
2. Resistor colour-band decoding (a dedicated OpenCV routine).
3. Coarse shape/colour heuristics as a low-confidence fallback.

This design lets you bolt a trained CNN classifier on later as a fourth signal
without touching the API layer — just append candidates from it.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from app.components import database as db
from app.models import ComponentType, DetectionCandidate, ScanResult
from app.vision import ocr, resistor


def _decode_image(image_bytes: bytes):
    """Decode raw bytes into a BGR numpy array, or None on failure."""
    try:
        import cv2
        import numpy as np
    except Exception:  # noqa: BLE001 - opencv not installed
        return None
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


def _ocr_candidates(bgr, notes: List[str]) -> List[DetectionCandidate]:
    candidates: List[DetectionCandidate] = []
    tokens = ocr.extract_tokens(bgr)
    if tokens:
        notes.append(f"OCR read: {', '.join(tokens[:6])}")
    for token in tokens:
        cid = db.find_by_alias(token)
        if cid:
            comp = db.get_component(cid)
            if comp:
                candidates.append(
                    DetectionCandidate(
                        component_id=comp.id,
                        name=comp.name,
                        type=comp.type,
                        confidence=0.85,
                        detected_value=token,
                        detection_method="ocr",
                        reason=f"Label text '{token}' matched {comp.name}",
                    )
                )
    return candidates


def _resistor_candidate(bgr, notes: List[str]) -> Optional[DetectionCandidate]:
    try:
        reading = resistor.decode(bgr)
    except Exception as exc:  # noqa: BLE001
        notes.append(f"Resistor decode skipped: {exc}")
        return None
    if reading is None:
        return None
    comp = db.get_component("resistor")
    if comp is None:
        return None
    notes.append(f"Colour bands: {' / '.join(reading.bands)}")
    return DetectionCandidate(
        component_id="resistor",
        name=f"Resistor {reading.display}",
        type=ComponentType.resistor,
        confidence=reading.confidence,
        detected_value=reading.display,
        detection_method="color_bands",
        reason=f"Decoded bands {reading.bands} -> {reading.display}",
    )


def _shape_fallback(bgr, notes: List[str]) -> List[DetectionCandidate]:
    """Very coarse: guess IC vs module from aspect ratio / darkness.

    This only fires when nothing better matched, and always at low confidence.
    """
    try:
        import cv2
        import numpy as np
    except Exception:  # noqa: BLE001
        return []
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(gray.mean())
    h, w = gray.shape[:2]
    aspect = w / h if h else 1.0
    guesses: List[DetectionCandidate] = []
    if mean_brightness < 90:
        # Dark, chip-like object -> generic IC hint.
        guesses.append(
            DetectionCandidate(
                component_id="ne555",
                name="Integrated circuit (unrecognised)",
                type=ComponentType.ic,
                confidence=0.2,
                detection_method="shape",
                reason="Dark rectangular object resembling an IC package. "
                "Point the label toward the camera for a better read.",
            )
        )
    if aspect > 2.2:
        notes.append("Elongated object — could be a resistor or axial part.")
    return guesses


def analyze(image_bytes: bytes) -> ScanResult:
    """Run the full pipeline on raw image bytes."""
    notes: List[str] = []
    scan_id = uuid.uuid4().hex

    bgr = _decode_image(image_bytes)
    if bgr is None:
        return ScanResult(
            scan_id=scan_id,
            best_match=None,
            candidates=[],
            notes=["Could not decode the image, or OpenCV is not installed on the server."],
        )

    height, width = bgr.shape[:2]
    candidates: List[DetectionCandidate] = []

    candidates.extend(_ocr_candidates(bgr, notes))

    res_candidate = _resistor_candidate(bgr, notes)
    if res_candidate is not None:
        candidates.append(res_candidate)

    if not candidates:
        candidates.extend(_shape_fallback(bgr, notes))

    # Rank by confidence, de-duplicating by component id (keep the strongest).
    by_id = {}
    for c in sorted(candidates, key=lambda x: x.confidence, reverse=True):
        by_id.setdefault(c.component_id, c)
    ranked = sorted(by_id.values(), key=lambda x: x.confidence, reverse=True)

    if not ranked:
        notes.append(
            "No component recognised. Try better lighting, fill the frame with "
            "the part, and keep any printed label in focus."
        )

    best = ranked[0] if ranked else None
    return ScanResult(
        scan_id=scan_id,
        best_match=best,
        candidates=ranked,
        notes=notes,
        image_width=width,
        image_height=height,
    )
