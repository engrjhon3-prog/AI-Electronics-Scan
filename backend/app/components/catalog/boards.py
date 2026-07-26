"""Development boards — the thing everything else plugs into."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "arduino_uno",
        "type": "board",
        "name": "Arduino Uno R3",
        "aliases": ["arduino uno", "uno r3", "arduino board"],
        "description": "The reference Arduino: ATmega328P, 14 digital pins (6 PWM), 6 "
        "analog inputs, 5V logic. Sturdy, forgiving and endlessly documented.",
        "package": "Board",
        "tags": ["board", "beginner", "avr"],
        "pins": [
            {"number": 1, "name": "5V", "type": "power", "description": "Regulated 5V out (~500mA from USB)"},
            {"number": 2, "name": "3.3V", "type": "power", "description": "50mA maximum — very limited"},
            {"number": 3, "name": "VIN", "type": "power", "description": "7-12V raw input"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground (three pins)"},
            {"number": 5, "name": "D0-D13", "type": "digital", "description": "Digital I/O; 3, 5, 6, 9, 10, 11 do PWM"},
            {"number": 6, "name": "A0-A5", "type": "analog", "description": "10-bit analog inputs"},
            {"number": 7, "name": "A4/A5", "type": "i2c", "description": "SDA / SCL"},
            {"number": 8, "name": "D10-D13", "type": "spi", "description": "SS, MOSI, MISO, SCK"},
            {"number": 9, "name": "D2/D3", "type": "digital", "description": "External interrupt pins"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "5V", "to_pin": "Sensor VCC", "note": "Budget 500mA in total"},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": "Every ground must be common"},
                    {"from_pin": "A4/A5", "to_pin": "I2C bus", "note": "SDA / SCL"},
                ],
                "notes": [
                    "Each pin sources at most 20mA, and 200mA across the whole chip.",
                    "D13 has the built-in LED wired to it — avoid it for inputs.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Scan the I2C bus for devices",
                "libraries": ["Wire"],
                "code": """#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(9600);
  Serial.println("Scanning I2C...");
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      Serial.println(addr, HEX);
    }
  }
  Serial.println("Done");
}

void loop() {}
""",
            },
        },
    },
    {
        "id": "arduino_nano",
        "type": "board",
        "name": "Arduino Nano",
        "aliases": ["arduino nano", "nano v3", "nano board"],
        "description": "The Uno's brain in a breadboard-friendly DIP footprint, plus "
        "two extra analog inputs (A6/A7, analog-only).",
        "package": "Board (DIP-30)",
        "tags": ["board", "beginner", "avr"],
        "pins": [
            {"number": 1, "name": "5V", "type": "power", "description": "Regulated 5V"},
            {"number": 2, "name": "VIN", "type": "power", "description": "7-12V input"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "D2-D13", "type": "digital", "description": "Digital I/O"},
            {"number": 5, "name": "A0-A7", "type": "analog", "description": "A6/A7 are analog-input only"},
        ],
        "wiring": {
            "nano": {
                "connections": [
                    {"from_pin": "5V", "to_pin": "Breadboard + rail", "note": ""},
                    {"from_pin": "GND", "to_pin": "Breadboard - rail", "note": ""},
                ],
                "notes": ["Clone boards usually need the 'old bootloader' option to upload."],
            },
        },
        "code": {},
    },
    {
        "id": "arduino_mega",
        "type": "board",
        "name": "Arduino Mega 2560",
        "aliases": ["arduino mega", "mega 2560", "atmega2560"],
        "description": "54 digital pins, 16 analog inputs and four hardware serial "
        "ports — for projects that simply ran out of room on an Uno.",
        "package": "Board",
        "tags": ["board", "avr"],
        "pins": [
            {"number": 1, "name": "5V", "type": "power", "description": "Regulated 5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "D0-D53", "type": "digital", "description": "54 digital pins, 15 with PWM"},
            {"number": 4, "name": "A0-A15", "type": "analog", "description": "16 analog inputs"},
            {"number": 5, "name": "D20/D21", "type": "i2c", "description": "SDA / SCL"},
            {"number": 6, "name": "D50-D53", "type": "spi", "description": "MISO, MOSI, SCK, SS"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "D20/D21", "to_pin": "I2C bus", "note": "Different pins from the Uno"},
                    {"from_pin": "5V", "to_pin": "Sensor VCC", "note": ""},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": ""},
                ],
                "notes": ["Serial1-3 make it the natural choice for GPS + GSM + display together."],
            },
        },
        "code": {},
    },
    {
        "id": "esp32_devkit",
        "type": "board",
        "name": "ESP32 DevKit V1",
        "aliases": ["esp32", "esp32 devkit", "esp32 wroom", "esp32 dev board"],
        "description": "Dual-core 240MHz MCU with Wi-Fi and Bluetooth, 34 GPIOs, ADC, "
        "DAC, touch inputs and deep sleep. The default IoT board.",
        "package": "Board (30/38-pin)",
        "tags": ["board", "wifi", "bluetooth", "iot"],
        "pins": [
            {"number": 1, "name": "3V3", "type": "power", "description": "3.3V out (~600mA from the on-board LDO)"},
            {"number": 2, "name": "VIN", "type": "power", "description": "5V input"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "GPIO21/22", "type": "i2c", "description": "Default SDA / SCL"},
            {"number": 5, "name": "GPIO18/19/23/5", "type": "spi", "description": "SCK, MISO, MOSI, SS (VSPI)"},
            {"number": 6, "name": "GPIO32-39", "type": "analog", "description": "ADC1 — usable while Wi-Fi is on"},
            {"number": 7, "name": "GPIO34-39", "type": "analog", "description": "Input only, no pull-ups"},
            {"number": 8, "name": "GPIO0/2/12/15", "type": "digital", "description": "Strapping pins — affect boot mode"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "3V3", "to_pin": "Sensor VCC", "note": "3.3V logic — most GPIOs are NOT 5V tolerant"},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": ""},
                    {"from_pin": "GPIO21/22", "to_pin": "I2C bus", "note": "SDA / SCL"},
                ],
                "notes": [
                    "ADC2 pins stop working once Wi-Fi starts — stick to GPIO32-39 for analog.",
                    "Hold GPIO0 low at reset to flash; leave it alone otherwise.",
                ],
            },
        },
        "code": {
            "esp32": {
                "title": "Connect to Wi-Fi and serve a page",
                "libraries": ["WiFi", "WebServer"],
                "code": """#include <WiFi.h>
