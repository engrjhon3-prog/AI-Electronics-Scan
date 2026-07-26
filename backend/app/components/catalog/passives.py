"""Passive parts: resistors, capacitors, inductors, crystals, protection."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "resistor",
        "type": "resistor",
        "name": "Resistor",
        "aliases": ["resistor", "ohm", "carbon film resistor"],
        "description": "A passive two-terminal component that limits current. The "
        "colour bands encode its resistance value and tolerance.",
        "package": "Axial THT",
        "tags": ["passive", "beginner"],
        "pins": [
            {"number": 1, "name": "Terminal A", "type": "signal", "description": "Non-polarised"},
            {"number": 2, "name": "Terminal B", "type": "signal", "description": "Non-polarised"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "Signal", "note": "In series with the load"},
                    {"from_pin": "Terminal B", "to_pin": "Load", "note": ""},
                ],
                "notes": ["Resistors are not polarised — orientation does not matter."],
            },
        },
        "code": {},
    },
    {
        "id": "resistor_smd",
        "type": "resistor",
        "name": "SMD Resistor",
        "aliases": ["smd resistor", "chip resistor", "0805 resistor", "0603 resistor"],
        "description": "Surface-mount resistor. The printed code gives the value: "
        "three digits (103 = 10kΩ), four digits (1002 = 10kΩ) or EIA-96.",
        "package": "0402 / 0603 / 0805 / 1206",
        "tags": ["passive", "smd"],
        "pins": [
            {"number": 1, "name": "Pad 1", "type": "signal", "description": "Non-polarised"},
            {"number": 2, "name": "Pad 2", "type": "signal", "description": "Non-polarised"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Pad 1", "to_pin": "Signal", "note": "In series with the load"},
                    {"from_pin": "Pad 2", "to_pin": "Load", "note": ""},
                ],
                "notes": ["'000' or a single 0 marks a zero-ohm jumper."],
            },
        },
        "code": {},
    },
    {
        "id": "potentiometer",
        "type": "resistor",
        "name": "Potentiometer",
        "aliases": ["pot", "potentiometer", "trimpot", "variable resistor", "b10k", "a10k"],
        "description": "A three-terminal variable resistor. The wiper outputs an "
        "analog voltage between the two ends.",
        "package": "THT",
        "tags": ["input", "analog", "beginner"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "One end of the track"},
            {"number": 2, "name": "Wiper", "type": "analog", "description": "Middle terminal, analog out"},
            {"number": 3, "name": "VCC", "type": "power", "description": "Other end of the track"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "Wiper", "to_pin": "A0", "note": "Analog input"},
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                ],
                "notes": [],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "Wiper", "to_pin": "GPIO34", "note": "ADC1 input-only pin"},
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                ],
                "notes": ["Use an ADC1 pin (GPIO32-39). Keep input <= 3.3V."],
            },
        },
        "code": {
            "uno": {
                "title": "Read a potentiometer",
                "libraries": [],
                "code": """const int POT_PIN = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int value = analogRead(POT_PIN);       // 0..1023
  Serial.println(value);
  delay(100);
}
""",
            },
            "esp32": {
                "title": "Read a potentiometer (ESP32)",
                "libraries": [],
                "code": """const int POT_PIN = 34;

void setup() {
  Serial.begin(115200);
}

