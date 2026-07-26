"""Power: regulators, converters, chargers, batteries, energy monitoring."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "lm7805",
        "type": "power",
        "name": "7805 Linear Regulator",
        "aliases": ["7805", "l7805", "lm7805", "5v regulator", "voltage regulator"],
        "description": "Classic 5V/1A linear regulator. Simple and quiet, but it burns "
        "the extra voltage as heat — 12V in at 500mA means 3.5W wasted.",
        "package": "TO-220",
        "tags": ["power", "regulator", "beginner"],
        "pins": [
            {"number": 1, "name": "IN", "type": "power", "description": "7-25V input"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground (also the tab)"},
            {"number": 3, "name": "OUT", "type": "power", "description": "5V output"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "IN", "to_pin": "12V supply", "note": "0.33µF from IN to GND"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "5V rail", "note": "0.1µF from OUT to GND"},
                ],
                "notes": [
                    "Needs ~2V of headroom — it cannot make 5V from a 6V battery under load.",
                    "Above ~300mA it wants a heatsink.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "ams1117",
        "type": "power",
        "name": "AMS1117 3.3V Regulator",
        "aliases": ["ams1117", "1117", "3.3v regulator", "ldo regulator"],
        "description": "The 3.3V LDO on nearly every ESP and sensor breakout. 800mA "
        "with about 1.1V of dropout.",
        "package": "SOT-223",
        "tags": ["power", "regulator", "smd"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 2, "name": "OUT", "type": "power", "description": "3.3V output"},
            {"number": 3, "name": "IN", "type": "power", "description": "4.5-15V input"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "IN", "to_pin": "5V", "note": "10µF input capacitor"},
                    {"from_pin": "OUT", "to_pin": "3V3 rail", "note": "22µF output capacitor"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Wi-Fi bursts of 500mA are what browns out an under-specified AMS1117."],
            },
        },
        "code": {},
    },
    {
        "id": "lm2596",
        "type": "power",
        "name": "LM2596 Buck Converter",
        "aliases": ["lm2596", "buck converter", "step down converter", "dc-dc converter"],
        "description": "Adjustable step-down module, 3A and roughly 90% efficient — the "
        "right way to get 5V from a 12V battery without cooking a linear regulator.",
        "package": "Module",
        "tags": ["power", "converter", "iot"],
        "pins": [
            {"number": 1, "name": "IN+", "type": "power", "description": "4.5-40V input"},
            {"number": 2, "name": "IN-", "type": "ground", "description": "Input ground"},
            {"number": 3, "name": "OUT+", "type": "power", "description": "Adjustable output"},
            {"number": 4, "name": "OUT-", "type": "ground", "description": "Output ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "IN+", "to_pin": "12V battery +", "note": ""},
                    {"from_pin": "IN-", "to_pin": "Battery -", "note": ""},
                    {"from_pin": "OUT+", "to_pin": "5V (VIN)", "note": "Set to 5.0V BEFORE connecting the board"},
                    {"from_pin": "OUT-", "to_pin": "GND", "note": ""},
                ],
                "notes": [
                    "Always set the output with a multimeter first — it ships at whatever the pot happens to be.",
                    "Output must be at least ~1.5V below the input.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "mt3608",
        "type": "power",
        "name": "MT3608 Boost Converter",
        "aliases": ["mt3608", "boost converter", "step up converter", "xl6009"],
        "description": "Step-up module: run 5V electronics from a single Li-ion cell or "
        "from two AA batteries. Up to 2A input current.",
        "package": "Module",
        "tags": ["power", "converter", "battery"],
        "pins": [
            {"number": 1, "name": "IN+", "type": "power", "description": "2-24V input"},
            {"number": 2, "name": "IN-", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "OUT+", "type": "power", "description": "Boosted output (up to 28V)"},
            {"number": 4, "name": "OUT-", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "IN+", "to_pin": "18650 +", "note": "3.0-4.2V from the cell"},
                    {"from_pin": "IN-", "to_pin": "18650 -", "note": ""},
                    {"from_pin": "OUT+", "to_pin": "5V (VIN)", "note": "Trim to 5.0V before connecting"},
                    {"from_pin": "OUT-", "to_pin": "GND", "note": ""},
                ],
                "notes": ["A boost converter cannot output less than its input voltage."],
            },
        },
        "code": {},
    },
    {
        "id": "tp4056",
        "type": "power",
        "name": "TP4056 Li-ion Charger Module",
        "aliases": ["tp4056", "lithium charger", "18650 charger", "li-ion charging module"],
        "description": "USB charger for a single Li-ion/LiPo cell at 1A. Buy the "
        "version with the DW01 protection chip — it saves the cell from abuse.",
        "package": "Module (micro-USB / USB-C)",
        "tags": ["power", "battery", "charger", "iot"],
        "pins": [
            {"number": 1, "name": "IN+", "type": "power", "description": "5V from USB"},
            {"number": 2, "name": "IN-", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "BAT+", "type": "power", "description": "Cell positive"},
            {"number": 4, "name": "BAT-", "type": "ground", "description": "Cell negative"},
            {"number": 5, "name": "OUT+", "type": "power", "description": "Protected output (protection version)"},
            {"number": 6, "name": "OUT-", "type": "ground", "description": "Protected ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "BAT+", "to_pin": "Cell +", "note": ""},
                    {"from_pin": "BAT-", "to_pin": "Cell -", "note": ""},
                    {"from_pin": "OUT+", "to_pin": "Boost / regulator IN+", "note": "Never power the load from BAT+"},
                    {"from_pin": "OUT-", "to_pin": "GND", "note": ""},
                ],
                "notes": [
                    "The default charge current is 1A; change R3 for smaller cells.",
                    "Take the load from OUT+/OUT-, so the protection circuit stays in the path.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "battery_18650",
        "type": "power",
        "name": "18650 Li-ion Cell",
        "aliases": ["18650", "lithium battery", "li-ion cell", "battery holder"],
        "description": "The standard rechargeable cylindrical cell: 3.7V nominal, "
        "2000-3500mAh. Powers most portable IoT builds.",
        "package": "18650 cell + holder",
        "tags": ["power", "battery", "iot"],
        "pins": [
            {"number": 1, "name": "+", "type": "power", "description": "Positive (button end)"},
            {"number": 2, "name": "-", "type": "ground", "description": "Negative (flat end)"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "+", "to_pin": "TP4056 BAT+", "note": "Charge and protect through the module"},
                    {"from_pin": "-", "to_pin": "TP4056 BAT-", "note": ""},
                ],
                "notes": [
                    "Never discharge below 3.0V or charge above 4.2V.",
                    "Beware fake 9900mAh cells — genuine capacity tops out near 3500mAh.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "solar_panel",
        "type": "power",
        "name": "Small Solar Panel (6V)",
        "aliases": ["solar panel", "photovoltaic panel", "6v solar", "solar cell"],
        "description": "Turns light into current for off-grid nodes. Pair it with a "
        "charge controller (CN3065 or TP4056+regulator) and a Li-ion cell.",
        "package": "Panel",
        "tags": ["power", "solar", "iot", "offgrid"],
        "pins": [
            {"number": 1, "name": "+", "type": "power", "description": "Positive output"},
            {"number": 2, "name": "-", "type": "ground", "description": "Negative output"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "+", "to_pin": "Charge controller IN+", "note": "Schottky diode blocks night-time drain"},
                    {"from_pin": "-", "to_pin": "Charge controller IN-", "note": ""},
                ],
                "notes": [
                    "Size the panel for the worst week of weather, not the best day.",
                    "Deep sleep is what makes a solar node actually survive winter.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "ina219",
        "type": "power",
        "name": "INA219 Current & Power Monitor",
        "aliases": ["ina219", "current monitor", "power monitor", "ina226"],
        "description": "High-side I2C current, voltage and power meter — measure "
        "exactly what your battery project draws while it sleeps.",
        "package": "Module",
        "tags": ["power", "i2c", "measurement", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3-5.5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 5, "name": "VIN+", "type": "power", "description": "Supply side of the shunt"},
            {"number": 6, "name": "VIN-", "type": "power", "description": "Load side of the shunt"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                    {"from_pin": "VIN+", "to_pin": "Battery +", "note": "In series with the load"},
                    {"from_pin": "VIN-", "to_pin": "Load +", "note": ""},
                ],
                "notes": ["Default address 0x40; the 0.1Ω shunt reads up to 3.2A."],
            },
        },
        "code": {
            "esp32": {
                "title": "Log current, voltage and power",
                "libraries": ["Adafruit INA219"],
                "code": """#include <Adafruit_INA219.h>

