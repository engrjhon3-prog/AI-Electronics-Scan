"""Storage, timekeeping, human input and the connectors that tie it together."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "ds3231",
        "type": "module",
        "name": "DS3231 Real-Time Clock",
        "aliases": ["ds3231", "rtc module", "real time clock", "ds1307", "zs-042"],
        "description": "Temperature-compensated RTC accurate to a couple of minutes a "
        "year, with a battery backup so time survives a power cut.",
        "package": "Module (ZS-042)",
        "tags": ["time", "i2c", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5.5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 4, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 5, "name": "SQW", "type": "digital", "description": "Alarm / square-wave output"},
            {"number": 6, "name": "32K", "type": "digital", "description": "32.768kHz reference output"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "A4", "note": ""},
                    {"from_pin": "SCL", "to_pin": "A5", "note": ""},
                    {"from_pin": "SQW", "to_pin": "D2", "note": "Optional alarm interrupt"},
                ],
                "notes": [
                    "Address 0x68; the on-board AT24C32 EEPROM answers at 0x57.",
                    "Many ZS-042 boards try to charge a non-rechargeable CR2032 — remove resistor R5.",
                ],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                ],
                "notes": ["A Wi-Fi board can use NTP instead — but the RTC keeps time offline."],
            },
        },
        "code": {
            "uno": {
                "title": "Read and set the clock",
                "libraries": ["RTClib"],
                "code": """#include <RTClib.h>

RTC_DS3231 rtc;

void setup() {
  Serial.begin(9600);
  if (!rtc.begin()) {
    Serial.println("RTC not found");
    while (1) delay(10);
  }
  if (rtc.lostPower()) {
    // Set the clock to this sketch's compile time, once.
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }
}

