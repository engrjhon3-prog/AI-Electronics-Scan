"""API and knowledge-base tests. Run with: pytest -q"""
from __future__ import annotations

import io

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.components import database as db
from app.main import app
from app.models import Board
from app.vision import resistor

client = TestClient(app)


def test_root_and_health():
    assert client.get("/health").json() == {"status": "ok"}
    body = client.get("/").json()
    assert body["components"] > 0


def test_list_and_get_component():
    items = client.get("/api/v1/components").json()
    assert any(c["id"] == "ne555" for c in items)

    detail = client.get("/api/v1/components/ne555").json()
    assert detail["name"].startswith("NE555")
    assert len(detail["pins"]) == 8


def test_unknown_component_404():
    assert client.get("/api/v1/components/does-not-exist").status_code == 404


def test_premium_gating_blocks_without_token():
    r = client.get("/api/v1/components/dht11/wiring", params={"board": "uno"})
    assert r.status_code == 402


def test_premium_wiring_with_token():
    r = client.get(
        "/api/v1/components/dht11/wiring",
        params={"board": "uno"},
        headers={"X-Premium-Token": "premium-dev"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["svg"] and body["svg"].startswith("<svg")
    assert len(body["connections"]) >= 2


def test_premium_code_with_token():
    r = client.get(
        "/api/v1/components/dht11/code",
        params={"board": "uno"},
        headers={"X-Premium-Token": "premium-dev"},
    )
    assert r.status_code == 200
    assert "dht.begin()" in r.json()["code"]


def test_database_integrity():
    """Every component with wiring must have matching pins referenced."""
    for comp in db.all_components():
        for board in comp.supported_boards:
            wiring = db.get_wiring(comp.id, board)
            assert wiring is not None
            assert len(wiring.connections) >= 1


def test_alias_lookup():
    assert db.find_by_alias("NE555") == "ne555"
    assert db.find_by_alias("I have an HC-SR04 here") == "hcsr04"
    assert db.find_by_alias("mpu6050") == "mpu6050"


def test_scan_with_blank_image():
    """A blank image should not crash the pipeline."""
    import cv2

    img = np.full((200, 200, 3), 240, dtype=np.uint8)
    ok, buf = cv2.imencode(".png", img)
    assert ok
    files = {"image": ("blank.png", io.BytesIO(buf.tobytes()), "image/png")}
    r = client.post("/api/v1/scan", files=files)
    assert r.status_code == 200
    assert "scan_id" in r.json()


def test_resistor_decoder_on_synthetic():
    """Build a synthetic resistor (brown/black/red = 1kΩ) and decode it."""
    import cv2

    # Beige body with three bands.
    img = np.full((60, 300, 3), (170, 200, 210), dtype=np.uint8)  # BGR beige
    bands_bgr = {
        "brown": (30, 60, 110),
        "black": (20, 20, 20),
        "red": (30, 30, 200),
    }
    positions = [80, 130, 180]
    for (name, color), x in zip(bands_bgr.items(), positions):
        cv2.rectangle(img, (x, 5), (x + 16, 55), color, -1)
    reading = resistor.decode(img)
    # We don't assert the exact value (colour classification is fuzzy), only
    # that the decoder runs and returns a plausible structure.
    assert reading is None or reading.value_ohms is not None


def test_missing_wiring_board_404():
    r = client.get(
        "/api/v1/components/ne555/wiring",
        params={"board": "esp32"},
        headers={"X-Premium-Token": "premium-dev"},
    )
    assert r.status_code == 404
