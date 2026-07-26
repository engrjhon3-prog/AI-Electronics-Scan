"""Built-in component knowledge base.

This is the "brain" behind pinouts, wiring diagrams, and code generation.
Each entry contains everything needed to help a maker wire the part up and
get working firmware, for both Arduino (AVR) and ESP32/ESP8266 targets.

The data here is intentionally hand-curated and conservative — it favours the
most common, well-documented parts a hobbyist is likely to scan. Adding a new
component is just a matter of appending a dict to `_RAW`.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from app.models import (
    Board,
    CodeSnippet,
    Component,
    ComponentType,
    Connection,
    Pin,
    PinType,
    WiringDiagram,
)

# ---------------------------------------------------------------------------
# Raw data. Each component declares pins, per-board wiring, and per-board code.
# ---------------------------------------------------------------------------

_RAW: List[dict] = [
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
        "id": "resistor",
        "type": "resistor",
        "name": "Resistor",
        "aliases": ["resistor", "ohm"],
        "description": "A passive two-terminal component that limits current. The "
        "colour bands encode its resistance value and tolerance.",
        "package": "Axial THT",
        "tags": ["passive"],
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
        "id": "push_button",
        "type": "module",
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
    {
        "id": "potentiometer",
        "type": "sensor",
        "name": "Potentiometer",
        "aliases": ["pot", "potentiometer", "trimpot", "variable resistor"],
        "description": "A three-terminal variable resistor. The wiper outputs an "
        "analog voltage between the two ends.",
        "package": "THT",
        "tags": ["input", "analog"],
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
        "id": "dht11",
        "type": "sensor",
        "name": "DHT11 Temperature & Humidity Sensor",
        "aliases": ["dht11", "dht", "temperature humidity sensor"],
        "description": "A low-cost digital temperature and humidity sensor using a "
        "single-wire protocol. DHT22 is the higher-precision sibling.",
        "package": "4-pin module",
        "tags": ["sensor", "digital", "temperature", "humidity"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "DATA", "type": "digital", "description": "Single-wire data, needs 10k pull-up"},
            {"number": 3, "name": "NC", "type": "nc", "description": "Not connected (bare sensor)"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "DATA", "to_pin": "D2", "note": "10kΩ pull-up to VCC"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Many DHT11 modules include the pull-up resistor already."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "DATA", "to_pin": "GPIO4", "note": "10kΩ pull-up to 3V3"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Read temperature & humidity (DHT11)",
                "libraries": ["DHT sensor library (Adafruit)", "Adafruit Unified Sensor"],
                "code": """#include <DHT.h>

#define DHT_PIN 2
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float humidity = dht.readHumidity();
  float tempC = dht.readTemperature();
  if (isnan(humidity) || isnan(tempC)) {
    Serial.println("Sensor read failed");
  } else {
    Serial.print("Temp: "); Serial.print(tempC); Serial.print(" C  ");
    Serial.print("Humidity: "); Serial.print(humidity); Serial.println(" %");
  }
  delay(2000);
}
""",
            },
            "esp32": {
                "title": "Read temperature & humidity (DHT11 on ESP32)",
                "libraries": ["DHT sensor library (Adafruit)", "Adafruit Unified Sensor"],
                "code": """#include <DHT.h>