void loop() {
  DateTime now = rtc.now();
  Serial.print(now.timestamp(DateTime::TIMESTAMP_FULL));
  Serial.print("  ");
  Serial.print(rtc.getTemperature());
  Serial.println(" C");
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "microsd_module",
        "type": "module",
        "name": "microSD Card Module",
        "aliases": ["microsd module", "sd card module", "sd module", "data logger module"],
        "description": "SPI microSD holder with a 3.3V regulator and level shifting — "
        "the standard way to log data offline.",
        "package": "Module",
        "tags": ["storage", "spi", "datalogging"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V (module regulates to 3.3V)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "MISO", "type": "spi", "description": "Data out"},
            {"number": 4, "name": "MOSI", "type": "spi", "description": "Data in"},
            {"number": 5, "name": "SCK", "type": "spi", "description": "Clock"},
            {"number": 6, "name": "CS", "type": "spi", "description": "Chip select"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "MISO", "to_pin": "D12", "note": ""},
                    {"from_pin": "MOSI", "to_pin": "D11", "note": ""},
                    {"from_pin": "SCK", "to_pin": "D13", "note": ""},
                    {"from_pin": "CS", "to_pin": "D10", "note": ""},
                ],
                "notes": [
                    "Format the card FAT32 and keep it 32GB or smaller.",
                    "Cheap modules lack MISO tri-stating and can upset other SPI devices.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Append sensor readings to a CSV file",
                "libraries": ["SD", "SPI"],
                "code": """#include <SPI.h>
#include <SD.h>

const int CS_PIN = 10;

void setup() {
  Serial.begin(9600);
  if (!SD.begin(CS_PIN)) {
    Serial.println("Card failed or not present");
    return;
  }
  File file = SD.open("log.csv", FILE_WRITE);
  if (file) {
    file.println("millis,reading");
    file.close();
  }
}

void loop() {
  File file = SD.open("log.csv", FILE_WRITE);
  if (file) {
    file.print(millis());
    file.print(',');
    file.println(analogRead(A0));
    file.close();
  }
  delay(5000);
}
""",
            },
        },
    },
    {
        "id": "at24c32",
        "type": "ic",
        "name": "AT24C32 I2C EEPROM",
        "aliases": ["at24c32", "eeprom", "24c32", "i2c eeprom", "at24c256"],
        "description": "External non-volatile memory over I2C — settings, calibration "
        "data and small logs that must survive a power cut.",
        "package": "DIP-8 / on the RTC module",
        "tags": ["storage", "i2c"],
        "pins": [
            {"number": 1, "name": "A0", "type": "digital", "description": "Address bit 0"},
            {"number": 2, "name": "A1", "type": "digital", "description": "Address bit 1"},
            {"number": 3, "name": "A2", "type": "digital", "description": "Address bit 2"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 5, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 6, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 7, "name": "WP", "type": "digital", "description": "Write protect (GND = writable)"},
            {"number": 8, "name": "VCC", "type": "power", "description": "1.8-5.5V"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "A4", "note": ""},
                    {"from_pin": "SCL", "to_pin": "A5", "note": ""},
                    {"from_pin": "WP", "to_pin": "GND", "note": "Allow writes"},
                ],
                "notes": ["Wait 5ms after each write page, or the next read returns garbage."],
            },
        },
        "code": {},
    },
    {
        "id": "keypad_4x4",
        "type": "switch",
        "name": "4x4 Matrix Keypad",
        "aliases": ["keypad", "4x4 keypad", "matrix keypad", "membrane keypad"],
        "description": "Sixteen buttons wired as a matrix, so eight pins read them all "
        "— PIN entry, menus, calculators.",
        "package": "Membrane / plastic keypad",
        "tags": ["input", "digital", "ui"],
        "pins": [
            {"number": 1, "name": "R1-R4", "type": "digital", "description": "Row pins"},
            {"number": 2, "name": "C1-C4", "type": "digital", "description": "Column pins"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "R1-R4", "to_pin": "D9,D8,D7,D6", "note": "Rows"},
                    {"from_pin": "C1-C4", "to_pin": "D5,D4,D3,D2", "note": "Columns"},
                ],
                "notes": ["The library handles pull-ups and scanning; no external parts needed."],
            },
        },
        "code": {
            "uno": {
                "title": "Read keys and check a PIN",
                "libraries": ["Keypad"],
                "code": """#include <Keypad.h>

const byte ROWS = 4, COLS = 4;
char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);
String entered = "";
const String PIN_CODE = "1234";

void setup() {
  Serial.begin(9600);
}

void loop() {
  char key = keypad.getKey();
  if (!key) return;

  if (key == '#') {
    Serial.println(entered == PIN_CODE ? "Unlocked" : "Wrong PIN");
    entered = "";
  } else if (key == '*') {
    entered = "";
  } else {
    entered += key;
  }
}
""",
            },
        },
    },
    {
        "id": "dip_switch",
        "type": "switch",
        "name": "DIP Switch",
        "aliases": ["dip switch", "config switch", "slide switch bank"],
        "description": "A row of tiny slide switches for setting addresses or modes "
        "without reflashing firmware.",
        "package": "DIP-8 (4-position)",
        "tags": ["input", "config"],
        "pins": [
            {"number": 1, "name": "SW1-SW4 A", "type": "digital", "description": "One side of each switch"},
            {"number": 2, "name": "SW1-SW4 B", "type": "ground", "description": "Common side to ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "SW1-SW4 A", "to_pin": "D4..D7", "note": "INPUT_PULLUP on each"},
                    {"from_pin": "SW1-SW4 B", "to_pin": "GND", "note": "Commoned"},
                ],
                "notes": ["Closed reads LOW with internal pull-ups."],
            },
        },
        "code": {},
    },
    {
        "id": "toggle_switch",
        "type": "switch",
        "name": "Toggle / Rocker Switch",
        "aliases": ["toggle switch", "rocker switch", "spst switch", "power switch"],
        "description": "Mechanical on/off switch for power rails and mode selection. "
        "SPST, SPDT and DPDT variants cover most needs.",
        "package": "Panel mount",
        "tags": ["input", "power"],
        "pins": [
            {"number": 1, "name": "COM", "type": "power", "description": "Common"},
            {"number": 2, "name": "NO", "type": "power", "description": "Closed when switched on"},
            {"number": 3, "name": "NC", "type": "power", "description": "Closed when switched off (SPDT)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "COM", "to_pin": "Battery +", "note": "Switch the positive rail"},
                    {"from_pin": "NO", "to_pin": "VIN", "note": ""},
                ],
                "notes": ["Check the current rating before putting one in a motor supply."],
            },
        },
        "code": {},
    },
    {
        "id": "breadboard",
        "type": "connector",
        "name": "Solderless Breadboard",
        "aliases": ["breadboard", "protoboard", "solderless breadboard", "mb-102"],
        "description": "Rows of spring clips for building circuits without solder. The "
        "long side rails are power buses; each half-row of five is one node.",
        "package": "830 / 400 tie points",
        "tags": ["prototyping", "beginner"],
        "pins": [
            {"number": 1, "name": "+ rail", "type": "power", "description": "Power bus (often split in the middle)"},
            {"number": 2, "name": "- rail", "type": "ground", "description": "Ground bus"},
            {"number": 3, "name": "a-e / f-j", "type": "signal", "description": "Five clips per node, split by the centre channel"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "+ rail", "to_pin": "5V", "note": ""},
                    {"from_pin": "- rail", "to_pin": "GND", "note": ""},
                ],
                "notes": [
                    "On big boards the power rails are split halfway — bridge them or half the board is dead.",
                    "Not suitable for mains, high current, or anything above a few MHz.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "jumper_wires",
        "type": "connector",
        "name": "Jumper Wires",
        "aliases": ["jumper wires", "dupont wires", "breadboard wires", "dupont cable"],
        "description": "Pre-crimped wires with Dupont ends: male-male for breadboards, "
        "male-female for modules, female-female for header pins.",
        "package": "M-M / M-F / F-F",
        "tags": ["prototyping", "beginner"],
        "pins": [
            {"number": 1, "name": "End A", "type": "signal", "description": "Male pin or female socket"},
            {"number": 2, "name": "End B", "type": "signal", "description": "Male pin or female socket"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "End A", "to_pin": "Board pin", "note": "Red for power, black for ground"},
                    {"from_pin": "End B", "to_pin": "Module pin", "note": ""},
                ],
                "notes": ["Intermittent faults are usually a tired jumper — swap it before debugging code."],
            },
        },
        "code": {},
    },
    {
        "id": "screw_terminal",
        "type": "connector",
        "name": "Screw Terminal Block",
        "aliases": ["screw terminal", "terminal block", "kf301", "phoenix connector"],
        "description": "Clamps bare wire under a screw — the reliable way to attach "
        "power, motors and field wiring to a PCB.",
        "package": "5.08mm / 3.5mm pitch",
        "tags": ["connector", "power"],
        "pins": [
            {"number": 1, "name": "Terminal 1", "type": "power", "description": "Screw clamp"},
            {"number": 2, "name": "Terminal 2", "type": "power", "description": "Screw clamp"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal 1", "to_pin": "Supply +", "note": "Tin the wire or use a ferrule"},
                    {"from_pin": "Terminal 2", "to_pin": "Supply -", "note": ""},
                ],
                "notes": ["Retighten after the first thermal cycle — copper creeps."],
            },
        },
        "code": {},
    },
    {
        "id": "header_pins",
        "type": "connector",
        "name": "Header Pins & Sockets",
        "aliases": ["header pins", "pin header", "female header", "2.54mm header"],
        "description": "The 2.54mm pins and sockets that every module and shield uses. "
        "Sockets let you replace a module without desoldering.",
        "package": "2.54mm pitch strip",
        "tags": ["connector", "prototyping"],
        "pins": [
            {"number": 1, "name": "Pin", "type": "signal", "description": "One per 2.54mm position"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Pin", "to_pin": "PCB pad", "note": "Solder from the opposite side"},
                ],
                "notes": ["Socket a module rather than soldering it — you will want it back."],
            },
        },
        "code": {},
    },
    {
        "id": "jst_connector",
        "type": "connector",
        "name": "JST Connector (PH / XH)",
        "aliases": ["jst connector", "jst ph", "jst xh", "battery connector"],
        "description": "Polarised locking connector used for LiPo batteries, servos "
        "and sensor leads — it cannot be plugged in backwards.",
        "package": "2.0mm (PH) / 2.5mm (XH)",
        "tags": ["connector", "battery"],
        "pins": [
            {"number": 1, "name": "Pin 1", "type": "power", "description": "Usually positive (check first!)"},
            {"number": 2, "name": "Pin 2", "type": "ground", "description": "Usually negative"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Pin 1", "to_pin": "BAT+", "note": "Meter it before trusting the colours"},
                    {"from_pin": "Pin 2", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Polarity is not standardised across sellers — always check with a meter."],
            },
        },
        "code": {},
    },
    {
        "id": "heat_sink",
        "type": "connector",
        "name": "Heatsink",
        "aliases": ["heatsink", "heat sink", "cooling fin", "thermal pad"],
        "description": "Aluminium fins that move heat away from regulators, drivers and "
        "MOSFETs. Use thermal paste or a thermal pad, never a dry joint.",
        "package": "TO-220 clip-on / adhesive",
        "tags": ["thermal", "power"],
        "pins": [
            {"number": 1, "name": "Mounting face", "type": "signal", "description": "Contacts the component tab"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Mounting face", "to_pin": "Regulator tab", "note": "Thermal pad in between"},
                ],
                "notes": ["The tab of a TO-220 is usually electrically live — insulate it."],
            },
        },
        "code": {},
    },
    {
        "id": "push_button",
        "type": "switch",
        "name": "Tactile Push Button",
        "aliases": ["button", "push button", "momentary switch", "tact switch"],
        "description": "A momentary tactile switch. Use the internal pull-up so the "
        "pin reads HIGH when released and LOW when pressed.",
        "package": "6mm THT",
        "tags": ["input", "beginner"],
        "pins": [
            {"number": 1, "name": "Pin 1", "type": "signal", "description": "One side of the switch"},
            {"number": 2, "name": "Pin 2", "type": "ground", "description": "Other side, to GND"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Pin 1", "to_pin": "D2", "note": "Use INPUT_PULLUP"},
                    {"from_pin": "Pin 2", "to_pin": "GND", "note": ""},
                ],
                "notes": ["With INPUT_PULLUP the pin reads LOW when pressed."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "Pin 1", "to_pin": "GPIO4", "note": "Use INPUT_PULLUP"},
                    {"from_pin": "Pin 2", "to_pin": "GND", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Read a push button",
                "libraries": [],
                "code": """const int BUTTON_PIN = 2;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  bool pressed = digitalRead(BUTTON_PIN) == LOW;
  Serial.println(pressed ? "Pressed" : "Released");
  delay(100);
}
""",
            },
        },
    },
]