void loop() {
  int value = analogRead(POT_PIN);       // 0..4095 (12-bit)
  Serial.println(value);
  delay(100);
}
""",
            },
        },
    },
    {
        "id": "capacitor_ceramic",
        "type": "capacitor",
        "name": "Ceramic Capacitor",
        "aliases": ["ceramic capacitor", "mlcc", "decoupling capacitor", "104 capacitor"],
        "description": "Small non-polarised capacitor. The 3-digit code is picofarads "
        "with a multiplier: 104 = 100nF, 103 = 10nF, 224 = 220nF.",
        "package": "THT disc / SMD",
        "tags": ["passive", "beginner"],
        "pins": [
            {"number": 1, "name": "Terminal A", "type": "signal", "description": "Non-polarised"},
            {"number": 2, "name": "Terminal B", "type": "signal", "description": "Non-polarised"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "5V", "note": "Right at the chip's supply pin"},
                    {"from_pin": "Terminal B", "to_pin": "GND", "note": ""},
                ],
                "notes": [
                    "A 100nF decoupling cap belongs next to every IC's power pins.",
                    "Not polarised — either way round is fine.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "capacitor_electrolytic",
        "type": "capacitor",
        "name": "Electrolytic Capacitor",
        "aliases": ["electrolytic capacitor", "electrolytic", "polarised capacitor", "smoothing capacitor"],
        "description": "Polarised bulk capacitor for smoothing power rails. The stripe "
        "marks the negative leg; the positive leg is longer.",
        "package": "Radial THT",
        "tags": ["passive", "power"],
        "pins": [
            {"number": 1, "name": "Anode (+)", "type": "power", "description": "Longer leg, to the positive rail"},
            {"number": 2, "name": "Cathode (-)", "type": "ground", "description": "Stripe side, to ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Anode (+)", "to_pin": "5V", "note": "Across the supply"},
                    {"from_pin": "Cathode (-)", "to_pin": "GND", "note": ""},
                ],
                "notes": [
                    "Reversing the polarity can make it vent or explode.",
                    "Pick a voltage rating at least 1.5x your supply.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "capacitor_tantalum",
        "type": "capacitor",
        "name": "Tantalum Capacitor",
        "aliases": ["tantalum capacitor", "tantalum"],
        "description": "Compact polarised capacitor with low ESR, common on regulator "
        "outputs. The bar marks the POSITIVE terminal (opposite of electrolytics).",
        "package": "SMD A/B/C / THT",
        "tags": ["passive", "power", "smd"],
        "pins": [
            {"number": 1, "name": "Anode (+)", "type": "power", "description": "Bar-marked side"},
            {"number": 2, "name": "Cathode (-)", "type": "ground", "description": "Unmarked side"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Anode (+)", "to_pin": "3V3", "note": "Regulator output"},
                    {"from_pin": "Cathode (-)", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Derate hard: use a part rated at twice your rail voltage."],
            },
        },
        "code": {},
    },
    {
        "id": "supercapacitor",
        "type": "capacitor",
        "name": "Supercapacitor",
        "aliases": ["supercapacitor", "supercap", "ultracapacitor", "gold cap"],
        "description": "Farad-scale capacitor used to ride through power cuts or to "
        "back up an RTC. Low voltage rating (typically 2.7V or 5.5V).",
        "package": "Radial THT",
        "tags": ["passive", "power", "iot"],
        "pins": [
            {"number": 1, "name": "Anode (+)", "type": "power", "description": "Positive terminal"},
            {"number": 2, "name": "Cathode (-)", "type": "ground", "description": "Negative terminal"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Anode (+)", "to_pin": "3V3", "note": "Through a 10Ω inrush resistor"},
                    {"from_pin": "Cathode (-)", "to_pin": "GND", "note": ""},
                ],
                "notes": [
                    "Charging a discharged supercap looks like a short — always add a series resistor.",
                    "Great for finishing a flash write after mains power drops.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "inductor",
        "type": "inductor",
        "name": "Inductor",
        "aliases": ["inductor", "coil", "choke", "power inductor"],
        "description": "Stores energy in a magnetic field; the heart of buck/boost "
        "converters and of noise filters.",
        "package": "Axial / radial / SMD shielded",
        "tags": ["passive", "power"],
        "pins": [
            {"number": 1, "name": "Terminal A", "type": "signal", "description": "Non-polarised"},
            {"number": 2, "name": "Terminal B", "type": "signal", "description": "Non-polarised"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "Switch node", "note": "From the converter IC"},
                    {"from_pin": "Terminal B", "to_pin": "VOUT", "note": "To the output capacitor"},
                ],
                "notes": ["Saturation current matters more than the inductance value."],
            },
        },
        "code": {},
    },
    {
        "id": "crystal_oscillator",
        "type": "inductor",
        "name": "Quartz Crystal",
        "aliases": ["crystal", "quartz crystal", "xtal", "16mhz crystal", "hc-49"],
        "description": "Sets the clock frequency of a microcontroller. Needs two small "
        "load capacitors (typically 22pF) to ground.",
        "package": "HC-49 / SMD 3225",
        "tags": ["passive", "clock"],
        "pins": [
            {"number": 1, "name": "XTAL1", "type": "signal", "description": "To the MCU's XTAL1 pin"},
            {"number": 2, "name": "XTAL2", "type": "signal", "description": "To the MCU's XTAL2 pin"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "XTAL1", "to_pin": "Pin 9 (ATmega328P)", "note": "22pF to GND as well"},
                    {"from_pin": "XTAL2", "to_pin": "Pin 10 (ATmega328P)", "note": "22pF to GND as well"},
                ],
                "notes": ["Keep the traces short — this node is sensitive to stray capacitance."],
            },
        },
        "code": {},
    },
    {
        "id": "fuse",
        "type": "connector",
        "name": "Fuse",
        "aliases": ["fuse", "glass fuse", "blade fuse", "resettable fuse", "polyfuse"],
        "description": "Sacrificial link that opens on overcurrent. Resettable "
        "polyfuses (PPTC) recover once the fault is removed and they cool down.",
        "package": "5x20mm glass / SMD PPTC",
        "tags": ["protection", "power"],
        "pins": [
            {"number": 1, "name": "Terminal A", "type": "power", "description": "Supply side"},
            {"number": 2, "name": "Terminal B", "type": "power", "description": "Load side"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "VIN", "note": "In series with the positive supply"},
                    {"from_pin": "Terminal B", "to_pin": "Load", "note": ""},
                ],
                "notes": ["Rate it just above the normal working current, never far above."],
            },
        },
        "code": {},
    },
    {
        "id": "varistor",
        "type": "diode",
        "name": "MOV / Varistor",
        "aliases": ["varistor", "mov", "metal oxide varistor", "surge suppressor"],
        "description": "Clamps mains-side voltage spikes. Sits across live and neutral "
        "in a surge protector, ahead of the power supply.",
        "package": "Radial disc",
        "tags": ["protection", "mains"],
        "pins": [
            {"number": 1, "name": "Terminal A", "type": "power", "description": "Non-polarised"},
            {"number": 2, "name": "Terminal B", "type": "power", "description": "Non-polarised"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "Live (mains)", "note": "AFTER the fuse"},
                    {"from_pin": "Terminal B", "to_pin": "Neutral (mains)", "note": ""},
                ],
                "notes": [
                    "Mains wiring is lethal — leave it to a qualified person.",
                    "Always pair a MOV with a fuse; a failed MOV can short.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "tvs_diode",
        "type": "diode",
        "name": "TVS Diode",
        "aliases": ["tvs diode", "transient voltage suppressor", "esd diode", "sma6t"],
        "description": "Fast clamp that shunts ESD and inductive spikes to ground. "
        "Standard protection on USB, RS-485 and automotive inputs.",
        "package": "SMA / SOT-23",
        "tags": ["protection", "signal"],
        "pins": [
            {"number": 1, "name": "Line", "type": "signal", "description": "To the protected line"},
            {"number": 2, "name": "GND", "type": "ground", "description": "To ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Line", "to_pin": "Protected input", "note": "As close to the connector as possible"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Pick a stand-off voltage above your signal's normal maximum."],
            },
        },
        "code": {},
    },
    {
        "id": "thermistor_ntc",
        "type": "resistor",
        "name": "NTC Thermistor",
        "aliases": ["thermistor", "ntc", "ntc thermistor", "10k thermistor", "100k thermistor"],
        "description": "A resistor whose value falls as it heats up. With one fixed "
        "resistor it becomes a cheap, fast temperature sensor.",
        "package": "THT bead / probe",
        "tags": ["sensor", "analog", "temperature"],
        "pins": [
            {"number": 1, "name": "Terminal A", "type": "analog", "description": "Non-polarised"},
            {"number": 2, "name": "Terminal B", "type": "analog", "description": "Non-polarised"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "5V", "note": ""},
                    {"from_pin": "Terminal B", "to_pin": "A0", "note": "10kΩ from A0 to GND"},
                ],
                "notes": ["The thermistor and the 10kΩ resistor form a divider into A0."],
            },
        },
        "code": {
            "uno": {
                "title": "Read temperature from a 10k NTC",
                "libraries": [],
                "code": """// 10k NTC (B=3950) in a divider with a 10k resistor to GND.