#include <WebServer.h>

const char* WIFI_SSID = "your-wifi";
const char* WIFI_PASS = "your-password";

WebServer server(80);

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print('.');
  }
  Serial.print("\\nIP address: ");
  Serial.println(WiFi.localIP());

  server.on("/", []() {
    server.send(200, "text/html",
                "<h1>ESP32 online</h1><p>Uptime: " +
                String(millis() / 1000) + "s</p>");
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
    {
        "id": "esp32_s3",
        "type": "board",
        "name": "ESP32-S3 DevKit",
        "aliases": ["esp32-s3", "esp32 s3", "s3 devkit"],
        "description": "ESP32 with native USB, more RAM and vector instructions for "
        "on-device machine learning — camera and voice projects.",
        "package": "Board",
        "tags": ["board", "wifi", "iot", "ai"],
        "pins": [
            {"number": 1, "name": "3V3", "type": "power", "description": "3.3V out"},
            {"number": 2, "name": "5V", "type": "power", "description": "USB input"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "GPIO8/9", "type": "i2c", "description": "Default SDA / SCL"},
            {"number": 5, "name": "GPIO19/20", "type": "digital", "description": "Native USB D-/D+"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "3V3", "to_pin": "Sensor VCC", "note": ""},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": ""},
                ],
                "notes": ["Native USB means it can act as a keyboard, mouse or mass-storage device."],
            },
        },
        "code": {},
    },
    {
        "id": "nodemcu_esp8266",
        "type": "board",
        "name": "NodeMCU ESP8266",
        "aliases": ["nodemcu", "esp8266 board", "esp-12e", "nodemcu v3"],
        "description": "Cheap single-core Wi-Fi board. One analog input, fewer GPIOs "
        "than an ESP32, but it is still perfect for a one-sensor node.",
        "package": "Board",
        "tags": ["board", "wifi", "iot", "budget"],
        "pins": [
            {"number": 1, "name": "3V3", "type": "power", "description": "3.3V out"},
            {"number": 2, "name": "VIN", "type": "power", "description": "5V input"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "D1/D2", "type": "i2c", "description": "SCL / SDA (GPIO5 / GPIO4)"},
            {"number": 5, "name": "A0", "type": "analog", "description": "Single ADC, 0-3.3V on most boards"},
            {"number": 6, "name": "D0", "type": "digital", "description": "GPIO16 — wire to RST for deep-sleep wake"},
        ],
        "wiring": {
            "esp8266": {
                "connections": [
                    {"from_pin": "3V3", "to_pin": "Sensor VCC", "note": ""},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": ""},
                    {"from_pin": "D1/D2", "to_pin": "I2C bus", "note": "SCL / SDA"},
                    {"from_pin": "D0", "to_pin": "RST", "note": "Required to wake from deep sleep"},
                ],
                "notes": ["D3, D4 and D8 are strapping pins — a sensor pulling them the wrong way blocks boot."],
            },
        },
        "code": {
            "esp8266": {
                "title": "Deep-sleep sensor node",
                "libraries": ["ESP8266WiFi", "ESP8266HTTPClient"],
                "code": """#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* WIFI_SSID = "your-wifi";
const char* WIFI_PASS = "your-password";
const char* ENDPOINT = "http://example.com/api/reading";

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  for (int i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) delay(250);

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, ENDPOINT);
    http.addHeader("Content-Type", "application/json");
    http.POST("{\\"value\\":" + String(analogRead(A0)) + "}");
    http.end();
  }
  // Sleep 15 minutes. D0 must be wired to RST for this to wake up.
  ESP.deepSleep(15 * 60e6);
}

void loop() {}
""",
            },
        },
    },
    {
        "id": "wemos_d1_mini",
        "type": "board",
        "name": "Wemos D1 Mini",
        "aliases": ["d1 mini", "wemos", "wemos d1", "esp8266 mini"],
        "description": "Thumb-sized ESP8266 board with a stackable shield ecosystem — "
        "the smallest sensible Wi-Fi node for a permanent install.",
        "package": "Board",
        "tags": ["board", "wifi", "iot", "compact"],
        "pins": [
            {"number": 1, "name": "3V3", "type": "power", "description": "3.3V out"},
            {"number": 2, "name": "5V", "type": "power", "description": "USB input"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "D1/D2", "type": "i2c", "description": "SCL / SDA"},
            {"number": 5, "name": "A0", "type": "analog", "description": "0-3.2V via the on-board divider"},
        ],
        "wiring": {
            "esp8266": {
                "connections": [
                    {"from_pin": "3V3", "to_pin": "Sensor VCC", "note": ""},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": ""},
                ],
                "notes": ["Shields stack: relay, OLED, battery and DHT boards all exist."],
            },
        },
        "code": {},
    },
    {
        "id": "rpi_pico_w",
        "type": "board",
        "name": "Raspberry Pi Pico W",
        "aliases": ["pico w", "raspberry pi pico", "rp2040", "pico"],
        "description": "RP2040 dual-core board with Wi-Fi, programmable I/O state "
        "machines, and a choice of MicroPython or C/C++.",
        "package": "Board",
        "tags": ["board", "wifi", "iot", "micropython"],
        "pins": [
            {"number": 1, "name": "3V3(OUT)", "type": "power", "description": "3.3V out, 300mA"},
            {"number": 2, "name": "VSYS", "type": "power", "description": "1.8-5.5V input"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground (eight pins)"},
            {"number": 4, "name": "GP0-GP28", "type": "digital", "description": "26 GPIOs, 3.3V logic"},
            {"number": 5, "name": "GP26-GP28", "type": "analog", "description": "12-bit ADC inputs"},
            {"number": 6, "name": "GP4/GP5", "type": "i2c", "description": "Common I2C0 pins"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "3V3(OUT)", "to_pin": "Sensor VCC", "note": ""},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": ""},
                    {"from_pin": "GP4/GP5", "to_pin": "I2C bus", "note": "SDA / SCL"},
                ],
                "notes": [
                    "Hold BOOTSEL while plugging in USB to get a drag-and-drop drive.",
                    "The PIO blocks can bit-bang WS2812, DVI or custom protocols in hardware.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "raspberry_pi",
        "type": "board",
        "name": "Raspberry Pi (4 / Zero 2 W)",
        "aliases": ["raspberry pi", "rpi", "pi 4", "pi zero", "raspberry pi 4"],
        "description": "A full Linux computer with a 40-pin GPIO header — the natural "
        "gateway or hub for an IoT project (databases, dashboards, cameras).",
        "package": "Single-board computer",
        "tags": ["board", "linux", "iot", "gateway"],
        "pins": [
            {"number": 1, "name": "3V3", "type": "power", "description": "Pins 1 and 17, ~50mA each"},
            {"number": 2, "name": "5V", "type": "power", "description": "Pins 2 and 4, straight from the supply"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Pins 6, 9, 14, 20, 25, 30, 34, 39"},
            {"number": 4, "name": "GPIO2/3", "type": "i2c", "description": "SDA / SCL (pins 3 and 5)"},
            {"number": 5, "name": "GPIO14/15", "type": "uart", "description": "TXD / RXD (pins 8 and 10)"},
            {"number": 6, "name": "GPIO10/9/11", "type": "spi", "description": "MOSI / MISO / SCLK"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "3V3", "to_pin": "Sensor VCC", "note": "GPIO is 3.3V and NOT 5V tolerant"},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": ""},
                    {"from_pin": "GPIO2/3", "to_pin": "I2C bus", "note": "Pull-ups are already on the board"},
                ],
                "notes": [
                    "There is no ADC — add an MCP3008 or ADS1115 for analog sensors.",
                    "Enable I2C/SPI with raspi-config before anything appears in /dev.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "stm32_bluepill",
        "type": "board",
        "name": "STM32 Blue Pill",
        "aliases": ["blue pill", "stm32f103", "stm32 board", "bluepill"],
        "description": "72MHz Cortex-M3 with real 12-bit ADCs, plenty of timers and a "
        "USB peripheral — a big step up from AVR for the same money.",
        "package": "Board",
        "tags": ["board", "arm", "advanced"],
        "pins": [
            {"number": 1, "name": "3.3V", "type": "power", "description": "3.3V rail"},
            {"number": 2, "name": "5V", "type": "power", "description": "USB / regulator input"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "PB6/PB7", "type": "i2c", "description": "I2C1 SCL / SDA"},
            {"number": 5, "name": "PA0-PA7", "type": "analog", "description": "12-bit ADC inputs"},
            {"number": 6, "name": "BOOT0", "type": "digital", "description": "Set high to flash over serial"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "3.3V", "to_pin": "Sensor VCC", "note": "5V-tolerant on many pins, but not all"},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": ""},
                ],
                "notes": ["Most clones need an ST-Link or a USB bootloader flashed once."],
            },
        },
        "code": {},
    },
    {
        "id": "attiny85",
        "type": "board",
        "name": "ATtiny85",
        "aliases": ["attiny85", "attiny", "digispark"],
        "description": "Eight pins, 8KB flash, five usable I/Os. When a project needs "
        "one blinking LED and a coin cell, an Uno is overkill.",
        "package": "DIP-8 / Digispark board",
        "tags": ["board", "avr", "compact"],
        "pins": [
            {"number": 1, "name": "PB5/RESET", "type": "digital", "description": "Reset (usable as I/O only with a fuse change)"},
            {"number": 2, "name": "PB3", "type": "analog", "description": "ADC3"},
            {"number": 3, "name": "PB4", "type": "analog", "description": "ADC2"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 5, "name": "PB0", "type": "pwm", "description": "PWM / MOSI / SDA"},
            {"number": 6, "name": "PB1", "type": "pwm", "description": "PWM / MISO"},
            {"number": 7, "name": "PB2", "type": "digital", "description": "SCK / SCL / INT0"},
            {"number": 8, "name": "VCC", "type": "power", "description": "2.7-5.5V"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "100nF decoupling"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "PB0", "to_pin": "D11", "note": "MOSI, when programming via an Uno as ISP"},
                    {"from_pin": "PB1", "to_pin": "D12", "note": "MISO"},
                    {"from_pin": "PB2", "to_pin": "D13", "note": "SCK"},
                    {"from_pin": "PB5/RESET", "to_pin": "D10", "note": "Reset line for ISP"},
                ],
                "notes": ["Use the 'Arduino as ISP' sketch to flash it from an Uno."],
            },
        },
        "code": {},
    },
    {
        "id": "xiao_esp32c3",
        "type": "board",
        "name": "Seeed XIAO ESP32-C3",
        "aliases": ["xiao esp32c3", "xiao", "esp32-c3", "seeed xiao"],
        "description": "Thumbnail-sized RISC-V board with Wi-Fi, BLE and a battery "
        "connector — wearables and tiny always-on sensors.",
        "package": "Board (21x17mm)",
        "tags": ["board", "wifi", "iot", "compact"],
        "pins": [
            {"number": 1, "name": "3V3", "type": "power", "description": "3.3V out"},
            {"number": 2, "name": "5V", "type": "power", "description": "USB-C input"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "D4/D5", "type": "i2c", "description": "SDA / SCL"},
            {"number": 5, "name": "BAT+/-", "type": "power", "description": "LiPo pads with on-board charging"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "3V3", "to_pin": "Sensor VCC", "note": ""},
                    {"from_pin": "GND", "to_pin": "Sensor GND", "note": ""},
                    {"from_pin": "D4/D5", "to_pin": "I2C bus", "note": ""},
                ],
                "notes": ["Deep sleep plus a 400mAh cell runs for weeks."],
            },
        },
        "code": {},
    },
]
