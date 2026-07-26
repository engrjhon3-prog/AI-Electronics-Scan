"""AI identification tests — schema conversion, caching, gating, error paths.

The model itself is stubbed: these check the contract around it (what we send,
what we accept back, what gets cached, who is allowed to ask).
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.ai import cache as component_cache
from app.ai import identifier
from app.ai.schema import IDENTIFY_SCHEMA, to_catalog_entry
from app.config import settings
from app.main import app

client = TestClient(app)

PREMIUM = {"X-Premium-Token": "premium-dev"}
IMAGE = b"\xff\xd8\xff" + b"fake jpeg bytes"

MODEL_REPLY = {
    "identified": True,
    "confidence": 0.88,
    "detected_text": "BME680",
    "reasoning": "The silkscreen reads BME680 on a 4-pin I2C breakout.",
    "advice": "",
    "component": {
        "id": "BME680",
        "type": "sensor",
        "name": "BME680 Environmental Sensor",
        "aliases": ["bme680", "gy-bme680", "ai"],
        "description": "Temperature, humidity, pressure and gas resistance over I2C.",
        "package": "Module",
        "datasheet_url": "",
        "tags": ["sensor", "i2c", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "Clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "Data"},
        ],
        "wiring": [
            {
                "board": "esp32",
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                ],
                "notes": ["Address 0x76 or 0x77."],
            },
            {
                "board": "pico",  # not a board we support — must be dropped
                "connections": [{"from_pin": "VCC", "to_pin": "3V3", "note": ""}],
                "notes": [],
            },
        ],
        "code": [
            {
                "board": "esp32",
                "title": "Read the BME680",
                "description": "",
                "libraries": ["Adafruit BME680 Library"],
                "code": "#include <Adafruit_BME680.h>\nvoid setup() {}\nvoid loop() {}\n",
            }
        ],
    },
}


def _stub_model(monkeypatch, reply: dict, *, calls: list | None = None):
    """Replace the Claude client with one that returns `reply`."""

    class _Stream:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get_final_message(self):
            return SimpleNamespace(
                stop_reason="end_turn",
                content=[SimpleNamespace(type="text", text=json.dumps(reply))],
                usage=SimpleNamespace(
                    input_tokens=2100, output_tokens=1400, cache_read_input_tokens=0
                ),
            )

    class _Messages:
        def stream(self, **kwargs):
            if calls is not None:
                calls.append(kwargs)
            return _Stream()

    monkeypatch.setattr(identifier, "_client", lambda: SimpleNamespace(messages=_Messages()))


@pytest.fixture(autouse=True)
def fresh_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ai_cache_path", str(tmp_path / "ai.json"))
    component_cache.reset_cache()
    yield
    component_cache.reset_cache()


# ------------------------------------------------------------------- schema
def test_schema_is_a_valid_structured_output_schema():
    # Structured outputs require every object to close itself off.
    def check(node):
        if node.get("type") == "object":
            assert node["additionalProperties"] is False
            assert set(node["required"]) == set(node["properties"])
            for child in node["properties"].values():
                check(child)
        if node.get("type") == "array":
            check(node["items"])

    check(IDENTIFY_SCHEMA)


def test_conversion_produces_a_catalog_shaped_entry():
    entry = to_catalog_entry(MODEL_REPLY["component"])
    assert entry["wiring"]["esp32"]["connections"][0]["to_pin"] == "3V3"
    assert entry["code"]["esp32"]["libraries"] == ["Adafruit BME680 Library"]
    assert entry["datasheet_url"] is None  # empty string means "unknown"
    assert "ai" not in entry["aliases"]  # two-character aliases are dropped
    assert entry["category"] == "ai-identified"


# ------------------------------------------------------------------ gating
def test_identification_requires_pro():
    res = client.post("/api/v1/ai/identify", files={"image": ("c.jpg", IMAGE, "image/jpeg")})
    assert res.status_code == 402


def test_status_reports_availability():
    body = client.get("/api/v1/ai/status").json()
    assert body["available"] is False  # no ANTHROPIC_API_KEY in tests
    assert body["cached_components"] == 0


def test_identify_without_a_key_is_a_clear_503():
    res = client.post(
        "/api/v1/ai/identify",
        files={"image": ("c.jpg", IMAGE, "image/jpeg")},
        headers=PREMIUM,
    )
    assert res.status_code == 503
    assert "ANTHROPIC_API_KEY" in res.json()["detail"]


# ------------------------------------------------------------- happy path
def test_identifies_a_component_the_catalog_has_never_heard_of(monkeypatch):
    calls: list = []
    _stub_model(monkeypatch, MODEL_REPLY, calls=calls)

    res = client.post(
        "/api/v1/ai/identify",
        files={"image": ("c.jpg", IMAGE, "image/jpeg")},
        data={"ocr_text": "BME680"},
        headers=PREMIUM,
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["identified"] is True
    assert body["cached"] is False

    component = body["component"]
    assert component["id"] == "bme680"  # normalised
    assert len(component["pins"]) == 4
    # Unsupported board dropped; supported one keeps a rendered diagram.
    assert set(component["wiring"]) == {"esp32"}
    assert component["wiring"]["esp32"]["svg"].startswith("<svg")
    assert component["code"]["esp32"]["code"].startswith("#include")
    assert component["source"] == "ai"

    # The photo and the OCR text both reached the model.
    content = calls[0]["messages"][0]["content"]
    assert content[0]["type"] == "image"
    assert "BME680" in content[1]["text"]
    assert calls[0]["output_config"]["format"]["type"] == "json_schema"


def test_a_second_scan_of_the_same_part_is_served_from_cache(monkeypatch):
    calls: list = []
    _stub_model(monkeypatch, MODEL_REPLY, calls=calls)

    for _ in range(2):
        res = client.post(
            "/api/v1/ai/identify",
            files={"image": ("c.jpg", IMAGE, "image/jpeg")},
            data={"ocr_text": "BME680"},
            headers=PREMIUM,
        )
        assert res.status_code == 200

    assert len(calls) == 1, "the model should only be paid for once"
    assert res.json()["cached"] is True

    listed = client.get("/api/v1/ai/components").json()
    assert [c["id"] for c in listed] == ["bme680"]
    assert client.get("/api/v1/ai/components/BME680").json()["name"].startswith("BME680")


def test_low_confidence_guesses_are_not_cached(monkeypatch):
    unsure = json.loads(json.dumps(MODEL_REPLY))
    unsure["identified"] = False
    unsure["confidence"] = 0.2
    unsure["advice"] = "Photograph the printed side of the chip in focus."
    _stub_model(monkeypatch, unsure)

    body = client.post(
        "/api/v1/ai/identify",
        files={"image": ("c.jpg", IMAGE, "image/jpeg")},
        headers=PREMIUM,
    ).json()
    assert body["identified"] is False
    assert body["advice"]
    assert client.get("/api/v1/ai/components").json() == []


def test_unknown_component_lookup_is_404():
    assert client.get("/api/v1/ai/components/nope").status_code == 404


# ------------------------------------------------------------- error paths
def test_refusal_becomes_a_readable_error(monkeypatch):
    class _Stream:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get_final_message(self):
            return SimpleNamespace(
                stop_reason="refusal",
                content=[],
                usage=SimpleNamespace(input_tokens=10, output_tokens=0),
            )

    monkeypatch.setattr(
        identifier,
        "_client",
        lambda: SimpleNamespace(messages=SimpleNamespace(stream=lambda **k: _Stream())),
    )
    res = client.post(
        "/api/v1/ai/identify",
        files={"image": ("c.jpg", IMAGE, "image/jpeg")},
        headers=PREMIUM,
    )
    assert res.status_code == 502
    assert "declined" in res.json()["detail"]


def test_empty_upload_is_rejected():
    res = client.post(
        "/api/v1/ai/identify",
        files={"image": ("c.jpg", b"", "image/jpeg")},
        headers=PREMIUM,
    )
    assert res.status_code == 400


def test_cache_id_normalisation():
    assert component_cache.normalise_id("  BME-680 ") == "bme_680"
    assert component_cache.normalise_id("TB6612FNG") == "tb6612fng"
