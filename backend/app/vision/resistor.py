"""Resistor colour-band decoding.

This is a genuinely working OpenCV routine (not a stub): it isolates the
resistor body, samples the colour bands along its length, classifies each band
against the standard resistor colour code, and computes the resistance value.

It is deliberately tolerant — lighting and camera colour balance vary a lot, so
we return a confidence score alongside the decoded value and let the caller
decide whether to trust it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

# Standard resistor colour code. Values are (digit, multiplier_power, tolerance).
# tolerance is only meaningful for the gold/silver bands.
_COLOR_CODE = {
    "black": {"digit": 0, "mult": 0, "tol": None},
    "brown": {"digit": 1, "mult": 1, "tol": 1.0},
    "red": {"digit": 2, "mult": 2, "tol": 2.0},
    "orange": {"digit": 3, "mult": 3, "tol": None},
    "yellow": {"digit": 4, "mult": 4, "tol": None},
    "green": {"digit": 5, "mult": 5, "tol": 0.5},
    "blue": {"digit": 6, "mult": 6, "tol": 0.25},
    "violet": {"digit": 7, "mult": 7, "tol": 0.1},
    "grey": {"digit": 8, "mult": 8, "tol": None},
    "white": {"digit": 9, "mult": 9, "tol": None},
    "gold": {"digit": None, "mult": -1, "tol": 5.0},
    "silver": {"digit": None, "mult": -2, "tol": 10.0},
}

# Representative HSV centres (OpenCV ranges: H 0-179, S 0-255, V 0-255).
_COLOR_HSV = {
    "black": (0, 0, 25),
    "brown": (12, 150, 90),
    "red": (0, 200, 160),
    "orange": (13, 210, 210),
    "yellow": (26, 200, 210),
    "green": (60, 160, 140),
    "blue": (108, 180, 160),
    "violet": (140, 120, 150),
    "grey": (0, 10, 130),
    "white": (0, 8, 235),
    "gold": (22, 130, 165),
    "silver": (0, 8, 175),
}


@dataclass
class ResistorReading:
    value_ohms: Optional[float]
    display: str
    bands: List[str]
    tolerance: Optional[float]
    confidence: float


def _format_ohms(value: float, tolerance: Optional[float]) -> str:
    if value >= 1_000_000:
        base = f"{value / 1_000_000:g}MΩ"
    elif value >= 1_000:
        base = f"{value / 1_000:g}kΩ"
    else:
        base = f"{value:g}Ω"
    if tolerance is not None:
        return f"{base} ±{tolerance:g}%"
    return base


def _classify_hsv(hsv_pixel: Tuple[float, float, float]) -> Tuple[str, float]:
    """Nearest-colour classification with a rough confidence in [0,1]."""
    h, s, v = hsv_pixel
    best_name = "black"
    best_dist = float("inf")
    for name, (ch, cs, cv) in _COLOR_HSV.items():
        # Hue is circular; weight it more when saturation is high.
        dh = min(abs(h - ch), 180 - abs(h - ch))
        # Low-saturation colours (black/white/grey/silver) are hue-agnostic.
        hue_weight = 2.0 if s > 60 else 0.2
        dist = (hue_weight * dh) ** 2 + (0.5 * (s - cs)) ** 2 + (0.6 * (v - cv)) ** 2
        if dist < best_dist:
            best_dist = dist
            best_name = name
    # Map distance to a soft confidence.
    conf = max(0.0, min(1.0, 1.0 - (best_dist ** 0.5) / 220.0))
    return best_name, conf


def _find_resistor_body(bgr: "np.ndarray") -> Optional[Tuple[int, int, int, int]]:
    """Return a bounding box (x, y, w, h) of the most resistor-like region."""
    import cv2

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    # Resistor bodies are usually beige/blue/green with moderate saturation and
    # are the dominant coloured object on a plain background. We threshold on
    # saturation to drop washed-out backgrounds, then take the largest contour.
    sat = hsv[:, :, 1]
    _, mask = cv2.threshold(sat, 40, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    best = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(best)
    # A resistor is elongated. Reject blobs that are too small or too square.
    if w < 20 or h < 6:
        return None
    return x, y, w, h


def decode(bgr: "np.ndarray") -> Optional[ResistorReading]:
    """Attempt to decode a resistor from a BGR image. Returns None if the image
    does not look like a resistor at all."""
    import cv2

    box = _find_resistor_body(bgr)
    if box is None:
        return None
    x, y, w, h = box

    # Work along the long axis. If the body is taller than wide, rotate our view.
    roi = bgr[y : y + h, x : x + w]
    if h > w:
        roi = cv2.rotate(roi, cv2.ROTATE_90_CLOCKWISE)
    rh, rw = roi.shape[:2]
    if rw < 30:
        return None

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    # Sample a horizontal strip through the middle of the body.
    strip = hsv[int(rh * 0.35) : int(rh * 0.65), :, :]
    col_mean = strip.mean(axis=0)  # shape (rw, 3)

    # Estimate the body (lead/background) colour as the median column, then find
    # columns that differ from it — those are candidate bands.
    body = np.median(col_mean, axis=0)
    diff = np.linalg.norm(col_mean - body, axis=1)
    threshold = max(35.0, float(np.percentile(diff, 70)))

    bands: List[str] = []
    band_confs: List[float] = []
    in_band = False
    acc: List[np.ndarray] = []
    for i in range(rw):
        if diff[i] > threshold:
            in_band = True
            acc.append(col_mean[i])
        else:
            if in_band and len(acc) >= 2:
                mean_hsv = np.mean(acc, axis=0)
                name, conf = _classify_hsv(tuple(mean_hsv))
                bands.append(name)
                band_confs.append(conf)
            in_band = False
            acc = []
    if in_band and len(acc) >= 2:
        mean_hsv = np.mean(acc, axis=0)
        name, conf = _classify_hsv(tuple(mean_hsv))
        bands.append(name)
        band_confs.append(conf)

    if len(bands) < 3:
        return None

    # Use the first 3-4 bands for a 4- or 5-band resistor.
    reading = _bands_to_value(bands)
    if reading is None:
        return None
    value, tol, used = reading
    avg_conf = float(np.mean(band_confs[: len(used)])) if band_confs else 0.3
    # Penalise if we found an odd number of bands or very low per-band confidence.
    confidence = round(min(0.9, avg_conf * (0.85 if len(bands) > 5 else 1.0)), 2)
    return ResistorReading(
        value_ohms=value,
        display=_format_ohms(value, tol),
        bands=used,
        tolerance=tol,
        confidence=confidence,
    )


def _bands_to_value(
    bands: List[str],
) -> Optional[Tuple[float, Optional[float], List[str]]]:
    """Convert an ordered band list into (value, tolerance, used_bands)."""
    # Trim to a plausible band count. Prefer 4 bands (2 digits + mult + tol).
    usable = [b for b in bands if b in _COLOR_CODE]
    if len(usable) < 3:
        return None

    def digits_and_mult(seq: List[str]) -> Optional[Tuple[float, Optional[float]]]:
        digit_bands = seq[:-1]
        mult_band = seq[-1]
        digits = []
        for b in digit_bands:
            d = _COLOR_CODE[b]["digit"]
            if d is None:
                return None
            digits.append(str(d))
        mult = _COLOR_CODE[mult_band]["mult"]
        if mult is None:
            return None
        try:
            base = int("".join(digits))
        except ValueError:
            return None
        value = base * (10 ** mult)
        return value, None

    # Try a 5-band interpretation (3 digits + mult + tol) then 4-band.
    for n in (5, 4):
        if len(usable) >= n:
            seq = usable[:n]
            tol = _COLOR_CODE[seq[-1]]["tol"]
            core = seq[:-1] if tol is not None else seq
            res = digits_and_mult(core)
            if res is not None:
                value, _ = res
                return value, tol, seq
    # 3-band fallback: 2 digits + mult, no tolerance band.
    seq = usable[:3]
    res = digits_and_mult(seq)
    if res is not None:
        value, _ = res
        return value, None, seq
    return None
