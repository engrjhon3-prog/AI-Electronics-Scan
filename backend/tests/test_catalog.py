"""Integrity checks for the component knowledge base."""
from __future__ import annotations

import pytest

from app.components import database as db
from app.components.catalog import ALL, CATEGORIES
from app.models import Board, ComponentType, PinType


def test_catalog_is_large_and_iot_heavy():
    components = db.all_components()
    assert len(components) >= 150

    tags = {tag for c in components for tag in c.tags}
    assert "iot" in tags

    # The categories a maker expects to browse.
    assert {"wireless", "sensors-environment", "boards", "power"} <= set(CATEGORIES)
    assert db.categories()["wireless"] >= 10


def test_component_ids_are_unique():
    ids = [entry["id"] for entry in ALL]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("entry", ALL, ids=lambda e: e["id"])
def test_entry_is_well_formed(entry):
    assert entry["id"] == entry["id"].lower()
    assert ComponentType(entry["type"])
    assert entry["name"].strip()
    assert len(entry.get("description", "")) > 20
    assert entry.get("pins"), f"{entry['id']} has no pins"

    for alias in entry.get("aliases", []):
        assert alias == alias.lower(), f"{entry['id']}: alias {alias!r} is not lowercase"

    for pin in entry["pins"]:
        assert PinType(pin.get("type", "signal"))
        assert pin["name"].strip()

    for board, wiring in entry.get("wiring", {}).items():
        assert Board(board), f"{entry['id']}: unknown board {board}"
        assert wiring["connections"], f"{entry['id']}/{board} has no connections"
        for conn in wiring["connections"]:
            assert conn["from_pin"] and conn["to_pin"]

    for board, snippet in entry.get("code", {}).items():
        assert Board(board)
        assert snippet["title"].strip()
        assert len(snippet["code"]) > 40


def test_every_component_resolves_through_the_public_api():
    for component in db.all_components():
        assert db.get_component(component.id) is not None
        assert component.category, f"{component.id} has no category"
        for board in component.supported_boards:
            assert db.get_wiring(component.id, board) is not None


def test_alias_lookup_finds_common_iot_parts():
    assert db.find_by_alias("this is an esp32 devkit board") == "esp32_devkit"
    assert db.find_by_alias("nrf24l01+ module") == "nrf24l01"
    assert db.find_by_alias("neo-6m gps") == "neo6m_gps"
    assert db.find_by_alias("ds18b20") == "ds18b20"


def test_code_snippets_exist_for_the_iot_headliners():
    for component_id in ["esp32_devkit", "lora_sx1278", "dht22", "rc522"]:
        component = db.get_component(component_id)
        assert component is not None
        snippets = [
            db.get_code(component_id, board) for board in component.supported_boards
        ]
        assert any(s is not None for s in snippets), f"{component_id} has no code"