#define DHT_PIN 4
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  float humidity = dht.readHumidity();
  float tempC = dht.readTemperature();
  if (isnan(humidity) || isnan(tempC)) {
    Serial.println("Sensor read failed");
  } else {
    Serial.printf("Temp: %.1f C  Humidity: %.1f %%\\n", tempC, humidity);
  }
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "hcsr04",
        "type": "sensor",
        "name": "HC-SR04 Ultrasonic Distance Sensor",
        "aliases": ["hc-sr04", "hcsr04", "ultrasonic sensor", "distance sensor"],
        "description": "An ultrasonic ranging module. Emit a trigger pulse, then time "
        "the echo to compute distance (2cm-400cm).",
        "package": "4-pin module",
        "tags": ["sensor", "distance"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V"},
            {"number": 2, "name": "TRIG", "type": "digital", "description": "Trigger input"},
            {"number": 3, "name": "ECHO", "type": "digital", "description": "Echo output (5V!)"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "TRIG", "to_pin": "D9", "note": ""},
                    {"from_pin": "ECHO", "to_pin": "D10", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": [],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": "Sensor needs 5V"},
                    {"from_pin": "TRIG", "to_pin": "GPIO5", "note": ""},
                    {"from_pin": "ECHO", "to_pin": "GPIO18", "note": "Use a divider: ECHO is 5V!"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["ECHO outputs 5V — drop to 3.3V with a 1k/2k divider on ESP32."],
            },
        },
        "code": {
            "uno": {
                "title": "Measure distance (HC-SR04)",
                "libraries": [],
                "code": """const int TRIG_PIN = 9;
const int ECHO_PIN = 10;

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distanceCm = duration * 0.0343 / 2.0;
  Serial.print("Distance: ");
  Serial.print(distanceCm);
  Serial.println(" cm");
  delay(200);
}
""",
            },
        },
    },
    {
        "id": "hcsr501",
        "type": "sensor",
        "name": "HC-SR501 PIR Motion Sensor",
        "aliases": ["pir", "hc-sr501", "motion sensor"],
        "description": "A passive infrared motion detector. Outputs HIGH when motion is "
        "detected; on-board pots set sensitivity and hold time.",
        "package": "3-pin module",
        "tags": ["sensor", "motion", "digital"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5-20V"},
            {"number": 2, "name": "OUT", "type": "digital", "description": "3.3V digital output"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "OUT", "to_pin": "D2", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": [],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": ""},
                    {"from_pin": "OUT", "to_pin": "GPIO13", "note": "Output is 3.3V, safe"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Detect motion (PIR)",
                "libraries": [],
                "code": """const int PIR_PIN = 2;

void setup() {
  pinMode(PIR_PIN, INPUT);
  Serial.begin(9600);
}

void loop() {
  if (digitalRead(PIR_PIN) == HIGH) {
    Serial.println("Motion detected!");
  }
  delay(200);
}
""",
            },
        },
    },
    {
        "id": "sg90",
        "type": "actuator",
        "name": "SG90 Micro Servo",
        "aliases": ["sg90", "servo", "micro servo"],
        "description": "A small hobby servo controlled with a 50Hz PWM signal. Position "
        "maps to pulse width (~1-2ms).",
        "package": "Servo",
        "tags": ["actuator", "pwm"],
        "pins": [
            {"number": 1, "name": "Signal", "type": "pwm", "description": "Orange/yellow wire"},
            {"number": 2, "name": "VCC", "type": "power", "description": "Red wire, 4.8-6V"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Brown/black wire"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Signal", "to_pin": "D9", "note": "PWM-capable pin"},
                    {"from_pin": "VCC", "to_pin": "5V", "note": "Use external 5V if it stutters"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Share ground with the board"},
                ],
                "notes": ["Servos can draw >250mA; power from an external supply for reliability."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "Signal", "to_pin": "GPIO13", "note": ""},
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Sweep a servo",
                "libraries": ["Servo (built-in)"],
                "code": """#include <Servo.h>

Servo myServo;

void setup() {
  myServo.attach(9);
}

void loop() {
  for (int angle = 0; angle <= 180; angle++) {
    myServo.write(angle);
    delay(15);
  }
  for (int angle = 180; angle >= 0; angle--) {
    myServo.write(angle);
    delay(15);
  }
}
""",
            },
            "esp32": {
                "title": "Sweep a servo (ESP32)",
                "libraries": ["ESP32Servo"],
                "code": """#include <ESP32Servo.h>

Servo myServo;

void setup() {
  myServo.attach(13);
}

void loop() {
  for (int angle = 0; angle <= 180; angle++) {
    myServo.write(angle);
    delay(15);
  }
  for (int angle = 180; angle >= 0; angle--) {
    myServo.write(angle);
    delay(15);
  }
}
""",
            },
        },
    },
    {
        "id": "ssd1306",
        "type": "module",
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
    {
        "id": "mpu6050",
        "type": "sensor",
        "name": "MPU-6050 Accelerometer + Gyroscope",
        "aliases": ["mpu6050", "mpu-6050", "imu", "accelerometer", "gyroscope"],
        "description": "A 6-axis inertial measurement unit (3-axis accelerometer + "
        "3-axis gyro) over I2C. Default address 0x68.",
        "package": "I2C module",
        "tags": ["sensor", "i2c", "imu"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V (onboard regulator)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 5, "name": "XDA", "type": "i2c", "description": "Auxiliary I2C data (optional)"},
            {"number": 6, "name": "XCL", "type": "i2c", "description": "Auxiliary I2C clock (optional)"},
            {"number": 7, "name": "AD0", "type": "digital", "description": "Address select (LOW=0x68)"},
            {"number": 8, "name": "INT", "type": "digital", "description": "Interrupt output"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SCL", "to_pin": "A5", "note": ""},
                    {"from_pin": "SDA", "to_pin": "A4", "note": ""},
                ],
                "notes": [],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Read acceleration (MPU-6050)",
                "libraries": ["Adafruit MPU6050", "Adafruit Unified Sensor"],
                "code": """#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(9600);
  if (!mpu.begin()) {
    Serial.println("MPU6050 not found");
    while (1) delay(10);
  }
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  Serial.print("aX: "); Serial.print(a.acceleration.x);
  Serial.print("  aY: "); Serial.print(a.acceleration.y);
  Serial.print("  aZ: "); Serial.println(a.acceleration.z);
  delay(200);
}
""",
            },
        },
    },
    {
        "id": "hc05",
        "type": "module",
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
    {
        "id": "relay_module",
        "type": "module",
        "name": "Relay Module (1-channel)",
        "aliases": ["relay", "relay module"],
        "description": "An opto-isolated relay board that switches mains/high-current "
        "loads from a logic pin. Most are active-LOW.",
        "package": "Relay board",
        "tags": ["module", "actuator"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V coil supply"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "IN", "type": "digital", "description": "Control input (often active-LOW)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "IN", "to_pin": "D7", "note": "LOW usually turns the relay ON"},
                ],
                "notes": ["Never wire mains voltage without proper insulation and knowledge."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "IN", "to_pin": "GPIO26", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Toggle a relay",
                "libraries": [],
                "code": """const int RELAY_PIN = 7;

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // OFF for active-LOW modules
}

void loop() {
  digitalWrite(RELAY_PIN, LOW);  // ON
  delay(2000);
  digitalWrite(RELAY_PIN, HIGH); // OFF
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "l293d",
        "type": "ic",
        "name": "L293D Motor Driver",
        "aliases": ["l293d", "motor driver", "h-bridge"],
        "description": "A dual H-bridge driver IC that can control two DC motors or one "
        "stepper. Handles up to 600mA per channel.",
        "package": "DIP-16",
        "datasheet_url": "https://www.ti.com/lit/ds/symlink/l293d.pdf",
        "tags": ["ic", "motor", "driver"],
        "pins": [
            {"number": 1, "name": "EN1,2", "type": "digital", "description": "Enable channel 1/2 (PWM)"},
            {"number": 2, "name": "IN1", "type": "digital", "description": "Input 1"},
            {"number": 3, "name": "OUT1", "type": "signal", "description": "Output 1 to motor A"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground / heatsink"},
            {"number": 5, "name": "GND", "type": "ground", "description": "Ground / heatsink"},
            {"number": 6, "name": "OUT2", "type": "signal", "description": "Output 2 to motor A"},
            {"number": 7, "name": "IN2", "type": "digital", "description": "Input 2"},
            {"number": 8, "name": "VCC2", "type": "power", "description": "Motor supply (up to 36V)"},
            {"number": 9, "name": "EN3,4", "type": "digital", "description": "Enable channel 3/4 (PWM)"},
            {"number": 10, "name": "IN3", "type": "digital", "description": "Input 3"},
            {"number": 11, "name": "OUT3", "type": "signal", "description": "Output 3 to motor B"},
            {"number": 12, "name": "GND", "type": "ground", "description": "Ground / heatsink"},
            {"number": 13, "name": "GND", "type": "ground", "description": "Ground / heatsink"},
            {"number": 14, "name": "OUT4", "type": "signal", "description": "Output 4 to motor B"},
            {"number": 15, "name": "IN4", "type": "digital", "description": "Input 4"},
            {"number": 16, "name": "VCC1", "type": "power", "description": "Logic supply 5V"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC1", "to_pin": "5V", "note": "Logic supply"},
                    {"from_pin": "VCC2", "to_pin": "Motor V+", "note": "External motor supply"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Common ground with the board"},
                    {"from_pin": "EN1,2", "to_pin": "D9", "note": "PWM for speed"},
                    {"from_pin": "IN1", "to_pin": "D8", "note": "Direction"},
                    {"from_pin": "IN2", "to_pin": "D7", "note": "Direction"},
                ],
                "notes": ["Tie the motor supply ground to the Arduino ground."],
            },
        },
        "code": {
            "uno": {
                "title": "Drive a DC motor (L293D)",
                "libraries": [],
                "code": """const int EN = 9;   // PWM
const int IN1 = 8;
const int IN2 = 7;

void setup() {
  pinMode(EN, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
}

void loop() {
  // Forward at ~75% speed
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(EN, 190);
  delay(2000);

  // Stop
  analogWrite(EN, 0);
  delay(1000);

  // Reverse
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(EN, 190);
  delay(2000);
}
""",
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Build typed objects and lookup indexes at import time.
# ---------------------------------------------------------------------------


def _build_component(raw: dict) -> Component:
    pins = [Pin(**p) for p in raw.get("pins", [])]
    boards = [Board(b) for b in raw.get("wiring", {}).keys()]
    return Component(
        id=raw["id"],
        type=ComponentType(raw["type"]),
        name=raw["name"],
        aliases=raw.get("aliases", []),
        description=raw.get("description", ""),
        package=raw.get("package", ""),
        datasheet_url=raw.get("datasheet_url"),
        pins=pins,
        supported_boards=boards,
        tags=raw.get("tags", []),
    )


_COMPONENTS: Dict[str, Component] = {}
_RAW_BY_ID: Dict[str, dict] = {}
_ALIAS_INDEX: Dict[str, str] = {}

for _raw in _RAW:
    comp = _build_component(_raw)
    _COMPONENTS[comp.id] = comp
    _RAW_BY_ID[comp.id] = _raw
    _ALIAS_INDEX[comp.id.lower()] = comp.id
    _ALIAS_INDEX[comp.name.lower()] = comp.id
    for alias in comp.aliases:
        _ALIAS_INDEX[alias.lower()] = comp.id


def all_components() -> List[Component]:
    return list(_COMPONENTS.values())


def get_component(component_id: str) -> Optional[Component]:
    return _COMPONENTS.get(component_id)


def find_by_alias(text: str) -> Optional[str]:
    """Return a component id whose name/alias appears in `text`, if any."""
    t = text.lower()
    # Exact alias hit first.
    if t in _ALIAS_INDEX:
        return _ALIAS_INDEX[t]
    # Otherwise substring match, preferring the longest alias.
    best: Optional[str] = None
    best_len = 0
    for alias, cid in _ALIAS_INDEX.items():
        if len(alias) >= 3 and alias in t and len(alias) > best_len:
            best = cid
            best_len = len(alias)
    return best


def get_wiring(component_id: str, board: Board) -> Optional[WiringDiagram]:
    raw = _RAW_BY_ID.get(component_id)
    if not raw:
        return None
    wiring = raw.get("wiring", {}).get(board.value)
    if not wiring:
        return None
    connections = [Connection(**c) for c in wiring.get("connections", [])]
    return WiringDiagram(
        component_id=component_id,
        board=board,
        connections=connections,
        notes=wiring.get("notes", []),
    )


def get_code(component_id: str, board: Board) -> Optional[CodeSnippet]:
    raw = _RAW_BY_ID.get(component_id)
    if not raw:
        return None
    code = raw.get("code", {}).get(board.value)
    if not code:
        return None
    return CodeSnippet(
        component_id=component_id,
        board=board,
        title=code.get("title", ""),
        description=code.get("description", ""),
        libraries=code.get("libraries", []),
        code=code.get("code", ""),
    )
