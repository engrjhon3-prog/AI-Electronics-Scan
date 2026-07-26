"""Connectivity for IoT: Wi-Fi, BLE, LoRa, cellular, GPS, RFID, RF, wired buses."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "esp01",
        "type": "wireless",
        "name": "ESP-01 Wi-Fi Module (ESP8266)",
        "aliases": ["esp-01", "esp01", "esp8266 module", "wifi module", "at wifi module"],
        "description": "The tiny 8-pin ESP8266 board that adds Wi-Fi to an Arduino — "
        "either through AT commands or by flashing your own firmware onto it.",
        "package": "8-pin module",
        "tags": ["wifi", "iot", "uart"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V only — 5V destroys it"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "TX", "type": "uart", "description": "Transmit (3.3V)"},
            {"number": 4, "name": "RX", "type": "uart", "description": "Receive (3.3V)"},
            {"number": 5, "name": "CH_PD", "type": "digital", "description": "Chip enable — tie to 3.3V"},
            {"number": 6, "name": "RST", "type": "digital", "description": "Reset (active low)"},
            {"number": 7, "name": "GPIO0", "type": "digital", "description": "Low at boot = flash mode"},
            {"number": 8, "name": "GPIO2", "type": "digital", "description": "Spare GPIO, must be high at boot"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "External 3.3V", "note": "Needs 300mA peaks — not the Uno's 3.3V pin"},
                    {"from_pin": "CH_PD", "to_pin": "3.3V", "note": "Required to run"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Common ground"},
                    {"from_pin": "RX", "to_pin": "D3", "note": "Through a divider — Uno TX is 5V"},
                    {"from_pin": "TX", "to_pin": "D2", "note": "Safe direct into the Uno"},
                ],
                "notes": [
                    "Brown-outs are the number one cause of 'AT works then dies' — add 470µF.",
                    "For new projects an ESP32 or NodeMCU replaces the Uno+ESP-01 pair entirely.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Talk to an ESP-01 with AT commands",
                "libraries": ["SoftwareSerial"],
                "code": """#include <SoftwareSerial.h>

SoftwareSerial esp(2, 3);      // RX = D2 (from ESP TX), TX = D3 (to ESP RX)

void send(const char* cmd, unsigned long waitMs) {
  esp.println(cmd);
  unsigned long start = millis();
  while (millis() - start < waitMs) {
    while (esp.available()) Serial.write(esp.read());
  }
}

void setup() {
  Serial.begin(9600);
  esp.begin(9600);
  send("AT", 1000);                       // expect OK
  send("AT+CWMODE=1", 1000);              // station mode
  send("AT+CWJAP=\\"your-wifi\\",\\"your-password\\"", 8000);
  send("AT+CIFSR", 2000);                 // print the IP address
}

void loop() {
  while (esp.available()) Serial.write(esp.read());
  while (Serial.available()) esp.write(Serial.read());
}
""",
            },
        },
    },
    {
        "id": "nrf24l01",
        "type": "wireless",
        "name": "nRF24L01+ 2.4GHz Transceiver",
        "aliases": ["nrf24l01", "nrf24", "2.4ghz transceiver", "rf24"],
        "description": "Cheap two-way 2.4GHz radio link between microcontrollers, up "
        "to ~100m (1km with the PA/LNA version). No Wi-Fi router needed.",
        "package": "Module (SPI)",
        "tags": ["rf", "iot", "spi", "mesh"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 2, "name": "VCC", "type": "power", "description": "3.3V only"},
            {"number": 3, "name": "CE", "type": "digital", "description": "Chip enable (RX/TX mode)"},
            {"number": 4, "name": "CSN", "type": "spi", "description": "SPI chip select"},
            {"number": 5, "name": "SCK", "type": "spi", "description": "SPI clock"},
            {"number": 6, "name": "MOSI", "type": "spi", "description": "SPI data in"},
            {"number": 7, "name": "MISO", "type": "spi", "description": "SPI data out"},
            {"number": 8, "name": "IRQ", "type": "digital", "description": "Interrupt (optional)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3.3V", "note": "10µF right at the module — this is essential"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "CE", "to_pin": "D9", "note": ""},
                    {"from_pin": "CSN", "to_pin": "D10", "note": ""},
                    {"from_pin": "SCK", "to_pin": "D13", "note": ""},
                    {"from_pin": "MOSI", "to_pin": "D11", "note": ""},
                    {"from_pin": "MISO", "to_pin": "D12", "note": ""},
                ],
                "notes": [
                    "The data pins tolerate 5V logic; VCC absolutely does not.",
                    "Flaky link? It is nearly always the missing decoupling capacitor.",
                ],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": "Add 10µF"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "CE", "to_pin": "GPIO4", "note": ""},
                    {"from_pin": "CSN", "to_pin": "GPIO5", "note": ""},
                    {"from_pin": "SCK", "to_pin": "GPIO18", "note": ""},
                    {"from_pin": "MOSI", "to_pin": "GPIO23", "note": ""},
                    {"from_pin": "MISO", "to_pin": "GPIO19", "note": ""},
                ],
                "notes": ["It shares the 2.4GHz band with Wi-Fi — pick a high channel."],
            },
        },
        "code": {
            "uno": {
                "title": "Send sensor readings to another Arduino",
                "libraries": ["RF24"],
                "code": """#include <SPI.h>
