"""Optical character recognition for component labels.

Many ICs, sensors, and modules are silk-screened with a part number
(e.g. "NE555", "MPU6050", "HC-SR04"). Reading that text is the single most
reliable way to identify them. We use Tesseract when it is available and fall
back gracefully when it is not, so the service still runs on a minimal box.
"""
from __future__ import annotations

import re
from typing import List

_TESSERACT_AVAILABLE = False
try:  # pragma: no cover - depends on runtime environment
    import pytesseract  # type: ignore

    _TESSERACT_AVAILABLE = True
except Exception:  # noqa: BLE001
    pytesseract = None  # type: ignore


def is_available() -> bool:
    return _TESSERACT_AVAILABLE


def _preprocess(bgr):
    """Boost contrast and binarise to help Tesseract read silk-screen text."""
    import cv2

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    # Adaptive threshold copes with uneven lighting across a chip surface.
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )
    return thresh


def extract_tokens(bgr) -> List[str]:
    """Return candidate part-number tokens found in the image, upper-cased.

    Empty list if OCR is unavailable or nothing legible is found.
    """
    if not _TESSERACT_AVAILABLE:
        return []
    try:  # pragma: no cover - depends on runtime environment
        import cv2  # noqa: F401

        processed = _preprocess(bgr)
        # PSM 11: sparse text. Good for scattered silk-screen markings.
        raw = pytesseract.image_to_string(processed, config="--psm 11")
    except Exception:  # noqa: BLE001
        return []

    tokens: List[str] = []
    for match in re.findall(r"[A-Za-z0-9\-]{3,}", raw):
        cleaned = match.strip("-").upper()
        # Keep tokens that look like part numbers (contain a digit or a hyphen).
        if any(ch.isdigit() for ch in cleaned) or "-" in cleaned:
            tokens.append(cleaned)
    # De-duplicate, preserve order.
    seen = set()
    unique = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique
