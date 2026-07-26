"""Displays: OLED, LCD, TFT, e-paper, LED matrices and digit drivers."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "lcd1602_i2c",
        "type": "display",
        "name": "16x2 LCD with I2C Backpack",
        "aliases": ["lcd1602", "16x2 lcd", "i2c lcd", "hd44780", "lcd display"],
        "description": "The classic character LCD with a PCF8574 backpack, so it needs "
        "only two wires instead of six. Readable in bright sunlight.",
        "package": "16x2 module",
        "tags": ["display", "i2c", "beginner"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 2, "name": "VCC", "type": "power", "description": "5V (dim at 3.3V)"},
            {"number": 3, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 4, "name": "SCL", "type": "i2c", "description": "I2C clock"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "A4", "note": ""},
                    {"from_pin": "SCL", "to_pin": "A5", "note": ""},
                ],
                "notes": [
                    "Address is 0x27 or 0x3F — run an I2C scanner if the screen stays blank.",
                    "The pot on the back sets contrast; a blank screen is usually that.",
                ],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": "5V for a readable display"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": "3.3V I2C works with 5V backpacks"},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Print two lines on an I2C LCD",
                "libraries": ["LiquidCrystal_I2C"],
                "code": """#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);   // try 0x3F if nothing shows

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("AI Electronics");
  lcd.setCursor(0, 1);
  lcd.print("Scanner ready");
}

