"""Pydantic data models shared across the API.

These define the JSON contract between the Python backend and the Flutter
frontend. Keep field names in sync with `frontend/lib/models/`.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    resistor = "resistor"
    capacitor = "capacitor"
    led = "led"
    diode = "diode"
    transistor = "transistor"
    ic = "ic"
    sensor = "sensor"
    module = "module"
    actuator = "actuator"
    unknown = "unknown"


class PinType(str, Enum):
    power = "power"
    ground = "ground"
    digital = "digital"
    analog = "analog"
    pwm = "pwm"
    i2c = "i2c"
    spi = "spi"
    uart = "uart"
    signal = "signal"
    nc = "nc"  # not connected


class Board(str, Enum):
    uno = "uno"
    nano = "nano"
    esp32 = "esp32"
    esp8266 = "esp8266"


class Pin(BaseModel):
    number: int
    name: str
    type: PinType = PinType.signal
    description: str = ""


class Connection(BaseModel):
    """A single wire in a wiring diagram."""
    from_pin: str = Field(..., description="Component pin name")
    to_pin: str = Field(..., description="Board pin / net name")
    note: str = ""


class WiringDiagram(BaseModel):
    component_id: str
    board: Board
    connections: List[Connection]
    notes: List[str] = []
    # Inline SVG the frontend can render directly.
    svg: Optional[str] = None


class CodeSnippet(BaseModel):
    component_id: str
    board: Board
    language: str = "cpp"
    title: str
    description: str = ""
    libraries: List[str] = []
    code: str


class Component(BaseModel):
    id: str
    type: ComponentType
    name: str
    aliases: List[str] = []
    description: str = ""
    package: str = ""
    datasheet_url: Optional[str] = None
    pins: List[Pin] = []
    # Boards for which we can generate wiring + code.
    supported_boards: List[Board] = []
    tags: List[str] = []


class DetectionCandidate(BaseModel):
    component_id: str
    name: str
    type: ComponentType
    confidence: float
    detected_value: Optional[str] = None
    detection_method: str = ""
    reason: str = ""


class ScanResult(BaseModel):
    scan_id: str
    best_match: Optional[DetectionCandidate] = None
    candidates: List[DetectionCandidate] = []
    # Free-form notes about what the vision pipeline saw.
    notes: List[str] = []
    image_width: int = 0
    image_height: int = 0