#include <RF24.h>

RF24 radio(9, 10);                    // CE, CSN
const byte ADDRESS[6] = "NODE1";

struct Packet {
  uint8_t nodeId;
  float temperature;
};

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.setPALevel(RF24_PA_LOW);      // LOW is more reliable on USB power
  radio.setChannel(108);              // above most Wi-Fi traffic
  radio.openWritingPipe(ADDRESS);
  radio.stopListening();
}

void loop() {
  Packet packet = {1, 24.6};
  bool ok = radio.write(&packet, sizeof(packet));
  Serial.println(ok ? "sent" : "no ack");
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "lora_sx1278",
        "type": "wireless",
        "name": "LoRa SX1278 / RA-02 Module",
        "aliases": ["sx1278", "ra-02", "lora module", "lora", "sx1276", "rfm95"],
        "description": "Long-range, low-power radio: kilometres of range at a few kbps. "
        "The backbone of off-grid IoT sensors and LoRaWAN nodes.",
        "package": "Module (SPI)",
        "tags": ["lora", "iot", "spi", "long-range"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V only"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCK", "type": "spi", "description": "SPI clock"},
            {"number": 4, "name": "MISO", "type": "spi", "description": "SPI data out"},
            {"number": 5, "name": "MOSI", "type": "spi", "description": "SPI data in"},
            {"number": 6, "name": "NSS", "type": "spi", "description": "Chip select"},
            {"number": 7, "name": "RST", "type": "digital", "description": "Reset"},
            {"number": 8, "name": "DIO0", "type": "digital", "description": "TX done / RX done interrupt"},
            {"number": 9, "name": "ANT", "type": "signal", "description": "Antenna — never transmit without one"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": "Peaks around 120mA while transmitting"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SCK", "to_pin": "GPIO18", "note": ""},
                    {"from_pin": "MISO", "to_pin": "GPIO19", "note": ""},
                    {"from_pin": "MOSI", "to_pin": "GPIO23", "note": ""},
                    {"from_pin": "NSS", "to_pin": "GPIO5", "note": ""},
                    {"from_pin": "RST", "to_pin": "GPIO14", "note": ""},
                    {"from_pin": "DIO0", "to_pin": "GPIO2", "note": ""},
                ],
                "notes": [
                    "Use the frequency your country allows: 433MHz, 868MHz (EU) or 915MHz (US/PH).",
                    "Transmitting without an antenna can destroy the output stage.",
                ],
            },
        },
        "code": {
            "esp32": {
                "title": "LoRa sender node",
                "libraries": ["LoRa (Sandeep Mistry)"],
                "code": """#include <SPI.h>
#include <LoRa.h>

const long FREQUENCY = 433E6;      // match your region and your receiver

void setup() {
  Serial.begin(115200);
  LoRa.setPins(5, 14, 2);          // NSS, RST, DIO0
  if (!LoRa.begin(FREQUENCY)) {
    Serial.println("LoRa init failed");
    while (1) delay(10);
  }
  LoRa.setSpreadingFactor(10);     // higher = longer range, slower
  LoRa.setTxPower(17);
}

void loop() {
  LoRa.beginPacket();
  LoRa.printf("{\\"node\\":1,\\"temp\\":%.1f}", 26.4);
  LoRa.endPacket();
  Serial.println("packet sent");
  delay(30000);                    // stay within the duty-cycle rules
}
""",
            },
        },
    },
    {
        "id": "hc12",
        "type": "wireless",
        "name": "HC-12 433MHz Serial Radio",
        "aliases": ["hc-12", "hc12", "433mhz serial", "wireless serial module"],
        "description": "Drop-in wireless replacement for a serial cable: up to ~1km, "
        "no protocol to learn — whatever goes in one side comes out the other.",
        "package": "Module",
        "tags": ["rf", "uart", "iot", "long-range"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.2-5.5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "RXD", "type": "uart", "description": "Serial in"},
            {"number": 4, "name": "TXD", "type": "uart", "description": "Serial out"},
            {"number": 5, "name": "SET", "type": "digital", "description": "Pull low for AT command mode"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "Add 100µF; TX peaks are heavy"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "RXD", "to_pin": "D3", "note": "Arduino TX"},
                    {"from_pin": "TXD", "to_pin": "D2", "note": "Arduino RX"},
                    {"from_pin": "SET", "to_pin": "D4", "note": "LOW enters AT mode"},
                ],
                "notes": ["Both ends must share channel, baud rate and transmission mode."],
            },
        },
        "code": {},
    },
    {
        "id": "hm10_ble",
        "type": "wireless",
        "name": "HM-10 Bluetooth LE Module",
        "aliases": ["hm-10", "hm10", "ble module", "cc2541", "bluetooth low energy module"],
        "description": "Bluetooth Low Energy serial bridge that pairs with modern "
        "phones (iOS included, unlike classic HC-05).",
        "package": "Module",
        "tags": ["bluetooth", "ble", "iot", "uart"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V (module regulated)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "TXD", "type": "uart", "description": "To the MCU's RX"},
            {"number": 4, "name": "RXD", "type": "uart", "description": "From the MCU's TX (3.3V!)"},
            {"number": 5, "name": "STATE", "type": "digital", "description": "High while connected"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "TXD", "to_pin": "D2", "note": "Arduino RX"},
                    {"from_pin": "RXD", "to_pin": "D3", "note": "Through a divider — the pin is 3.3V"},
                ],
                "notes": ["Default 9600 baud; rename it with AT+NAME to find it in a crowd."],
            },
        },
        "code": {},
    },
    {
        "id": "sim800l",
        "type": "wireless",
        "name": "SIM800L GSM/GPRS Module",
        "aliases": ["sim800l", "gsm module", "gprs module", "sms module", "sim900"],
        "description": "2G cellular modem for SMS, calls and GPRS data — the classic "
        "way to put a project online where there is no Wi-Fi.",
        "package": "Module",
        "tags": ["cellular", "iot", "uart", "sms"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.4-4.4V, 2A peaks — NOT 5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "TXD", "type": "uart", "description": "To the MCU's RX"},
            {"number": 4, "name": "RXD", "type": "uart", "description": "From the MCU's TX (3.3V logic)"},
            {"number": 5, "name": "RST", "type": "digital", "description": "Reset (active low)"},
            {"number": 6, "name": "NET", "type": "signal", "description": "Antenna connection"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "4V supply", "note": "Li-ion cell or a buck converter, 2A capable"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Common ground with the ESP32"},
                    {"from_pin": "TXD", "to_pin": "GPIO16", "note": "ESP32 RX2"},
                    {"from_pin": "RXD", "to_pin": "GPIO17", "note": "ESP32 TX2"},
                ],
                "notes": [
                    "Add 1000µF+ at VCC — the 2A transmit bursts brown out most supplies.",
                    "2G networks are switched off in many countries; check yours before designing it in.",
                ],
            },
        },
        "code": {
            "esp32": {
                "title": "Send an SMS alert",
                "libraries": [],
                "code": """HardwareSerial sim(2);           // RX=16, TX=17

void atCommand(const char* cmd, unsigned long waitMs) {
  sim.println(cmd);
  unsigned long start = millis();
  while (millis() - start < waitMs) {
    while (sim.available()) Serial.write(sim.read());
  }
}

void setup() {
  Serial.begin(115200);
  sim.begin(9600, SERIAL_8N1, 16, 17);
  delay(5000);                    // let it register on the network

  atCommand("AT", 1000);
  atCommand("AT+CMGF=1", 1000);   // text mode
  sim.println("AT+CMGS=\\"+639171234567\\"");
  delay(500);
  sim.print("Water tank is full.");
  sim.write(26);                  // Ctrl+Z sends the message
  delay(8000);
}

void loop() {}
""",
            },
        },
    },
    {
        "id": "sim7600",
        "type": "wireless",
        "name": "SIM7600 / A7670 4G LTE Module",
        "aliases": ["sim7600", "a7670", "4g module", "lte module", "sim7670"],
        "description": "LTE Cat-1/Cat-4 modem with TCP, HTTPS and MQTT built in — the "
        "modern replacement for 2G modules on cellular IoT nodes.",
        "package": "Module / HAT",
        "tags": ["cellular", "iot", "uart", "4g"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V, 2A peaks"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "TXD", "type": "uart", "description": "To the MCU's RX"},
            {"number": 4, "name": "RXD", "type": "uart", "description": "From the MCU's TX"},
            {"number": 5, "name": "PWRKEY", "type": "digital", "description": "Pull low ~1s to power on"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "External 5V 2A", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Common ground"},
                    {"from_pin": "TXD", "to_pin": "GPIO16", "note": ""},
                    {"from_pin": "RXD", "to_pin": "GPIO17", "note": ""},
                    {"from_pin": "PWRKEY", "to_pin": "GPIO4", "note": "Pulse low for 1s at boot"},
                ],
                "notes": ["TinyGSM drives it nicely and gives you a Client for MQTT/HTTP."],
            },
        },
        "code": {},
    },
    {
        "id": "neo6m_gps",
        "type": "wireless",
        "name": "NEO-6M GPS Module",
        "aliases": ["neo-6m", "neo6m", "gps module", "ublox gps", "neo-m8n"],
        "description": "Satellite positioning over plain serial NMEA sentences: "
        "latitude, longitude, altitude, speed and an very accurate clock.",
        "package": "Module with patch antenna",
        "tags": ["gps", "iot", "uart", "navigation"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "TX", "type": "uart", "description": "NMEA output, 9600 baud"},
            {"number": 4, "name": "RX", "type": "uart", "description": "Configuration input"},
            {"number": 5, "name": "PPS", "type": "digital", "description": "1 pulse-per-second timing output"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "TX", "to_pin": "GPIO16", "note": "ESP32 RX2"},
                    {"from_pin": "RX", "to_pin": "GPIO17", "note": "ESP32 TX2"},
                ],
                "notes": [
                    "A first fix outdoors takes 30s-2min; indoors it may never come.",
                    "The PPS output is a free microsecond-accurate time reference.",
                ],
            },
        },
        "code": {
            "esp32": {
                "title": "Print latitude, longitude and satellites",
                "libraries": ["TinyGPSPlus"],
                "code": """#include <TinyGPSPlus.h>

TinyGPSPlus gps;
HardwareSerial gpsSerial(2);      // RX=16, TX=17

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600, SERIAL_8N1, 16, 17);
}

void loop() {
  while (gpsSerial.available()) {
    if (gps.encode(gpsSerial.read()) && gps.location.isValid()) {
      Serial.printf("%.6f, %.6f  alt %.1fm  sats %d\\n",
                    gps.location.lat(), gps.location.lng(),
                    gps.altitude.meters(), gps.satellites.value());
    }
  }
}
""",
            },
        },
    },
    {
        "id": "rc522",
        "type": "wireless",
        "name": "RC522 RFID Reader",
        "aliases": ["rc522", "mfrc522", "rfid reader", "rfid module", "nfc reader 13.56"],
        "description": "13.56MHz RFID reader/writer for MIFARE cards and tags — access "
        "control, attendance logging, inventory.",
        "package": "Module (SPI)",
        "tags": ["rfid", "iot", "spi", "security"],
        "pins": [
            {"number": 1, "name": "3.3V", "type": "power", "description": "3.3V only"},
            {"number": 2, "name": "RST", "type": "digital", "description": "Reset"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "IRQ", "type": "digital", "description": "Interrupt (optional)"},
            {"number": 5, "name": "MISO", "type": "spi", "description": "SPI data out"},
            {"number": 6, "name": "MOSI", "type": "spi", "description": "SPI data in"},
            {"number": 7, "name": "SCK", "type": "spi", "description": "SPI clock"},
            {"number": 8, "name": "SDA", "type": "spi", "description": "Chip select (SS)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "3.3V", "to_pin": "3.3V", "note": "5V will kill the module"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "RST", "to_pin": "D9", "note": ""},
                    {"from_pin": "SDA", "to_pin": "D10", "note": "SS"},
                    {"from_pin": "MOSI", "to_pin": "D11", "note": ""},
                    {"from_pin": "MISO", "to_pin": "D12", "note": ""},
                    {"from_pin": "SCK", "to_pin": "D13", "note": ""},
                ],
                "notes": ["Read range is only 2-5cm — that is normal for 13.56MHz."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "3.3V", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "RST", "to_pin": "GPIO22", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": "SS"},
                    {"from_pin": "MOSI", "to_pin": "GPIO23", "note": ""},
                    {"from_pin": "MISO", "to_pin": "GPIO19", "note": ""},
                    {"from_pin": "SCK", "to_pin": "GPIO18", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Read a card UID and unlock",
                "libraries": ["MFRC522"],
                "code": """#include <SPI.h>
#include <MFRC522.h>

const int SS_PIN = 10, RST_PIN = 9, RELAY_PIN = 7;
const byte ALLOWED[4] = {0xDE, 0xAD, 0xBE, 0xEF};   // your card's UID

MFRC522 reader(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  reader.PCD_Init();
  pinMode(RELAY_PIN, OUTPUT);
  Serial.println("Present a card");
}

void loop() {
  if (!reader.PICC_IsNewCardPresent() || !reader.PICC_ReadCardSerial()) return;

  bool allowed = reader.uid.size == 4;
  for (byte i = 0; i < reader.uid.size && allowed; i++) {
    Serial.print(reader.uid.uidByte[i], HEX);
    if (reader.uid.uidByte[i] != ALLOWED[i]) allowed = false;
  }
  Serial.println(allowed ? " -> access granted" : " -> denied");

  if (allowed) {
    digitalWrite(RELAY_PIN, HIGH);
    delay(3000);
    digitalWrite(RELAY_PIN, LOW);
  }
  reader.PICC_HaltA();
}
""",
            },
        },
    },
    {
        "id": "pn532",
        "type": "wireless",
        "name": "PN532 NFC Module",
        "aliases": ["pn532", "nfc module", "nfc reader", "elechouse nfc"],
        "description": "Full NFC controller: reads cards, emulates a tag and does "
        "peer-to-peer with phones. Speaks I2C, SPI or UART via DIP switches.",
        "package": "Module",
        "tags": ["nfc", "rfid", "iot", "i2c"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SDA", "type": "i2c", "description": "I2C data (mode dependent)"},
            {"number": 4, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 5, "name": "IRQ", "type": "digital", "description": "Interrupt"},
            {"number": 6, "name": "RSTO", "type": "digital", "description": "Reset"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                    {"from_pin": "IRQ", "to_pin": "GPIO19", "note": ""},
                ],
                "notes": ["Set the on-board DIP switches to I2C before wiring it this way."],
            },
        },
        "code": {},
    },
    {
        "id": "ir_receiver",
        "type": "wireless",
        "name": "VS1838B IR Receiver",
        "aliases": ["vs1838b", "ir receiver", "tsop38238", "infrared receiver", "ky-022"],
        "description": "Demodulates 38kHz infrared remote signals into clean logic "
        "pulses — decode any TV remote and use it as your project's input.",
        "package": "3-pin THT",
        "tags": ["ir", "input", "beginner"],
        "pins": [
            {"number": 1, "name": "OUT", "type": "digital", "description": "Demodulated data (idles high)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "VCC", "type": "power", "description": "2.7-5.5V"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "100nF decoupling helps"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "D2", "note": ""},
                ],
                "notes": ["Pin order varies by manufacturer — check before powering it."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "GPIO15", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Decode remote-control buttons",
                "libraries": ["IRremote"],
                "code": """#include <IRremote.hpp>

const int IR_PIN = 2;

void setup() {
  Serial.begin(9600);
  IrReceiver.begin(IR_PIN, ENABLE_LED_FEEDBACK);
  Serial.println("Point a remote at the receiver and press a button");
}

void loop() {
  if (IrReceiver.decode()) {
    Serial.print("protocol=");
    Serial.print(getProtocolString(IrReceiver.decodedIRData.protocol));
    Serial.print("  command=0x");
    Serial.println(IrReceiver.decodedIRData.command, HEX);
    IrReceiver.resume();
  }
}
""",
            },
        },
    },
    {
        "id": "rf433_pair",
        "type": "wireless",
        "name": "433MHz RF Transmitter / Receiver Pair",
        "aliases": ["433mhz", "rf transmitter", "fs1000a", "xy-mk-5v", "rf receiver"],
        "description": "The cheapest wireless link there is: one-way ASK modules for "
        "remote switches and simple telemetry, ~50-100m outdoors.",
        "package": "Module pair",
        "tags": ["rf", "iot", "budget"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "TX 3-12V (more volts = more range), RX 5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "DATA", "type": "digital", "description": "Data in (TX) / out (RX)"},
            {"number": 4, "name": "ANT", "type": "signal", "description": "17.3cm wire antenna for 433MHz"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "12V on the transmitter greatly improves range"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "DATA", "to_pin": "D12", "note": "TX side (RadioHead default)"},
                ],
                "notes": [
                    "Solder a 17.3cm straight wire as the antenna — it is worth 3x the range.",
                    "No error checking in the hardware: use RadioHead or RCSwitch.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Send a message over 433MHz",
                "libraries": ["RadioHead"],
                "code": """#include <RH_ASK.h>
#include <SPI.h>            // required by RadioHead even when unused

RH_ASK driver(2000, 11, 12);   // speed, RX pin, TX pin

void setup() {
  Serial.begin(9600);
  if (!driver.init()) Serial.println("RF init failed");
}

void loop() {
  const char* message = "GATE:OPEN";
  driver.send((uint8_t*)message, strlen(message));
  driver.waitPacketSent();
  Serial.println("sent");
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "w5500_ethernet",
        "type": "wireless",
        "name": "W5500 Ethernet Module",
        "aliases": ["w5500", "ethernet module", "enc28j60", "wiznet"],
        "description": "Hardwired TCP/IP over SPI — wired Ethernet for projects where "
        "Wi-Fi is not allowed or not reliable enough.",
        "package": "Module (SPI)",
        "tags": ["ethernet", "iot", "spi", "network"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V (module often accepts 5V)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCK", "type": "spi", "description": "SPI clock"},
            {"number": 4, "name": "MISO", "type": "spi", "description": "SPI data out"},
            {"number": 5, "name": "MOSI", "type": "spi", "description": "SPI data in"},
            {"number": 6, "name": "SCS", "type": "spi", "description": "Chip select"},
            {"number": 7, "name": "RST", "type": "digital", "description": "Reset"},
            {"number": 8, "name": "INT", "type": "digital", "description": "Interrupt"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": "Draws ~150mA"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SCK", "to_pin": "GPIO18", "note": ""},
                    {"from_pin": "MISO", "to_pin": "GPIO19", "note": ""},
                    {"from_pin": "MOSI", "to_pin": "GPIO23", "note": ""},
                    {"from_pin": "SCS", "to_pin": "GPIO5", "note": ""},
                ],
                "notes": ["The W5500 offloads the whole TCP stack — far lighter than ENC28J60."],
            },
        },
        "code": {},
    },
    {
        "id": "max485",
        "type": "wireless",
        "name": "MAX485 RS-485 Transceiver",
        "aliases": ["max485", "rs485 module", "rs-485", "modbus module"],
        "description": "Differential serial that survives 1km of noisy cable — the "
        "industrial bus behind Modbus RTU sensors and inverters.",
        "package": "Module / DIP-8",
        "tags": ["industrial", "uart", "iot", "modbus"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V (3.3V variants exist)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "DI", "type": "uart", "description": "Driver input — from the MCU's TX"},
            {"number": 4, "name": "RO", "type": "uart", "description": "Receiver output — to the MCU's RX"},
            {"number": 5, "name": "DE/RE", "type": "digital", "description": "Direction control (tie together)"},
            {"number": 6, "name": "A", "type": "signal", "description": "Bus line A (non-inverting)"},
            {"number": 7, "name": "B", "type": "signal", "description": "Bus line B (inverting)"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": "Use a 3.3V transceiver (MAX3485) with an ESP32"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "DI", "to_pin": "GPIO17", "note": "ESP32 TX2"},
                    {"from_pin": "RO", "to_pin": "GPIO16", "note": "ESP32 RX2"},
                    {"from_pin": "DE/RE", "to_pin": "GPIO4", "note": "HIGH to transmit, LOW to receive"},
                    {"from_pin": "A", "to_pin": "Bus A", "note": "120Ω terminator at each end of the run"},
                    {"from_pin": "B", "to_pin": "Bus B", "note": ""},
                ],
                "notes": ["Run a ground wire with A and B — 'two wires' is a myth in practice."],
            },
        },
        "code": {},
    },
    {
        "id": "mcp2515",
        "type": "wireless",
        "name": "MCP2515 CAN Bus Module",
        "aliases": ["mcp2515", "can bus module", "can transceiver", "tja1050"],
        "description": "CAN controller plus transceiver over SPI — read your car's OBD "
        "network or wire a robust multi-node bus in a machine.",
        "package": "Module (SPI)",
        "tags": ["automotive", "spi", "iot", "industrial"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V (logic is 5V on most boards)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "CS", "type": "spi", "description": "Chip select"},
            {"number": 4, "name": "SO", "type": "spi", "description": "SPI data out (MISO)"},
            {"number": 5, "name": "SI", "type": "spi", "description": "SPI data in (MOSI)"},
            {"number": 6, "name": "SCK", "type": "spi", "description": "SPI clock"},
            {"number": 7, "name": "INT", "type": "digital", "description": "Message received interrupt"},
            {"number": 8, "name": "CANH/CANL", "type": "signal", "description": "CAN bus pair"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "CS", "to_pin": "D10", "note": ""},
                    {"from_pin": "SI", "to_pin": "D11", "note": ""},
                    {"from_pin": "SO", "to_pin": "D12", "note": ""},
                    {"from_pin": "SCK", "to_pin": "D13", "note": ""},
                    {"from_pin": "INT", "to_pin": "D2", "note": ""},
                ],
                "notes": [
                    "Check the crystal: 8MHz and 16MHz boards need different init values.",
                    "Only the two ends of the bus carry a 120Ω terminator.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Read CAN frames at 500 kbps",
                "libraries": ["mcp_can"],
                "code": """#include <SPI.h>
#include <mcp_can.h>

MCP_CAN can(10);                 // CS pin

void setup() {
  Serial.begin(115200);
  // Use MCP_8MHZ if your board has an 8MHz crystal.
  while (can.begin(MCP_ANY, CAN_500KBPS, MCP_16MHZ) != CAN_OK) {
    Serial.println("CAN init failed");
    delay(500);
  }
  can.setMode(MCP_NORMAL);
}

void loop() {
  if (can.checkReceive() != CAN_MSGAVAIL) return;

  unsigned long id;
  byte len, buf[8];
  can.readMsgBuf(&id, &len, buf);
  Serial.print("ID 0x"); Serial.print(id, HEX); Serial.print(":");
  for (byte i = 0; i < len; i++) {
    Serial.print(' ');
    Serial.print(buf[i], HEX);
  }
  Serial.println();
}
""",
            },
        },
    },
    {
        "id": "esp32cam",
        "type": "wireless",
        "name": "ESP32-CAM Camera Module",
        "aliases": ["esp32-cam", "esp32cam", "ov2640 camera", "wifi camera module"],
        "description": "ESP32 with an OV2640 camera and a microSD slot — a complete "
        "Wi-Fi camera, video doorbell or AI-vision node for a few dollars.",
        "package": "Module",
        "tags": ["wifi", "camera", "iot", "ai"],
        "pins": [
            {"number": 1, "name": "5V", "type": "power", "description": "5V in, 500mA+ (Wi-Fi bursts)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "U0T", "type": "uart", "description": "Serial TX (flashing)"},
            {"number": 4, "name": "U0R", "type": "uart", "description": "Serial RX (flashing)"},
            {"number": 5, "name": "GPIO0", "type": "digital", "description": "Tie to GND to flash"},
            {"number": 6, "name": "GPIO4", "type": "digital", "description": "On-board flash LED"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "5V", "to_pin": "5V supply", "note": "A weak supply causes brownout reboots"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "U0T", "to_pin": "USB-TTL RX", "note": "For flashing"},
                    {"from_pin": "U0R", "to_pin": "USB-TTL TX", "note": "For flashing"},
                    {"from_pin": "GPIO0", "to_pin": "GND", "note": "Only while flashing, then remove"},
                ],
                "notes": [
                    "There is no USB port — you need a USB-to-serial adapter.",
                    "The microSD uses most of the free GPIOs; plan your extra hardware around it.",
                ],
            },
        },
        "code": {
            "esp32": {
                "title": "Wi-Fi camera web server",
                "libraries": ["esp32-camera (bundled with the ESP32 core)"],
                "code": """// Arduino IDE: Board = "AI Thinker ESP32-CAM", then open
// File > Examples > ESP32 > Camera > CameraWebServer and set your Wi-Fi.
#include <WiFi.h>
#include "esp_camera.h"

const char* WIFI_SSID = "your-wifi";
const char* WIFI_PASS = "your-password";

void startCameraServer();        // provided by the CameraWebServer example

void setup() {
  Serial.begin(115200);
  // camera_config_t for AI-Thinker boards comes from the example's
  // camera_pins.h — keep those pin definitions.
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) delay(400);
  startCameraServer();
  Serial.print("Stream ready at http://");
  Serial.println(WiFi.localIP());
}

void loop() {
  delay(10000);
}
""",
            },
        },
    },
    {
        "id": "hc05",
        "type": "wireless",
        "name": "HC-05 Bluetooth Module",
        "aliases": ["hc-05", "hc05", "bluetooth module"],
        "description": "A Bluetooth SPP (serial) module. Communicates over UART. The RX "
        "pin is 3.3V — use a divider from the board's TX.",
        "package": "6-pin module",
        "tags": ["module", "bluetooth", "uart"],
        "pins": [
            {"number": 1, "name": "EN/KEY", "type": "digital", "description": "AT mode enable"},
            {"number": 2, "name": "VCC", "type": "power", "description": "3.6-6V"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 4, "name": "TXD", "type": "uart", "description": "Module transmit (to board RX)"},
            {"number": 5, "name": "RXD", "type": "uart", "description": "Module receive (3.3V!)"},
            {"number": 6, "name": "STATE", "type": "digital", "description": "Connection state"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "TXD", "to_pin": "D10", "note": "SoftwareSerial RX"},
                    {"from_pin": "RXD", "to_pin": "D11", "note": "Via 1k/2k divider (3.3V)"},
                ],
                "notes": ["The module RXD is 3.3V — never drive it with raw 5V."],
            },
        },
        "code": {
            "uno": {
                "title": "Bluetooth serial bridge (HC-05)",
                "libraries": ["SoftwareSerial (built-in)"],
                "code": """#include <SoftwareSerial.h>

SoftwareSerial bt(10, 11); // RX, TX

void setup() {
  Serial.begin(9600);
  bt.begin(9600);
}

void loop() {
  if (bt.available()) Serial.write(bt.read());
  if (Serial.available()) bt.write(Serial.read());
}
""",
            },
        },
    },
]