const int NTC_PIN = A0;
const float SERIES_R = 10000.0;
const float NOMINAL_R = 10000.0;
const float NOMINAL_T = 25.0;
const float BETA = 3950.0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int raw = analogRead(NTC_PIN);
  float resistance = SERIES_R * raw / (1023.0 - raw);
  float steinhart = log(resistance / NOMINAL_R) / BETA;
  steinhart += 1.0 / (NOMINAL_T + 273.15);
  float celsius = 1.0 / steinhart - 273.15;

  Serial.print("Temperature: ");
  Serial.print(celsius, 1);
  Serial.println(" C");
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "photoresistor",
        "type": "resistor",
        "name": "Photoresistor (LDR)",
        "aliases": ["ldr", "photoresistor", "light dependent resistor", "gl5516", "photocell"],
        "description": "Resistance drops as light increases — the cheapest possible "
        "light sensor, perfect for street-lamp style projects.",
        "package": "5mm THT",
        "tags": ["sensor", "analog", "light", "beginner"],
        "pins": [
            {"number": 1, "name": "Terminal A", "type": "analog", "description": "Non-polarised"},
            {"number": 2, "name": "Terminal B", "type": "analog", "description": "Non-polarised"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "5V", "note": ""},
                    {"from_pin": "Terminal B", "to_pin": "A0", "note": "10kΩ from A0 to GND"},
                ],
                "notes": ["Swap the LDR and the resistor to invert the reading."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "3V3", "note": ""},
                    {"from_pin": "Terminal B", "to_pin": "GPIO34", "note": "10kΩ from GPIO34 to GND"},
                ],
                "notes": ["ADC1 pins (32-39) keep working while Wi-Fi is on."],
            },
        },
        "code": {
            "uno": {
                "title": "Night light with an LDR",
                "libraries": [],
                "code": """const int LDR_PIN = A0;
const int LED_PIN = 13;
const int DARK_LEVEL = 400;   // tune for your room

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int light = analogRead(LDR_PIN);
  digitalWrite(LED_PIN, light < DARK_LEVEL ? HIGH : LOW);
  Serial.println(light);
  delay(200);
}
""",
            },
        },
    },
    {
        "id": "transformer",
        "type": "inductor",
        "name": "Transformer",
        "aliases": ["transformer", "step down transformer", "mains transformer"],
        "description": "Two magnetically coupled windings that change AC voltage and "
        "isolate the load from the mains.",
        "package": "EI core / toroidal",
        "tags": ["power", "mains"],
        "pins": [
            {"number": 1, "name": "Primary A", "type": "power", "description": "Mains input"},
            {"number": 2, "name": "Primary B", "type": "power", "description": "Mains input"},
            {"number": 3, "name": "Secondary A", "type": "power", "description": "Low-voltage output"},
            {"number": 4, "name": "Secondary B", "type": "power", "description": "Low-voltage output"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Secondary A", "to_pin": "Bridge rectifier AC1", "note": ""},
                    {"from_pin": "Secondary B", "to_pin": "Bridge rectifier AC2", "note": ""},
                ],
                "notes": [
                    "Never connect a transformer secondary straight to a board — rectify and regulate first.",
                    "The primary side carries mains voltage: fuse it and insulate it properly.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "ferrite_bead",
        "type": "inductor",
        "name": "Ferrite Bead",
        "aliases": ["ferrite bead", "ferrite core", "emi bead"],
        "description": "Looks like an inductor but behaves like a frequency-dependent "
        "resistor — it turns high-frequency noise into heat.",
        "package": "SMD 0805 / clamp-on",
        "tags": ["passive", "emi"],
        "pins": [
            {"number": 1, "name": "Terminal A", "type": "power", "description": "Noisy side"},
            {"number": 2, "name": "Terminal B", "type": "power", "description": "Clean side"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "5V in", "note": ""},
                    {"from_pin": "Terminal B", "to_pin": "Module VCC", "note": "Add 100nF + 10µF after the bead"},
                ],
                "notes": ["Common fix for noisy analog readings on a shared supply."],
            },
        },
        "code": {},
    },
]
