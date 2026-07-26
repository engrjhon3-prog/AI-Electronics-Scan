"""Integrated circuits: timers, op-amps, expanders, converters, drivers."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "ne555",
        "type": "ic",
        "name": "NE555 Timer",
        "aliases": ["555", "ne555", "555 timer", "timer ic"],
        "description": "The classic 8-pin timer IC, used for astable oscillators, "
        "monostable one-shots, and PWM.",
        "package": "DIP-8",
        "datasheet_url": "https://www.ti.com/lit/ds/symlink/ne555.pdf",
        "tags": ["analog", "timer"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 2, "name": "TRIG", "type": "signal", "description": "Trigger (< 1/3 Vcc starts pulse)"},
            {"number": 3, "name": "OUT", "type": "signal", "description": "Output"},
            {"number": 4, "name": "RESET", "type": "signal", "description": "Active-low reset, tie to Vcc"},
            {"number": 5, "name": "CTRL", "type": "analog", "description": "Control voltage, 10nF to GND"},
            {"number": 6, "name": "THRES", "type": "signal", "description": "Threshold (> 2/3 Vcc ends pulse)"},
            {"number": 7, "name": "DISCH", "type": "signal", "description": "Discharge"},
            {"number": 8, "name": "VCC", "type": "power", "description": "4.5-15V supply"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "RESET", "to_pin": "5V", "note": "Tie high to enable"},
                    {"from_pin": "OUT", "to_pin": "D2", "note": "Read the oscillator output"},
                    {"from_pin": "CTRL", "to_pin": "GND", "note": "Via 10nF capacitor"},
                ],
                "notes": [
                    "Astable: R1 from VCC->DISCH, R2 from DISCH->THRES(=TRIG), C from THRES->GND.",
                    "Frequency = 1.44 / ((R1 + 2*R2) * C).",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Measure 555 output frequency",
                "libraries": [],
                "code": """const int SIGNAL_PIN = 2;

void setup() {
  pinMode(SIGNAL_PIN, INPUT);
  Serial.begin(9600);
}