void loop() {
  lcd.setCursor(13, 1);
  lcd.print(millis() / 1000 % 1000);
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "lcd2004",
        "type": "display",
        "name": "20x4 Character LCD",
        "aliases": ["lcd2004", "20x4 lcd", "2004a lcd"],
        "description": "Bigger sibling of the 16x2 — four lines of twenty characters, "
        "handy for menus and dashboards. Same HD44780 driver.",
        "package": "20x4 module",
        "tags": ["display", "i2c"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 2, "name": "VCC", "type": "power", "description": "5V"},
            {"number": 3, "name": "SDA", "type": "i2c", "description": "I2C data (with backpack)"},
            {"number": 4, "name": "SCL", "type": "i2c", "description": "I2C clock"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "A4", "note": ""},
                    {"from_pin": "SCL", "to_pin": "A5", "note": ""},
                ],
                "notes": ["Same library as the 16x2 — just construct it as (addr, 20, 4)."],
            },
        },
        "code": {},
    },
    {
        "id": "sh1106",
        "type": "display",
        "name": "SH1106 1.3\" OLED",
        "aliases": ["sh1106", "1.3 oled", "oled 1.3 inch"],
        "description": "1.3\" I2C OLED that looks like an SSD1306 but has a slightly "
        "different memory layout — using the wrong driver shifts the image sideways.",
        "package": "Module",
        "tags": ["display", "i2c"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 2, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                ],
                "notes": ["If your text is offset by 2 pixels, you have an SH1106, not an SSD1306."],
            },
        },
        "code": {
            "esp32": {
                "title": "Draw on an SH1106 with U8g2",
                "libraries": ["U8g2"],
                "code": """#include <U8g2lib.h>

U8G2_SH1106_128X64_NONAME_F_HW_I2C display(U8G2_R0);

void setup() {
  display.begin();
}

void loop() {
  display.clearBuffer();
  display.setFont(u8g2_font_ncenB10_tr);
  display.drawStr(0, 20, "Uptime");
  display.setFont(u8g2_font_ncenB14_tr);
  display.setCursor(0, 48);
  display.print(millis() / 1000);
  display.print(" s");
  display.sendBuffer();
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "st7735",
        "type": "display",
        "name": "ST7735 1.8\" TFT Display",
        "aliases": ["st7735", "1.8 tft", "tft display", "spi tft"],
        "description": "128x160 colour TFT over SPI — graphs, icons and colour UI on a "
        "budget. Fast enough for simple animation.",
        "package": "Module",
        "tags": ["display", "spi", "color"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V (module regulated)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "spi", "description": "SPI clock"},
            {"number": 4, "name": "SDA", "type": "spi", "description": "SPI MOSI"},
            {"number": 5, "name": "RES", "type": "digital", "description": "Reset"},
            {"number": 6, "name": "DC", "type": "digital", "description": "Data/command select"},
            {"number": 7, "name": "CS", "type": "spi", "description": "Chip select"},
            {"number": 8, "name": "BLK", "type": "power", "description": "Backlight (PWM to dim)"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO18", "note": "SPI clock"},
                    {"from_pin": "SDA", "to_pin": "GPIO23", "note": "MOSI"},
                    {"from_pin": "CS", "to_pin": "GPIO5", "note": ""},
                    {"from_pin": "DC", "to_pin": "GPIO2", "note": ""},
                    {"from_pin": "RES", "to_pin": "GPIO4", "note": ""},
                ],
                "notes": ["Red-tab and black-tab panels need different init — swap if colours invert."],
            },
        },
        "code": {
            "esp32": {
                "title": "Colour text and shapes",
                "libraries": ["Adafruit ST7735", "Adafruit GFX"],
                "code": """#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>

#define TFT_CS 5
#define TFT_DC 2
#define TFT_RST 4

Adafruit_ST7735 tft(TFT_CS, TFT_DC, TFT_RST);

void setup() {
  tft.initR(INITR_BLACKTAB);
  tft.setRotation(1);
  tft.fillScreen(ST77XX_BLACK);
  tft.setTextColor(ST77XX_GREEN);
  tft.setTextSize(2);
  tft.setCursor(6, 10);
  tft.print("Sensors");
  tft.drawFastHLine(0, 34, tft.width(), ST77XX_GREEN);
}

void loop() {
  tft.fillRect(6, 50, 140, 20, ST77XX_BLACK);
  tft.setCursor(6, 50);
  tft.setTextColor(ST77XX_WHITE);
  tft.print(millis() / 1000);
  tft.print(" s");
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "ili9341",
        "type": "display",
        "name": "ILI9341 2.8\" TFT Touchscreen",
        "aliases": ["ili9341", "2.8 tft", "touch screen", "tft touch"],
        "description": "320x240 colour TFT, usually with a resistive touch controller "
        "on the same board — the classic DIY control-panel display.",
        "package": "Module / shield",
        "tags": ["display", "spi", "touch"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "CS", "type": "spi", "description": "Display chip select"},
            {"number": 4, "name": "RESET", "type": "digital", "description": "Reset"},
            {"number": 5, "name": "DC", "type": "digital", "description": "Data/command"},
            {"number": 6, "name": "SDI", "type": "spi", "description": "MOSI"},
            {"number": 7, "name": "SCK", "type": "spi", "description": "Clock"},
            {"number": 8, "name": "T_CS", "type": "spi", "description": "Touch controller chip select"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SCK", "to_pin": "GPIO18", "note": ""},
                    {"from_pin": "SDI", "to_pin": "GPIO23", "note": ""},
                    {"from_pin": "CS", "to_pin": "GPIO15", "note": ""},
                    {"from_pin": "DC", "to_pin": "GPIO2", "note": ""},
                    {"from_pin": "T_CS", "to_pin": "GPIO14", "note": "Touch shares the SPI bus"},
                ],
                "notes": ["TFT_eSPI is much faster than Adafruit_GFX on an ESP32."],
            },
        },
        "code": {},
    },
    {
        "id": "nokia5110",
        "type": "display",
        "name": "Nokia 5110 LCD (PCD8544)",
        "aliases": ["nokia 5110", "pcd8544", "5110 lcd"],
        "description": "84x48 monochrome graphic LCD from the phone era: cheap, "
        "readable, and it sips power — good for battery gadgets.",
        "package": "Module",
        "tags": ["display", "spi", "lowpower"],
        "pins": [
            {"number": 1, "name": "RST", "type": "digital", "description": "Reset"},
            {"number": 2, "name": "CE", "type": "spi", "description": "Chip enable"},
            {"number": 3, "name": "DC", "type": "digital", "description": "Data/command"},
            {"number": 4, "name": "DIN", "type": "spi", "description": "Data in (MOSI)"},
            {"number": 5, "name": "CLK", "type": "spi", "description": "Clock"},
            {"number": 6, "name": "VCC", "type": "power", "description": "3.3V"},
            {"number": 7, "name": "BL", "type": "power", "description": "Backlight"},
            {"number": 8, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3.3V", "note": "5V damages the panel"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "CLK", "to_pin": "D3", "note": "Through 10kΩ (5V logic)"},
                    {"from_pin": "DIN", "to_pin": "D4", "note": "Through 10kΩ"},
                    {"from_pin": "DC", "to_pin": "D5", "note": "Through 10kΩ"},
                    {"from_pin": "CE", "to_pin": "D6", "note": "Through 10kΩ"},
                    {"from_pin": "RST", "to_pin": "D7", "note": "Through 10kΩ"},
                ],
                "notes": ["All signals are 3.3V — series resistors or a level shifter are required."],
            },
        },
        "code": {},
    },
    {
        "id": "max7219_matrix",
        "type": "display",
        "name": "MAX7219 8x8 LED Matrix",
        "aliases": ["max7219", "led matrix", "dot matrix display", "fc-16"],
        "description": "Driver chip plus 8x8 LED matrix, chainable into a scrolling "
        "message board. Three wires drive any number of modules.",
        "package": "Module (chainable)",
        "tags": ["display", "spi", "led"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V (each module up to ~160mA)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "DIN", "type": "spi", "description": "Data in"},
            {"number": 4, "name": "CS", "type": "spi", "description": "Load / chip select"},
            {"number": 5, "name": "CLK", "type": "spi", "description": "Clock"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "Use an external supply past 4 modules"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "DIN", "to_pin": "D11", "note": "MOSI"},
                    {"from_pin": "CS", "to_pin": "D10", "note": ""},
                    {"from_pin": "CLK", "to_pin": "D13", "note": ""},
                ],
                "notes": ["Chain modules DOUT -> DIN and tell the library how many there are."],
            },
        },
        "code": {
            "uno": {
                "title": "Scroll a message across the matrix",
                "libraries": ["MD_Parola", "MD_MAX72XX"],
                "code": """#include <MD_Parola.h>
#include <MD_MAX72xx.h>
#include <SPI.h>

#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 4
#define CS_PIN 10

MD_Parola display = MD_Parola(HARDWARE_TYPE, CS_PIN, MAX_DEVICES);

void setup() {
  display.begin();
  display.setIntensity(4);
  display.displayText("AI ELECTRONICS SCANNER", PA_CENTER, 60, 1000,
                      PA_SCROLL_LEFT, PA_SCROLL_LEFT);
}

void loop() {
  if (display.displayAnimate()) display.displayReset();
}
""",
            },
        },
    },
    {
        "id": "tm1637",
        "type": "display",
        "name": "TM1637 4-digit Display",
        "aliases": ["tm1637", "4 digit display", "seven segment module", "clock display"],
        "description": "Four 7-segment digits with a colon, driven by two wires — the "
        "quickest way to show a clock, a counter or a temperature.",
        "package": "Module",
        "tags": ["display", "beginner"],
        "pins": [
            {"number": 1, "name": "CLK", "type": "digital", "description": "Clock"},
            {"number": 2, "name": "DIO", "type": "digital", "description": "Data"},
            {"number": 3, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "CLK", "to_pin": "D2", "note": ""},
                    {"from_pin": "DIO", "to_pin": "D3", "note": ""},
                ],
                "notes": ["Not I2C despite the two wires — it uses its own protocol."],
            },
        },
        "code": {
            "uno": {
                "title": "Show a running clock",
                "libraries": ["TM1637Display"],
                "code": """#include <TM1637Display.h>

TM1637Display display(2, 3);      // CLK, DIO

void setup() {
  display.setBrightness(5);
}

void loop() {
  unsigned long secs = millis() / 1000;
  int minutes = (secs / 60) % 60;
  int seconds = secs % 60;
  display.showNumberDecEx(minutes * 100 + seconds, 0b01000000, true);
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "epaper_29",
        "type": "display",
        "name": "2.9\" E-Paper Display",
        "aliases": ["e-paper", "epaper", "e-ink", "waveshare epaper", "eink display"],
        "description": "Electronic paper that keeps its image with zero power — ideal "
        "for battery-powered signs, badges and slow dashboards.",
        "package": "Module (SPI)",
        "tags": ["display", "spi", "lowpower", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "DIN", "type": "spi", "description": "MOSI"},
            {"number": 4, "name": "CLK", "type": "spi", "description": "Clock"},
            {"number": 5, "name": "CS", "type": "spi", "description": "Chip select"},
            {"number": 6, "name": "DC", "type": "digital", "description": "Data/command"},
            {"number": 7, "name": "RST", "type": "digital", "description": "Reset"},
            {"number": 8, "name": "BUSY", "type": "digital", "description": "High while refreshing"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "DIN", "to_pin": "GPIO23", "note": ""},
                    {"from_pin": "CLK", "to_pin": "GPIO18", "note": ""},
                    {"from_pin": "CS", "to_pin": "GPIO5", "note": ""},
                    {"from_pin": "DC", "to_pin": "GPIO17", "note": ""},
                    {"from_pin": "RST", "to_pin": "GPIO16", "note": ""},
                    {"from_pin": "BUSY", "to_pin": "GPIO4", "note": ""},
                ],
                "notes": [
                    "A full refresh takes 2-15 seconds — design for occasional updates.",
                    "Never leave an image on the panel for months without refreshing it.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "led_bar_graph",
        "type": "display",
        "name": "10-segment LED Bar Graph",
        "aliases": ["led bar graph", "bar graph display", "level meter led"],
        "description": "Ten LEDs in a row for level meters and VU displays. Each "
        "segment needs its own resistor, or drive it with an LM3914.",
        "package": "DIP-20",
        "tags": ["display", "led", "beginner"],
        "pins": [
            {"number": 1, "name": "Anode 1-10", "type": "digital", "description": "One per segment"},
            {"number": 2, "name": "Cathode 1-10", "type": "ground", "description": "One per segment"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Anode 1-10", "to_pin": "D2..D11", "note": "220Ω each"},
                    {"from_pin": "Cathode 1-10", "to_pin": "GND", "note": ""},
                ],
                "notes": ["A 74HC595 saves pins if you need all ten segments."],
            },
        },
        "code": {},
    },
    {
        "id": "ssd1306",
        "type": "display",
        "name": "SSD1306 OLED Display (I2C)",
        "aliases": ["ssd1306", "oled", "oled display", "128x64 oled"],
        "description": "A 128x64 monochrome OLED display driven over I2C. Default "
        "address is 0x3C.",
        "package": "I2C module",
        "tags": ["display", "i2c"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 2, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "SCL", "to_pin": "A5", "note": "Hardware I2C SCL"},
                    {"from_pin": "SDA", "to_pin": "A4", "note": "Hardware I2C SDA"},
                ],
                "notes": [],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": "Default I2C SCL"},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": "Default I2C SDA"},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Print text on an OLED",
                "libraries": ["Adafruit SSD1306", "Adafruit GFX Library"],
                "code": """#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Hello!");
  display.display();
}

void loop() {}
""",
            },
        },
    },
]
