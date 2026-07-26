"""Discrete semiconductors: LEDs, diodes, transistors, MOSFETs, optocouplers."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "led_5mm",
        "type": "led",
        "name": "5mm LED",
        "aliases": ["led", "light emitting diode"],
        "description": "A standard 5mm through-hole LED. Always drive it through a "
        "current-limiting resistor (220-330Ω for 5V logic).",
        "package": "5mm THT",
        "tags": ["output", "beginner"],
        "pins": [
            {"number": 1, "name": "Anode (+)", "type": "signal", "description": "Longer leg, connects toward positive"},
            {"number": 2, "name": "Cathode (-)", "type": "ground", "description": "Shorter leg / flat side, to ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Anode (+)", "to_pin": "D13", "note": "Through a 220Ω resistor"},
                    {"from_pin": "Cathode (-)", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Never connect an LED directly without a series resistor."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "Anode (+)", "to_pin": "GPIO2", "note": "Through a 220Ω resistor"},
                    {"from_pin": "Cathode (-)", "to_pin": "GND", "note": ""},
                ],
                "notes": ["ESP32 GPIOs are 3.3V; a 220Ω resistor is fine."],
            },
        },
        "code": {
            "uno": {
                "title": "Blink an LED",
                "libraries": [],
                "code": """const int LED_PIN = 13;

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  delay(500);
}
""",
            },
            "esp32": {
                "title": "Blink an LED (ESP32)",
                "libraries": [],
                "code": """const int LED_PIN = 2;

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "rgb_led",
        "type": "led",
        "name": "RGB LED (common cathode)",
        "aliases": ["rgb led", "tricolor led", "colour led"],
        "description": "Three LEDs in one package. Mix colours with PWM on the red, "
        "green and blue legs — each needs its own resistor.",
        "package": "5mm THT, 4 leads",
        "tags": ["output", "pwm", "beginner"],
        "pins": [
            {"number": 1, "name": "Red", "type": "pwm", "description": "Red anode"},
            {"number": 2, "name": "Cathode (-)", "type": "ground", "description": "Longest leg, common"},
            {"number": 3, "name": "Green", "type": "pwm", "description": "Green anode"},
            {"number": 4, "name": "Blue", "type": "pwm", "description": "Blue anode"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Red", "to_pin": "D9", "note": "Through 220Ω"},
                    {"from_pin": "Green", "to_pin": "D10", "note": "Through 220Ω"},
                    {"from_pin": "Blue", "to_pin": "D11", "note": "Through 220Ω"},
                    {"from_pin": "Cathode (-)", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Common-anode parts wire the long leg to 5V and invert the PWM."],
            },
        },
        "code": {
            "uno": {
                "title": "Fade an RGB LED through the rainbow",
                "libraries": [],
                "code": """const int R_PIN = 9, G_PIN = 10, B_PIN = 11;

void setColor(int r, int g, int b) {
  analogWrite(R_PIN, r);
  analogWrite(G_PIN, g);
  analogWrite(B_PIN, b);
}

void setup() {
  pinMode(R_PIN, OUTPUT);
  pinMode(G_PIN, OUTPUT);
  pinMode(B_PIN, OUTPUT);
}

void loop() {
  for (int hue = 0; hue < 256; hue++) {
    setColor(hue, 255 - hue, (hue * 2) % 256);
    delay(20);
  }
}
""",
            },
        },
    },
    {
        "id": "ws2812b",
        "type": "led",
        "name": "WS2812B Addressable LED (NeoPixel)",
        "aliases": ["ws2812", "ws2812b", "neopixel", "addressable led", "led strip"],
        "description": "RGB LED with a built-in controller: one data line drives a "
        "whole chain, each pixel individually addressable.",
        "package": "5050 SMD / strip / ring",
        "tags": ["output", "iot", "rgb"],
        "datasheet_url": "https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf",
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V (3.7-5.3V)"},
            {"number": 2, "name": "DIN", "type": "digital", "description": "Data in from the MCU"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "DOUT", "type": "digital", "description": "Data out to the next pixel"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "Use an external 5V supply past ~8 pixels"},
                    {"from_pin": "DIN", "to_pin": "D6", "note": "330Ω in series protects the first pixel"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Share ground with the supply"},
                ],
                "notes": ["Add 1000µF across 5V/GND at the strip's input."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": "External supply for long strips"},
                    {"from_pin": "DIN", "to_pin": "GPIO5", "note": "3.3V data usually works; a level shifter is safer"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["A 74AHCT125 buffer fixes flaky first pixels on 3.3V boards."],
            },
        },
        "code": {
            "uno": {
                "title": "Rainbow chase on a NeoPixel strip",
                "libraries": ["Adafruit_NeoPixel"],
                "code": """#include <Adafruit_NeoPixel.h>

const int LED_PIN = 6;
const int NUM_PIXELS = 16;

Adafruit_NeoPixel strip(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  strip.begin();
  strip.setBrightness(60);
  strip.show();
}

void loop() {
  for (long hue = 0; hue < 65536; hue += 256) {
    strip.rainbow(hue);
    strip.show();
    delay(20);
  }
}
""",
            },
        },
    },
    {
        "id": "ir_led",
        "type": "led",
        "name": "Infrared LED",
        "aliases": ["ir led", "infrared led", "ir emitter"],
        "description": "Invisible 940nm emitter used for remote controls and for the "
        "transmit half of IR obstacle/line sensors.",
        "package": "5mm THT",
        "tags": ["output", "ir"],
        "pins": [
            {"number": 1, "name": "Anode (+)", "type": "signal", "description": "Longer leg"},
            {"number": 2, "name": "Cathode (-)", "type": "ground", "description": "Flat side"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Anode (+)", "to_pin": "D3", "note": "Through 100Ω; D3 carries the 38kHz carrier"},
                    {"from_pin": "Cathode (-)", "to_pin": "GND", "note": ""},
                ],
                "notes": ["IRremote drives pin 3 on an Uno — the timer is fixed."],
            },
        },
        "code": {
            "uno": {
                "title": "Send an NEC remote code",
                "libraries": ["IRremote"],
                "code": """#include <IRremote.hpp>

const int IR_SEND_PIN = 3;

void setup() {
  IrSender.begin(IR_SEND_PIN);
}

void loop() {
  // Address 0x00, command 0x45 (power on many remotes), no repeats.
  IrSender.sendNEC(0x00, 0x45, 0);
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "laser_module",
        "type": "led",
        "name": "Laser Diode Module (KY-008)",
        "aliases": ["laser module", "ky-008", "laser diode", "650nm laser"],
        "description": "A 650nm red laser dot module with the driver resistor already "
        "fitted — drive it straight from a GPIO pin.",
        "package": "6mm module",
        "tags": ["output", "beginner"],
        "pins": [
            {"number": 1, "name": "SIG", "type": "digital", "description": "HIGH turns the laser on"},
            {"number": 2, "name": "VCC", "type": "power", "description": "5V"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "SIG", "to_pin": "D8", "note": ""},
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Never look into the beam, and don't aim it at anyone."],
            },
        },
        "code": {
            "uno": {
                "title": "Laser tripwire with an LDR",
                "libraries": [],
                "code": """const int LASER_PIN = 8;
const int LDR_PIN = A0;
const int BEAM_LEVEL = 300;   // reading with the beam landing on the LDR

void setup() {
  pinMode(LASER_PIN, OUTPUT);
  digitalWrite(LASER_PIN, HIGH);
  Serial.begin(9600);
}

void loop() {
  if (analogRead(LDR_PIN) < BEAM_LEVEL) {
    Serial.println("Beam broken!");
  }
  delay(50);
}
""",
            },
        },
    },
    {
        "id": "diode_1n4007",
        "type": "diode",
        "name": "1N4007 Rectifier Diode",
        "aliases": ["1n4007", "1n400", "rectifier diode", "power diode"],
        "description": "1A / 1000V general-purpose rectifier. The classic flyback diode "
        "across relay and motor coils.",
        "package": "DO-41",
        "tags": ["power", "protection", "beginner"],
        "pins": [
            {"number": 1, "name": "Anode", "type": "signal", "description": "Current flows in here"},
            {"number": 2, "name": "Cathode", "type": "signal", "description": "Banded end"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Cathode", "to_pin": "Coil +", "note": "Band toward the positive supply"},
                    {"from_pin": "Anode", "to_pin": "Coil -", "note": "Transistor / driver side"},
                ],
                "notes": ["Reverse-biased across the coil, it absorbs the switch-off spike."],
            },
        },
        "code": {},
    },
    {
        "id": "diode_1n4148",
        "type": "diode",
        "name": "1N4148 Signal Diode",
        "aliases": ["1n4148", "signal diode", "switching diode"],
        "description": "Fast small-signal diode: logic steering, keyboard matrices and "
        "clamping, up to 200mA.",
        "package": "DO-35",
        "tags": ["signal", "beginner"],
        "pins": [
            {"number": 1, "name": "Anode", "type": "signal", "description": "Unbanded end"},
            {"number": 2, "name": "Cathode", "type": "signal", "description": "Banded end"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Anode", "to_pin": "Signal", "note": "Blocks reverse current"},
                    {"from_pin": "Cathode", "to_pin": "Load", "note": ""},
                ],
                "notes": ["Forward drop is about 0.7V."],
            },
        },
        "code": {},
    },
    {
        "id": "diode_schottky",
        "type": "diode",
        "name": "Schottky Diode (1N5819)",
        "aliases": ["schottky", "1n5819", "schottky diode", "sr360", "ss34"],
        "description": "Low forward drop (~0.3V) and very fast recovery — used for "
        "reverse-polarity protection, OR-ing supplies and switching converters.",
        "package": "DO-41 / SMA",
        "tags": ["power", "protection"],
        "pins": [
            {"number": 1, "name": "Anode", "type": "power", "description": "Supply side"},
            {"number": 2, "name": "Cathode", "type": "power", "description": "Banded end, load side"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Anode", "to_pin": "Battery +", "note": ""},
                    {"from_pin": "Cathode", "to_pin": "VIN", "note": "Blocks reverse polarity"},
                ],
                "notes": ["Costs you ~0.3V of headroom — fine on 5V, tight on 3.3V."],
            },
        },
        "code": {},
    },
    {
        "id": "zener_diode",
        "type": "diode",
        "name": "Zener Diode",
        "aliases": ["zener", "zener diode", "1n4733", "5v1 zener"],
        "description": "Conducts backwards at a precise voltage — a simple voltage "
        "reference or an over-voltage clamp on an input pin.",
        "package": "DO-35 / DO-41",
        "tags": ["protection", "analog"],
        "pins": [
            {"number": 1, "name": "Anode", "type": "signal", "description": "To ground in a clamp"},
            {"number": 2, "name": "Cathode", "type": "signal", "description": "Banded end, to the protected node"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Cathode", "to_pin": "A0", "note": "Clamps the input at the Zener voltage"},
                    {"from_pin": "Anode", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Always feed a Zener through a series resistor to limit current."],
            },
        },
        "code": {},
    },
    {
        "id": "bridge_rectifier",
        "type": "diode",
        "name": "Bridge Rectifier",
        "aliases": ["bridge rectifier", "kbp307", "w10", "full wave rectifier", "diode bridge"],
        "description": "Four diodes in one package that turn AC into pulsating DC. "
        "Smooth the output with a large electrolytic capacitor.",
        "package": "KBP / WOB",
        "tags": ["power"],
        "pins": [
            {"number": 1, "name": "AC1", "type": "power", "description": "AC input"},
            {"number": 2, "name": "AC2", "type": "power", "description": "AC input"},
            {"number": 3, "name": "V+", "type": "power", "description": "Positive DC output"},
            {"number": 4, "name": "V-", "type": "ground", "description": "Negative DC output"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "AC1", "to_pin": "Transformer secondary", "note": ""},
                    {"from_pin": "AC2", "to_pin": "Transformer secondary", "note": ""},
                    {"from_pin": "V+", "to_pin": "Regulator IN", "note": "1000µF to GND here"},
                    {"from_pin": "V-", "to_pin": "GND", "note": ""},
                ],
                "notes": ["DC output peaks at about 1.4x the AC RMS voltage, minus 1.4V."],
            },
        },
        "code": {},
    },
    {
        "id": "transistor_2n2222",
        "type": "transistor",
        "name": "2N2222 NPN Transistor",
        "aliases": ["2n2222", "npn transistor", "p2n2222", "bc547", "s8050"],
        "description": "General-purpose NPN switch/amplifier good for up to ~600mA — "
        "the standard way to let a 20mA GPIO pin drive a relay or a small motor.",
        "package": "TO-92",
        "tags": ["switch", "beginner"],
        "pins": [
            {"number": 1, "name": "Emitter", "type": "ground", "description": "To ground (low-side switch)"},
            {"number": 2, "name": "Base", "type": "signal", "description": "Control, through a 1kΩ resistor"},
            {"number": 3, "name": "Collector", "type": "signal", "description": "To the load"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Base", "to_pin": "D9", "note": "Through a 1kΩ resistor"},
                    {"from_pin": "Collector", "to_pin": "Load -", "note": "Load + goes to 5V/12V"},
                    {"from_pin": "Emitter", "to_pin": "GND", "note": "Common ground with the supply"},
                ],
                "notes": [
                    "Pinout differs between makers — check the datasheet for your part.",
                    "Add a flyback diode across any inductive load.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Switch a load with an NPN transistor",
                "libraries": [],
                "code": """const int BASE_PIN = 9;

void setup() {
  pinMode(BASE_PIN, OUTPUT);
}

void loop() {
  digitalWrite(BASE_PIN, HIGH);   // load on
  delay(2000);
  digitalWrite(BASE_PIN, LOW);    // load off
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "transistor_tip120",
        "type": "transistor",
        "name": "TIP120 Darlington Transistor",
        "aliases": ["tip120", "darlington", "tip122", "power transistor"],
        "description": "Darlington pair rated 5A: enough for 12V LED strips, solenoids "
        "and small DC motors, still driven straight from a GPIO pin.",
        "package": "TO-220",
        "tags": ["switch", "power"],
        "pins": [
            {"number": 1, "name": "Base", "type": "signal", "description": "Control, through 1kΩ"},
            {"number": 2, "name": "Collector", "type": "signal", "description": "To the load"},
            {"number": 3, "name": "Emitter", "type": "ground", "description": "To ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Base", "to_pin": "D9", "note": "Through a 1kΩ resistor"},
                    {"from_pin": "Collector", "to_pin": "Load -", "note": "Load + to the 12V supply"},
                    {"from_pin": "Emitter", "to_pin": "GND", "note": "Tie all grounds together"},
                ],
                "notes": [
                    "Drops ~1V when on, so it warms up — bolt on a heatsink above 1A.",
                    "PWM on the base dims LED strips nicely.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Dim a 12V LED strip",
                "libraries": [],
                "code": """const int BASE_PIN = 9;

void setup() {
  pinMode(BASE_PIN, OUTPUT);
}

void loop() {
  for (int duty = 0; duty <= 255; duty += 5) {
    analogWrite(BASE_PIN, duty);
    delay(30);
  }
  for (int duty = 255; duty >= 0; duty -= 5) {
    analogWrite(BASE_PIN, duty);
    delay(30);
  }
}
""",
            },
        },
    },
    {
        "id": "mosfet_irf520",
        "type": "transistor",
        "name": "IRF520 N-channel MOSFET",
        "aliases": ["irf520", "mosfet", "n-channel mosfet", "irfz44n", "mosfet module"],
        "description": "Power MOSFET for switching motors, heaters and LED strips. "
        "Logic-level types (IRLZ44N) turn on properly from 5V; the IRF520 wants ~10V.",
        "package": "TO-220",
        "tags": ["switch", "power", "pwm"],
        "pins": [
            {"number": 1, "name": "Gate", "type": "signal", "description": "Control, 220Ω in series + 10k to GND"},
            {"number": 2, "name": "Drain", "type": "signal", "description": "To the load"},
            {"number": 3, "name": "Source", "type": "ground", "description": "To ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Gate", "to_pin": "D9", "note": "220Ω in series, 10kΩ gate-to-GND"},
                    {"from_pin": "Drain", "to_pin": "Load -", "note": "Load + to the supply"},
                    {"from_pin": "Source", "to_pin": "GND", "note": "Common ground"},
                ],
                "notes": [
                    "The pull-down keeps the load off while the MCU boots.",
                    "For 5V logic prefer a logic-level MOSFET (IRLZ44N, IRL540).",
                ],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "Gate", "to_pin": "GPIO25", "note": "220Ω in series, 10kΩ to GND"},
                    {"from_pin": "Drain", "to_pin": "Load -", "note": ""},
                    {"from_pin": "Source", "to_pin": "GND", "note": ""},
                ],
                "notes": ["3.3V gate drive needs a logic-level MOSFET."],
            },
        },
        "code": {
            "esp32": {
                "title": "PWM a load with LEDC (ESP32)",
                "libraries": [],
                "code": """const int GATE_PIN = 25;
const int PWM_CHANNEL = 0;

void setup() {
  ledcSetup(PWM_CHANNEL, 5000, 8);      // 5kHz, 8-bit
  ledcAttachPin(GATE_PIN, PWM_CHANNEL);
}

void loop() {
  for (int duty = 0; duty <= 255; duty += 5) {
    ledcWrite(PWM_CHANNEL, duty);
    delay(30);
  }
}
""",
            },
        },
    },
    {
        "id": "mosfet_2n7000",
        "type": "transistor",
        "name": "2N7000 Small-signal MOSFET",
        "aliases": ["2n7000", "bs170", "small signal mosfet", "logic level mosfet"],
        "description": "Tiny logic-level N-channel MOSFET (200mA). Handy as a level "
        "shifter or for switching an LED or a buzzer.",
        "package": "TO-92",
        "tags": ["switch", "signal"],
        "pins": [
            {"number": 1, "name": "Source", "type": "ground", "description": "To ground"},
            {"number": 2, "name": "Gate", "type": "signal", "description": "Control"},
            {"number": 3, "name": "Drain", "type": "signal", "description": "To the load"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Gate", "to_pin": "D7", "note": "10kΩ gate-to-GND"},
                    {"from_pin": "Drain", "to_pin": "Load -", "note": ""},
                    {"from_pin": "Source", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Two of these plus two resistors make a bidirectional level shifter."],
            },
        },
        "code": {},
    },
    {
        "id": "optocoupler_4n35",
        "type": "ic",
        "name": "4N35 Optocoupler",
        "aliases": ["4n35", "optocoupler", "opto isolator", "pc817", "photocoupler"],
        "description": "An LED and a phototransistor in one package: passes a signal "
        "while keeping the two sides electrically isolated.",
        "package": "DIP-6",
        "tags": ["isolation", "signal"],
        "pins": [
            {"number": 1, "name": "Anode", "type": "signal", "description": "Input LED +, through 220-470Ω"},
            {"number": 2, "name": "Cathode", "type": "ground", "description": "Input LED -"},
            {"number": 3, "name": "NC", "type": "nc", "description": "Not connected"},
            {"number": 4, "name": "Emitter", "type": "ground", "description": "Output side ground"},
            {"number": 5, "name": "Collector", "type": "signal", "description": "Output, with a pull-up"},
            {"number": 6, "name": "Base", "type": "nc", "description": "Usually left open"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Anode", "to_pin": "D8", "note": "Through 330Ω"},
                    {"from_pin": "Cathode", "to_pin": "GND", "note": ""},
                    {"from_pin": "Collector", "to_pin": "Isolated VCC", "note": "Through a 10kΩ pull-up"},
                    {"from_pin": "Emitter", "to_pin": "Isolated GND", "note": "Separate ground"},
                ],
                "notes": [
                    "The output is inverted: LED on pulls the collector low.",
                    "Keep the two grounds apart or the isolation is pointless.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "triac_bt136",
        "type": "transistor",
        "name": "BT136 TRIAC",
        "aliases": ["bt136", "triac", "bta16", "ac switch"],
        "description": "Switches AC loads. With a MOC3021 opto-triac driver it becomes "
        "a solid-state AC dimmer or relay.",
        "package": "TO-220",
        "tags": ["switch", "mains", "power"],
        "pins": [
            {"number": 1, "name": "MT1", "type": "power", "description": "Main terminal 1"},
            {"number": 2, "name": "MT2", "type": "power", "description": "Main terminal 2"},
            {"number": 3, "name": "Gate", "type": "signal", "description": "Trigger, from an opto-triac"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "MT1", "to_pin": "Neutral (mains)", "note": ""},
                    {"from_pin": "MT2", "to_pin": "Load", "note": ""},
                    {"from_pin": "Gate", "to_pin": "MOC3021 output", "note": "Through a 330Ω resistor"},
                ],
                "notes": [
                    "Mains voltage — isolate the MCU with the opto-triac, never wire it directly.",
                    "If you are not confident with mains, use a ready-made relay module instead.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "seven_segment",
        "type": "display",
        "name": "7-Segment Display (single digit)",
        "aliases": ["7 segment", "seven segment", "sma42056", "led digit"],
        "description": "Eight LEDs arranged as a digit plus a decimal point, sharing a "
        "common anode or cathode. Each segment needs its own resistor.",
        "package": "0.56\" THT",
        "tags": ["output", "display"],
        "pins": [
            {"number": 1, "name": "A", "type": "digital", "description": "Top segment"},
            {"number": 2, "name": "B", "type": "digital", "description": "Top right"},
            {"number": 3, "name": "C", "type": "digital", "description": "Bottom right"},
            {"number": 4, "name": "D", "type": "digital", "description": "Bottom"},
            {"number": 5, "name": "E", "type": "digital", "description": "Bottom left"},
            {"number": 6, "name": "F", "type": "digital", "description": "Top left"},
            {"number": 7, "name": "G", "type": "digital", "description": "Middle"},
            {"number": 8, "name": "DP", "type": "digital", "description": "Decimal point"},
            {"number": 9, "name": "COM", "type": "ground", "description": "Common cathode (or anode)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "A", "to_pin": "D2", "note": "Through 220Ω"},
                    {"from_pin": "B", "to_pin": "D3", "note": "Through 220Ω"},
                    {"from_pin": "C", "to_pin": "D4", "note": "Through 220Ω"},
                    {"from_pin": "D", "to_pin": "D5", "note": "Through 220Ω"},
                    {"from_pin": "E", "to_pin": "D6", "note": "Through 220Ω"},
                    {"from_pin": "F", "to_pin": "D7", "note": "Through 220Ω"},
                    {"from_pin": "G", "to_pin": "D8", "note": "Through 220Ω"},
                    {"from_pin": "COM", "to_pin": "GND", "note": "Common-cathode part"},
                ],
                "notes": ["Common-anode displays go to 5V and the logic inverts."],
            },
        },
        "code": {
            "uno": {
                "title": "Count 0-9 on a 7-segment display",
                "libraries": [],
                "code": """// Common-cathode digit on pins 2..8 (segments A..G).
const int SEG[7] = {2, 3, 4, 5, 6, 7, 8};
const byte DIGITS[10] = {
  0b0111111, 0b0000110, 0b1011011, 0b1001111, 0b1100110,
  0b1101101, 0b1111101, 0b0000111, 0b1111111, 0b1101111
};

void showDigit(int n) {
  for (int s = 0; s < 7; s++) {
    digitalWrite(SEG[s], bitRead(DIGITS[n], s) ? HIGH : LOW);
  }
}

void setup() {
  for (int s = 0; s < 7; s++) pinMode(SEG[s], OUTPUT);
}

void loop() {
  for (int n = 0; n <= 9; n++) {
    showDigit(n);
    delay(700);
  }
}
""",
            },
        },
    },
]