void loop() {
  unsigned long highTime = pulseIn(SIGNAL_PIN, HIGH);
  unsigned long lowTime  = pulseIn(SIGNAL_PIN, LOW);
  unsigned long period = highTime + lowTime;
  if (period > 0) {
    float freq = 1000000.0 / period;   // Hz
    Serial.print("Frequency: ");
    Serial.print(freq);
    Serial.println(" Hz");
  }
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "lm358",
        "type": "ic",
        "name": "LM358 Dual Op-Amp",
        "aliases": ["lm358", "op amp", "operational amplifier", "lm324"],
        "description": "Two general-purpose op-amps that work from a single supply — "
        "buffering sensors, amplifying small signals, building comparators.",
        "package": "DIP-8",
        "datasheet_url": "https://www.ti.com/lit/ds/symlink/lm358.pdf",
        "tags": ["analog", "amplifier"],
        "pins": [
            {"number": 1, "name": "OUT1", "type": "analog", "description": "Amplifier 1 output"},
            {"number": 2, "name": "IN1-", "type": "analog", "description": "Inverting input 1"},
            {"number": 3, "name": "IN1+", "type": "analog", "description": "Non-inverting input 1"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground / V-"},
            {"number": 5, "name": "IN2+", "type": "analog", "description": "Non-inverting input 2"},
            {"number": 6, "name": "IN2-", "type": "analog", "description": "Inverting input 2"},
            {"number": 7, "name": "OUT2", "type": "analog", "description": "Amplifier 2 output"},
            {"number": 8, "name": "VCC", "type": "power", "description": "3-32V supply"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "100nF decoupling to GND"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "IN1+", "to_pin": "Sensor out", "note": "High-impedance input"},
                    {"from_pin": "IN1-", "to_pin": "OUT1", "note": "Unity-gain buffer"},
                    {"from_pin": "OUT1", "to_pin": "A0", "note": "Buffered signal to the ADC"},
                ],
                "notes": ["Output cannot reach the supply rail — leave ~1.5V headroom."],
            },
        },
        "code": {
            "uno": {
                "title": "Read a buffered analog sensor",
                "libraries": [],
                "code": """const int SENSOR_PIN = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int raw = analogRead(SENSOR_PIN);
  float volts = raw * 5.0 / 1023.0;
  Serial.print(volts, 3);
  Serial.println(" V");
  delay(200);
}
""",
            },
        },
    },
    {
        "id": "lm393",
        "type": "ic",
        "name": "LM393 Dual Comparator",
        "aliases": ["lm393", "comparator", "lm339"],
        "description": "Compares two voltages and swings its open-collector output. "
        "The chip on the back of most cheap sensor modules with a trim pot.",
        "package": "DIP-8 / SOIC-8",
        "tags": ["analog", "comparator"],
        "pins": [
            {"number": 1, "name": "OUT1", "type": "digital", "description": "Open-collector output 1"},
            {"number": 2, "name": "IN1-", "type": "analog", "description": "Inverting input 1"},
            {"number": 3, "name": "IN1+", "type": "analog", "description": "Non-inverting input 1"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 5, "name": "IN2+", "type": "analog", "description": "Non-inverting input 2"},
            {"number": 6, "name": "IN2-", "type": "analog", "description": "Inverting input 2"},
            {"number": 7, "name": "OUT2", "type": "digital", "description": "Open-collector output 2"},
            {"number": 8, "name": "VCC", "type": "power", "description": "2-36V supply"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "IN1+", "to_pin": "Sensor", "note": ""},
                    {"from_pin": "IN1-", "to_pin": "Trim pot wiper", "note": "Threshold"},
                    {"from_pin": "OUT1", "to_pin": "D2", "note": "Needs a 10kΩ pull-up to 5V"},
                ],
                "notes": ["Open-collector: it can only pull low, so a pull-up is mandatory."],
            },
        },
        "code": {},
    },
    {
        "id": "hc595",
        "type": "ic",
        "name": "74HC595 Shift Register",
        "aliases": ["74hc595", "hc595", "shift register", "595"],
        "description": "Turns three pins into eight outputs, and chains for more. The "
        "classic fix when you run out of pins driving LEDs or a display.",
        "package": "DIP-16 / SOIC-16",
        "datasheet_url": "https://www.ti.com/lit/ds/symlink/sn74hc595.pdf",
        "tags": ["expander", "digital"],
        "pins": [
            {"number": 1, "name": "Q1", "type": "digital", "description": "Output 1"},
            {"number": 8, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 9, "name": "Q7S", "type": "digital", "description": "Serial out, to the next chip's DS"},
            {"number": 10, "name": "MR", "type": "digital", "description": "Master reset, tie to VCC"},
            {"number": 11, "name": "SHCP", "type": "digital", "description": "Shift clock"},
            {"number": 12, "name": "STCP", "type": "digital", "description": "Latch clock"},
            {"number": 13, "name": "OE", "type": "digital", "description": "Output enable, tie to GND"},
            {"number": 14, "name": "DS", "type": "digital", "description": "Serial data in"},
            {"number": 15, "name": "Q0", "type": "digital", "description": "Output 0"},
            {"number": 16, "name": "VCC", "type": "power", "description": "2-6V supply"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "100nF decoupling"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "DS", "to_pin": "D11", "note": "Data"},
                    {"from_pin": "SHCP", "to_pin": "D13", "note": "Clock"},
                    {"from_pin": "STCP", "to_pin": "D10", "note": "Latch"},
                    {"from_pin": "OE", "to_pin": "GND", "note": "Outputs always enabled"},
                    {"from_pin": "MR", "to_pin": "5V", "note": "No reset"},
                ],
                "notes": ["Each output still needs its own resistor when driving LEDs."],
            },
        },
        "code": {
            "uno": {
                "title": "Run a chase across 8 outputs",
                "libraries": [],
                "code": """const int DATA_PIN = 11;   // DS
const int CLOCK_PIN = 13;  // SHCP
const int LATCH_PIN = 10;  // STCP

void writeByte(byte value) {
  digitalWrite(LATCH_PIN, LOW);
  shiftOut(DATA_PIN, CLOCK_PIN, MSBFIRST, value);
  digitalWrite(LATCH_PIN, HIGH);
}

void setup() {
  pinMode(DATA_PIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);
  pinMode(LATCH_PIN, OUTPUT);
}

void loop() {
  for (int bit = 0; bit < 8; bit++) {
    writeByte(1 << bit);
    delay(120);
  }
}
""",
            },
        },
    },
    {
        "id": "hc165",
        "type": "ic",
        "name": "74HC165 Parallel-In Shift Register",
        "aliases": ["74hc165", "hc165", "input shift register", "165"],
        "description": "The mirror image of the 595: reads eight inputs (buttons, "
        "switches) into three MCU pins.",
        "package": "DIP-16",
        "tags": ["expander", "digital", "input"],
        "pins": [
            {"number": 1, "name": "PL", "type": "digital", "description": "Parallel load (active low)"},
            {"number": 2, "name": "CP", "type": "digital", "description": "Clock"},
            {"number": 8, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 9, "name": "Q7", "type": "digital", "description": "Serial output"},
            {"number": 10, "name": "DS", "type": "digital", "description": "Serial input for chaining"},
            {"number": 15, "name": "CE", "type": "digital", "description": "Clock enable, tie to GND"},
            {"number": 16, "name": "VCC", "type": "power", "description": "2-6V supply"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "PL", "to_pin": "D9", "note": "Load"},
                    {"from_pin": "CP", "to_pin": "D13", "note": "Clock"},
                    {"from_pin": "Q7", "to_pin": "D12", "note": "Data in"},
                    {"from_pin": "CE", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Each parallel input needs a pull-up or pull-down resistor."],
            },
        },
        "code": {
            "uno": {
                "title": "Read 8 buttons through a 74HC165",
                "libraries": [],
                "code": """const int LOAD_PIN = 9;
const int CLOCK_PIN = 13;
const int DATA_PIN = 12;

byte readInputs() {
  digitalWrite(LOAD_PIN, LOW);      // snapshot the inputs
  delayMicroseconds(5);
  digitalWrite(LOAD_PIN, HIGH);
  return shiftIn(DATA_PIN, CLOCK_PIN, MSBFIRST);
}

void setup() {
  pinMode(LOAD_PIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);
  pinMode(DATA_PIN, INPUT);
  Serial.begin(9600);
}

void loop() {
  Serial.println(readInputs(), BIN);
  delay(200);
}
""",
            },
        },
    },
    {
        "id": "uln2003",
        "type": "ic",
        "name": "ULN2003 Darlington Array",
        "aliases": ["uln2003", "uln2803", "darlington array", "stepper driver board"],
        "description": "Seven Darlington drivers with built-in flyback diodes — the "
        "chip on the little 28BYJ-48 stepper board, also great for relays.",
        "package": "DIP-16",
        "tags": ["driver", "power"],
        "pins": [
            {"number": 1, "name": "IN1", "type": "digital", "description": "Input 1"},
            {"number": 2, "name": "IN2", "type": "digital", "description": "Input 2"},
            {"number": 3, "name": "IN3", "type": "digital", "description": "Input 3"},
            {"number": 4, "name": "IN4", "type": "digital", "description": "Input 4"},
            {"number": 8, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 9, "name": "COM", "type": "power", "description": "Flyback diode common, to the load supply"},
            {"number": 13, "name": "OUT4", "type": "digital", "description": "Open-collector output 4"},
            {"number": 14, "name": "OUT3", "type": "digital", "description": "Open-collector output 3"},
            {"number": 15, "name": "OUT2", "type": "digital", "description": "Open-collector output 2"},
            {"number": 16, "name": "OUT1", "type": "digital", "description": "Open-collector output 1"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "IN1", "to_pin": "D8", "note": ""},
                    {"from_pin": "IN2", "to_pin": "D9", "note": ""},
                    {"from_pin": "IN3", "to_pin": "D10", "note": ""},
                    {"from_pin": "IN4", "to_pin": "D11", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Share ground with the load supply"},
                    {"from_pin": "COM", "to_pin": "12V", "note": "Load supply, for the flyback diodes"},
                ],
                "notes": ["Outputs sink current: wire loads between the supply and OUTx."],
            },
        },
        "code": {},
    },
    {
        "id": "l293d",
        "type": "ic",
        "name": "L293D Motor Driver",
        "aliases": ["l293d", "l293", "motor driver", "h-bridge"],
        "description": "Dual H-bridge that drives two DC motors (or one stepper) in "
        "both directions, up to 600mA per channel.",
        "package": "DIP-16",
        "tags": ["driver", "motor"],
        "pins": [
            {"number": 1, "name": "EN1", "type": "pwm", "description": "Enable / PWM channel 1"},
            {"number": 2, "name": "IN1", "type": "digital", "description": "Direction input 1"},
            {"number": 3, "name": "OUT1", "type": "signal", "description": "Motor A terminal 1"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground + heatsink"},
            {"number": 6, "name": "OUT2", "type": "signal", "description": "Motor A terminal 2"},
            {"number": 7, "name": "IN2", "type": "digital", "description": "Direction input 2"},
            {"number": 8, "name": "VMOT", "type": "power", "description": "Motor supply (4.5-36V)"},
            {"number": 16, "name": "VCC", "type": "power", "description": "Logic supply 5V"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "Logic supply"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Common ground"},
                    {"from_pin": "EN1", "to_pin": "D9", "note": "PWM speed control"},
                    {"from_pin": "IN1", "to_pin": "D7", "note": "Direction"},
                    {"from_pin": "IN2", "to_pin": "D8", "note": "Direction"},
                    {"from_pin": "VMOT", "to_pin": "External 6-12V", "note": "Never from the Arduino 5V pin"},
                ],
                "notes": ["IN1/IN2 opposite = spin; equal = brake."],
            },
        },
        "code": {
            "uno": {
                "title": "Drive a DC motor both ways",
                "libraries": [],
                "code": """const int EN1 = 9, IN1 = 7, IN2 = 8;

void drive(int speed) {           // -255..255
  digitalWrite(IN1, speed >= 0);
  digitalWrite(IN2, speed < 0);
  analogWrite(EN1, abs(speed));
}

void setup() {
  pinMode(EN1, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
}

void loop() {
  drive(200);    // forward
  delay(2000);
  drive(0);      // stop
  delay(500);
  drive(-200);   // reverse
  delay(2000);
  drive(0);
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "pcf8574",
        "type": "ic",
        "name": "PCF8574 I2C I/O Expander",
        "aliases": ["pcf8574", "i2c expander", "io expander", "lcd backpack"],
        "description": "Adds 8 bidirectional pins over I2C, with up to 8 chips on one "
        "bus. Also the chip inside I2C LCD backpacks.",
        "package": "DIP-16 / SOIC-16",
        "tags": ["expander", "i2c"],
        "pins": [
            {"number": 1, "name": "A0", "type": "digital", "description": "Address bit 0"},
            {"number": 2, "name": "A1", "type": "digital", "description": "Address bit 1"},
            {"number": 3, "name": "A2", "type": "digital", "description": "Address bit 2"},
            {"number": 8, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 13, "name": "INT", "type": "digital", "description": "Interrupt on change (active low)"},
            {"number": 14, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 15, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 16, "name": "VCC", "type": "power", "description": "2.5-6V supply"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "A4", "note": "I2C data"},
                    {"from_pin": "SCL", "to_pin": "A5", "note": "I2C clock"},
                    {"from_pin": "A0", "to_pin": "GND", "note": "Address 0x20"},
                ],
                "notes": ["Outputs sink well but source weakly — drive LEDs to GND."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Toggle expander pins over I2C",
                "libraries": ["Wire"],
                "code": """#include <Wire.h>

const byte PCF_ADDR = 0x20;

void writePins(byte value) {
  Wire.beginTransmission(PCF_ADDR);
  Wire.write(value);
  Wire.endTransmission();
}

void setup() {
  Wire.begin();
}

void loop() {
  writePins(0b10101010);
  delay(500);
  writePins(0b01010101);
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "mcp23017",
        "type": "ic",
        "name": "MCP23017 16-bit I/O Expander",
        "aliases": ["mcp23017", "mcp23016", "16 bit io expander", "gpio expander"],
        "description": "Sixteen extra GPIOs over I2C with per-pin pull-ups and "
        "interrupts — the go-to when a panel needs more buttons than the MCU has.",
        "package": "DIP-28 / SOIC-28",
        "tags": ["expander", "i2c"],
        "pins": [
            {"number": 9, "name": "VDD", "type": "power", "description": "1.8-5.5V supply"},
            {"number": 10, "name": "VSS", "type": "ground", "description": "Ground"},
            {"number": 12, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 13, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 15, "name": "A0", "type": "digital", "description": "Address bit 0"},
            {"number": 16, "name": "A1", "type": "digital", "description": "Address bit 1"},
            {"number": 17, "name": "A2", "type": "digital", "description": "Address bit 2"},
            {"number": 18, "name": "RESET", "type": "digital", "description": "Active low, tie to VDD"},
            {"number": 20, "name": "INTA", "type": "digital", "description": "Port A interrupt"},
            {"number": 19, "name": "INTB", "type": "digital", "description": "Port B interrupt"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VDD", "to_pin": "3V3", "note": ""},
                    {"from_pin": "VSS", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                    {"from_pin": "RESET", "to_pin": "3V3", "note": "Never leave floating"},
                    {"from_pin": "A0", "to_pin": "GND", "note": "Address 0x20"},
                ],
                "notes": ["Eight chips per bus = 128 extra pins."],
            },
        },
        "code": {
            "esp32": {
                "title": "Read a button and blink an LED on the expander",
                "libraries": ["Adafruit_MCP23X17"],
                "code": """#include <Adafruit_MCP23X17.h>

Adafruit_MCP23X17 mcp;

void setup() {
  Serial.begin(115200);
  mcp.begin_I2C(0x20);
  mcp.pinMode(0, OUTPUT);              // GPA0 -> LED
  mcp.pinMode(8, INPUT_PULLUP);        // GPB0 -> button
}

void loop() {
  bool pressed = mcp.digitalRead(8) == LOW;
  mcp.digitalWrite(0, pressed ? HIGH : LOW);
  delay(50);
}
""",
            },
        },
    },
    {
        "id": "ads1115",
        "type": "ic",
        "name": "ADS1115 16-bit ADC",
        "aliases": ["ads1115", "ads1015", "i2c adc", "16 bit adc"],
        "description": "Four-channel 16-bit ADC with a programmable gain amplifier — "
        "the fix for the ESP32's noisy built-in ADC and for tiny sensor signals.",
        "package": "Module / MSOP-10",
        "tags": ["analog", "i2c", "iot"],
        "pins": [
            {"number": 1, "name": "VDD", "type": "power", "description": "2-5.5V supply"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 5, "name": "ADDR", "type": "digital", "description": "Address select (GND = 0x48)"},
            {"number": 6, "name": "ALRT", "type": "digital", "description": "Comparator alert output"},
            {"number": 7, "name": "A0", "type": "analog", "description": "Analog input 0"},
            {"number": 8, "name": "A1", "type": "analog", "description": "Analog input 1"},
            {"number": 9, "name": "A2", "type": "analog", "description": "Analog input 2"},
            {"number": 10, "name": "A3", "type": "analog", "description": "Analog input 3"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VDD", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                    {"from_pin": "ADDR", "to_pin": "GND", "note": "I2C address 0x48"},
                    {"from_pin": "A0", "to_pin": "Sensor output", "note": "Keep within VDD"},
                ],
                "notes": ["Differential mode (A0-A1) rejects noise on long sensor leads."],
            },
        },
        "code": {
            "esp32": {
                "title": "Read a 16-bit analog channel",
                "libraries": ["Adafruit_ADS1X15"],
                "code": """#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;

void setup() {
  Serial.begin(115200);
  ads.begin(0x48);
  ads.setGain(GAIN_ONE);              // +/-4.096V full scale
}

void loop() {
  int16_t raw = ads.readADC_SingleEnded(0);
  float volts = ads.computeVolts(raw);
  Serial.print(volts, 4);
  Serial.println(" V");
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "mcp3008",
        "type": "ic",
        "name": "MCP3008 8-channel SPI ADC",
        "aliases": ["mcp3008", "spi adc", "mcp3208"],
        "description": "Eight 10-bit analog inputs over SPI. The standard way to give "
        "a Raspberry Pi (which has no ADC) analog inputs.",
        "package": "DIP-16",
        "tags": ["analog", "spi"],
        "pins": [
            {"number": 1, "name": "CH0", "type": "analog", "description": "Analog input 0"},
            {"number": 9, "name": "DGND", "type": "ground", "description": "Digital ground"},
            {"number": 10, "name": "CS", "type": "spi", "description": "Chip select (active low)"},
            {"number": 11, "name": "DIN", "type": "spi", "description": "SPI MOSI"},
            {"number": 12, "name": "DOUT", "type": "spi", "description": "SPI MISO"},
            {"number": 13, "name": "CLK", "type": "spi", "description": "SPI clock"},
            {"number": 14, "name": "AGND", "type": "ground", "description": "Analog ground"},
            {"number": 15, "name": "VREF", "type": "power", "description": "Reference voltage"},
            {"number": 16, "name": "VDD", "type": "power", "description": "2.7-5.5V supply"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VDD", "to_pin": "5V", "note": ""},
                    {"from_pin": "VREF", "to_pin": "5V", "note": "Full-scale reference"},
                    {"from_pin": "AGND", "to_pin": "GND", "note": ""},
                    {"from_pin": "DGND", "to_pin": "GND", "note": ""},
                    {"from_pin": "CLK", "to_pin": "D13", "note": "SCK"},
                    {"from_pin": "DOUT", "to_pin": "D12", "note": "MISO"},
                    {"from_pin": "DIN", "to_pin": "D11", "note": "MOSI"},
                    {"from_pin": "CS", "to_pin": "D10", "note": ""},
                ],
                "notes": ["A 100nF cap right at VDD keeps readings steady."],
            },
        },
        "code": {},
    },
    {
        "id": "cd4051",
        "type": "ic",
        "name": "CD4051 8-channel Analog Mux",
        "aliases": ["cd4051", "4051", "analog multiplexer", "74hc4051"],
        "description": "Routes one of eight analog channels to a single pin — turn one "
        "ADC input into eight sensor inputs with three select pins.",
        "package": "DIP-16",
        "tags": ["analog", "expander"],
        "pins": [
            {"number": 3, "name": "COM", "type": "analog", "description": "Common in/out"},
            {"number": 6, "name": "INH", "type": "digital", "description": "Inhibit, tie to GND"},
            {"number": 7, "name": "VEE", "type": "power", "description": "Negative supply, tie to GND"},
            {"number": 8, "name": "VSS", "type": "ground", "description": "Ground"},
            {"number": 9, "name": "S2", "type": "digital", "description": "Select bit 2"},
            {"number": 10, "name": "S1", "type": "digital", "description": "Select bit 1"},
            {"number": 11, "name": "S0", "type": "digital", "description": "Select bit 0"},
            {"number": 16, "name": "VDD", "type": "power", "description": "Supply"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VDD", "to_pin": "5V", "note": ""},
                    {"from_pin": "VSS", "to_pin": "GND", "note": ""},
                    {"from_pin": "VEE", "to_pin": "GND", "note": "Single-supply operation"},
                    {"from_pin": "INH", "to_pin": "GND", "note": "Always enabled"},
                    {"from_pin": "COM", "to_pin": "A0", "note": "Multiplexed analog input"},
                    {"from_pin": "S0", "to_pin": "D2", "note": ""},
                    {"from_pin": "S1", "to_pin": "D3", "note": ""},
                    {"from_pin": "S2", "to_pin": "D4", "note": ""},
                ],
                "notes": ["Allow a few microseconds after switching before you sample."],
            },
        },
        "code": {
            "uno": {
                "title": "Scan 8 analog sensors through one pin",
                "libraries": [],
                "code": """const int S0 = 2, S1 = 3, S2 = 4;
const int MUX_OUT = A0;

int readChannel(int channel) {
  digitalWrite(S0, bitRead(channel, 0));
  digitalWrite(S1, bitRead(channel, 1));
  digitalWrite(S2, bitRead(channel, 2));
  delayMicroseconds(10);
  return analogRead(MUX_OUT);
}

void setup() {
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  for (int ch = 0; ch < 8; ch++) {
    Serial.print(readChannel(ch));
    Serial.print('\\t');
  }
  Serial.println();
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "tca9548a",
        "type": "ic",
        "name": "TCA9548A I2C Multiplexer",
        "aliases": ["tca9548a", "i2c multiplexer", "i2c mux", "pca9548"],
        "description": "Eight switchable I2C buses behind one address — the answer to "
        "'I need four identical sensors but they all use address 0x76'.",
        "package": "Module / TSSOP-24",
        "tags": ["expander", "i2c", "iot"],
        "pins": [
            {"number": 1, "name": "VIN", "type": "power", "description": "1.65-5.5V supply"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SDA", "type": "i2c", "description": "Upstream I2C data"},
            {"number": 4, "name": "SCL", "type": "i2c", "description": "Upstream I2C clock"},
            {"number": 5, "name": "RST", "type": "digital", "description": "Reset (active low)"},
            {"number": 6, "name": "SD0..SD7", "type": "i2c", "description": "Downstream data channels"},
            {"number": 7, "name": "SC0..SC7", "type": "i2c", "description": "Downstream clock channels"},
            {"number": 8, "name": "A0-A2", "type": "digital", "description": "Address select (0x70 base)"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VIN", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                ],
                "notes": ["Each downstream channel needs its own pair of pull-ups."],
            },
        },
        "code": {
            "esp32": {
                "title": "Talk to four identical I2C sensors",
                "libraries": ["Wire"],
                "code": """#include <Wire.h>

const byte MUX_ADDR = 0x70;

void selectChannel(uint8_t channel) {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << channel);           // 0 disables every channel
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  for (uint8_t ch = 0; ch < 4; ch++) {
    selectChannel(ch);
    Wire.beginTransmission(0x76);     // e.g. a BME280 on every channel
    Serial.printf("Channel %u: %s\\n", ch,
                  Wire.endTransmission() == 0 ? "sensor found" : "empty");
  }
}

void loop() {}
""",
            },
        },
    },
    {
        "id": "level_shifter",
        "type": "ic",
        "name": "Bidirectional Level Shifter",
        "aliases": ["level shifter", "logic level converter", "txs0108e", "bss138 shifter"],
        "description": "Connects 3.3V and 5V logic safely in both directions. Essential "
        "when an ESP32 or Pi talks to 5V sensors, displays or LED strips.",
        "package": "4/8-channel module",
        "tags": ["interface", "iot"],
        "pins": [
            {"number": 1, "name": "LV", "type": "power", "description": "Low-voltage side supply (3.3V)"},
            {"number": 2, "name": "HV", "type": "power", "description": "High-voltage side supply (5V)"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Common ground (both sides)"},
            {"number": 4, "name": "LV1..LV4", "type": "signal", "description": "3.3V-side channels"},
            {"number": 5, "name": "HV1..HV4", "type": "signal", "description": "5V-side channels"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "LV", "to_pin": "3V3", "note": ""},
                    {"from_pin": "HV", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Both grounds must be joined"},
                    {"from_pin": "LV1", "to_pin": "GPIO21", "note": "SDA, 3.3V side"},
                    {"from_pin": "HV1", "to_pin": "5V sensor SDA", "note": ""},
                ],
                "notes": ["BSS138 modules suit I2C; TXS0108E handles faster push-pull signals."],
            },
        },
        "code": {},
    },
    {
        "id": "atmega328p",
        "type": "ic",
        "name": "ATmega328P Microcontroller",
        "aliases": ["atmega328", "atmega328p", "arduino chip", "avr microcontroller"],
        "description": "The 8-bit AVR at the heart of the Arduino Uno and Nano: 32KB "
        "flash, 2KB RAM, 23 I/O pins. Runs standalone with a crystal and two caps.",
        "package": "DIP-28 / TQFP-32",
        "datasheet_url": "https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega48A-PA-88A-PA-168A-PA-328-P-DS-DS40002061B.pdf",
        "tags": ["mcu", "avr"],
        "pins": [
            {"number": 1, "name": "RESET", "type": "digital", "description": "Active low, 10k pull-up to VCC"},
            {"number": 7, "name": "VCC", "type": "power", "description": "1.8-5.5V supply"},
            {"number": 8, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 9, "name": "XTAL1", "type": "signal", "description": "Crystal input"},
            {"number": 10, "name": "XTAL2", "type": "signal", "description": "Crystal output"},
            {"number": 20, "name": "AVCC", "type": "power", "description": "ADC supply, tie to VCC"},
            {"number": 21, "name": "AREF", "type": "analog", "description": "ADC reference, 100nF to GND"},
            {"number": 22, "name": "AGND", "type": "ground", "description": "Analog ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "100nF decoupling"},
                    {"from_pin": "AVCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "RESET", "to_pin": "5V", "note": "Through a 10kΩ pull-up"},
                    {"from_pin": "XTAL1", "to_pin": "16MHz crystal", "note": "22pF to GND"},
                    {"from_pin": "XTAL2", "to_pin": "16MHz crystal", "note": "22pF to GND"},
                ],
                "notes": [
                    "Burn the bootloader once with an ISP programmer or another Arduino.",
                    "The internal 8MHz oscillator saves the crystal if timing is not critical.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "cd4017",
        "type": "ic",
        "name": "CD4017 Decade Counter",
        "aliases": ["cd4017", "4017", "decade counter", "johnson counter"],
        "description": "Ten outputs that go high one after another on each clock pulse "
        "— LED chasers and sequencers with no code at all.",
        "package": "DIP-16",
        "tags": ["digital", "counter"],
        "pins": [
            {"number": 8, "name": "VSS", "type": "ground", "description": "Ground"},
            {"number": 13, "name": "CE", "type": "digital", "description": "Clock enable (active low)"},
            {"number": 14, "name": "CLK", "type": "digital", "description": "Clock input"},
            {"number": 15, "name": "MR", "type": "digital", "description": "Master reset"},
            {"number": 16, "name": "VDD", "type": "power", "description": "3-15V supply"},
            {"number": 3, "name": "Q0", "type": "digital", "description": "Output 0"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VDD", "to_pin": "5V", "note": ""},
                    {"from_pin": "VSS", "to_pin": "GND", "note": ""},
                    {"from_pin": "CLK", "to_pin": "D2", "note": "One pulse advances the output"},
                    {"from_pin": "MR", "to_pin": "D3", "note": "HIGH resets to Q0"},
                    {"from_pin": "CE", "to_pin": "GND", "note": "Always counting"},
                ],
                "notes": ["Pair it with a 555 astable for a code-free LED chaser."],
            },
        },
        "code": {},
    },
]