Adafruit_INA219 monitor;

void setup() {
  Serial.begin(115200);
  if (!monitor.begin()) {
    Serial.println("INA219 not found");
    while (1) delay(10);
  }
}

void loop() {
  float volts = monitor.getBusVoltage_V();
  float milliamps = monitor.getCurrent_mA();
  Serial.printf("%.2f V  %.1f mA  %.0f mW\\n",
                volts, milliamps, monitor.getPower_mW());
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "zmpt101b",
        "type": "power",
        "name": "ZMPT101B AC Voltage Sensor",
        "aliases": ["zmpt101b", "ac voltage sensor", "mains voltage sensor"],
        "description": "Transformer-isolated module that scales mains voltage down to "
        "something an ADC can read — energy monitors and brownout detection.",
        "package": "Module",
        "tags": ["power", "analog", "mains", "measurement"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "OUT", "type": "analog", "description": "AC waveform biased at VCC/2"},
            {"number": 4, "name": "AC IN", "type": "power", "description": "Mains terminals (isolated)"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": "Then the output centres near 1.65V"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "GPIO34", "note": "Sample fast and compute RMS"},
                ],
                "notes": [
                    "Mains wiring is lethal — only attempt this if you are qualified.",
                    "Calibrate the on-board pot against a known reference voltage.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "pzem004t",
        "type": "power",
        "name": "PZEM-004T Energy Meter",
        "aliases": ["pzem-004t", "pzem", "energy meter", "kwh meter module"],
        "description": "Ready-made AC energy meter: voltage, current, power, energy, "
        "frequency and power factor over Modbus serial, with an isolated CT clamp.",
        "package": "Module + current transformer",
        "tags": ["power", "uart", "mains", "iot"],
        "pins": [
            {"number": 1, "name": "5V", "type": "power", "description": "Logic supply"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "TX", "type": "uart", "description": "To the MCU's RX"},
            {"number": 4, "name": "RX", "type": "uart", "description": "From the MCU's TX"},
            {"number": 5, "name": "AC IN", "type": "power", "description": "Mains voltage sense"},
            {"number": 6, "name": "CT", "type": "signal", "description": "Split-core current clamp"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "5V", "to_pin": "5V (VIN)", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "TX", "to_pin": "GPIO16", "note": "ESP32 RX2"},
                    {"from_pin": "RX", "to_pin": "GPIO17", "note": "ESP32 TX2"},
                ],
                "notes": [
                    "The clamp goes around ONE conductor (live), never both.",
                    "The measuring side is isolated, but the mains terminals are not — treat with respect.",
                ],
            },
        },
        "code": {
            "esp32": {
                "title": "Read household power over Modbus",
                "libraries": ["PZEM004Tv30"],
                "code": """#include <PZEM004Tv30.h>

PZEM004Tv30 pzem(Serial2, 16, 17);      // RX, TX

void setup() {
  Serial.begin(115200);
}

void loop() {
  float volts = pzem.voltage();
  if (isnan(volts)) {
    Serial.println("No reading from the meter");
  } else {
    Serial.printf("%.1f V  %.2f A  %.1f W  %.3f kWh  pf %.2f\\n",
                  volts, pzem.current(), pzem.power(),
                  pzem.energy(), pzem.pf());
  }
  delay(5000);
}
""",
            },
        },
    },
    {
        "id": "usb_c_breakout",
        "type": "connector",
        "name": "USB-C Power Breakout",
        "aliases": ["usb-c breakout", "usb c connector", "type-c power board", "pd trigger"],
        "description": "Brings USB-C 5V out to solder pads, with the CC pull-downs "
        "already fitted. PD-trigger versions can request 9V, 12V or 20V.",
        "package": "Breakout board",
        "tags": ["power", "connector", "usb"],
        "pins": [
            {"number": 1, "name": "VBUS", "type": "power", "description": "5V (or the negotiated voltage)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "CC1/CC2", "type": "signal", "description": "5.1kΩ pull-downs to advertise a sink"},
            {"number": 4, "name": "D+/D-", "type": "signal", "description": "USB 2.0 data (if wired)"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VBUS", "to_pin": "5V (VIN)", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Without the CC resistors a USB-C charger will supply nothing at all."],
            },
        },
        "code": {},
    },
    {
        "id": "relay_module_4ch",
        "type": "power",
        "name": "4-channel Relay Module",
        "aliases": ["4 channel relay", "relay board", "relay module 4", "optocoupler relay"],
        "description": "Four opto-isolated relays on one board for switching mains "
        "appliances from a microcontroller. Home-automation workhorse.",
        "package": "Module",
        "tags": ["actuator", "relay", "mains", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V for the coils (~70mA each)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "IN1-IN4", "type": "digital", "description": "Control inputs (usually active LOW)"},
            {"number": 4, "name": "JD-VCC", "type": "power", "description": "Coil supply — remove the jumper to isolate"},
            {"number": 5, "name": "COM/NO/NC", "type": "power", "description": "Switched contacts per channel"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": "Four coils need ~300mA"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "IN1-IN4", "to_pin": "GPIO25/26/27/14", "note": "LOW switches the relay on"},
                ],
                "notes": [
                    "Relays often click on during boot — pick pins that idle high, or drive them inverted.",
                    "Mains side: keep creepage distance and never run mains across the module's low-voltage tracks.",
                ],
            },
        },
        "code": {
            "esp32": {
                "title": "Web-controlled relay board",
                "libraries": ["WiFi", "WebServer"],
                "code": """#include <WiFi.h>
#include <WebServer.h>

const char* WIFI_SSID = "your-wifi";
const char* WIFI_PASS = "your-password";
const int RELAYS[4] = {25, 26, 27, 14};

WebServer server(80);

void setRelay(int index, bool on) {
  digitalWrite(RELAYS[index], on ? LOW : HIGH);   // active LOW board
}

void setup() {
  Serial.begin(115200);
  for (int pin : RELAYS) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);                      // all off at boot
  }
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) delay(400);
  Serial.println(WiFi.localIP());

  // GET /relay?ch=0&on=1
  server.on("/relay", []() {
    int channel = server.arg("ch").toInt();
    bool on = server.arg("on") == "1";
    if (channel >= 0 && channel < 4) setRelay(channel, on);
    server.send(200, "text/plain", "ok");
  });
  server.begin();
}

void loop() {
  server.handleClient();
}
""",
            },
        },
    },
]
