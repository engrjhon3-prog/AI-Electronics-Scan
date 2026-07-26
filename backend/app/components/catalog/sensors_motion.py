"""Motion, distance, position and force sensors."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "vl53l0x",
        "type": "sensor",
        "name": "VL53L0X Time-of-Flight Distance Sensor",
        "aliases": ["vl53l0x", "tof sensor", "laser distance sensor", "vl53l1x"],
        "description": "Laser time-of-flight ranger, 30-2000mm with millimetre "
        "resolution over I2C. Unlike ultrasound it ignores soft, sound-absorbing "
        "surfaces.",
        "package": "Module (GY-530)",
        "tags": ["sensor", "distance", "i2c", "robotics"],
        "pins": [
            {"number": 1, "name": "VIN", "type": "power", "description": "3.3-5V (module has a regulator)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 5, "name": "XSHUT", "type": "digital", "description": "Shutdown — used to re-address multiple sensors"},
            {"number": 6, "name": "GPIO1", "type": "digital", "description": "Interrupt output"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VIN", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                    {"from_pin": "XSHUT", "to_pin": "GPIO19", "note": "Needed only for multiple sensors"},
                ],
                "notes": ["All units power up at 0x29 — hold XSHUT low and re-address one by one."],
            },
        },
        "code": {
            "esp32": {
                "title": "Read distance in millimetres",
                "libraries": ["Adafruit_VL53L0X"],
                "code": """#include <Adafruit_VL53L0X.h>

Adafruit_VL53L0X lox;

void setup() {
  Serial.begin(115200);
  if (!lox.begin()) {
    Serial.println("VL53L0X not found");
    while (1) delay(10);
  }
}

void loop() {
  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false);
  if (measure.RangeStatus != 4) {
    Serial.printf("Distance: %u mm\\n", measure.RangeMilliMeter);
  } else {
    Serial.println("Out of range");
  }
  delay(200);
}
""",
            },
        },
    },
    {
        "id": "sharp_gp2y0a21",
        "type": "sensor",
        "name": "Sharp GP2Y0A21 IR Distance Sensor",
        "aliases": ["gp2y0a21", "sharp ir sensor", "ir distance sensor", "sharp rangefinder"],
        "description": "Analog infrared rangefinder, 10-80cm. Immune to acoustic noise, "
        "which makes it a good partner for ultrasonic sensors on a robot.",
        "package": "Module with JST lead",
        "tags": ["sensor", "analog", "distance", "robotics"],
        "pins": [
            {"number": 1, "name": "VO", "type": "analog", "description": "Analog distance output"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "VCC", "type": "power", "description": "4.5-5.5V"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "10µF across VCC/GND smooths the pulses"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "VO", "to_pin": "A0", "note": ""},
                ],
                "notes": ["The curve is non-linear and ambiguous below 10cm — clamp your readings."],
            },
        },
        "code": {
            "uno": {
                "title": "Convert the analog curve to centimetres",
                "libraries": [],
                "code": """const int SENSOR_PIN = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int raw = analogRead(SENSOR_PIN);
  float volts = raw * 5.0 / 1023.0;
  float cm = 27.86 * pow(volts, -1.15);      // datasheet curve fit
  cm = constrain(cm, 10, 80);
  Serial.print(cm, 1);
  Serial.println(" cm");
  delay(150);
}
""",
            },
        },
    },
    {
        "id": "adxl345",
        "type": "sensor",
        "name": "ADXL345 3-axis Accelerometer",
        "aliases": ["adxl345", "accelerometer", "gy-291"],
        "description": "13-bit ±16g accelerometer with tap, free-fall and activity "
        "interrupts built in — motion wake-up for battery-powered nodes.",
        "package": "Module (GY-291)",
        "tags": ["sensor", "i2c", "motion", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V (module accepts 5V)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 5, "name": "INT1", "type": "digital", "description": "Interrupt 1 (tap / activity)"},
            {"number": 6, "name": "INT2", "type": "digital", "description": "Interrupt 2"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                    {"from_pin": "INT1", "to_pin": "GPIO33", "note": "Wake the ESP32 from deep sleep"},
                ],
                "notes": ["Address 0x53 (or 0x1D with SDO high)."],
            },
        },
        "code": {
            "esp32": {
                "title": "Read acceleration on three axes",
                "libraries": ["Adafruit ADXL345", "Adafruit Unified Sensor"],
                "code": """#include <Adafruit_ADXL345_U.h>

Adafruit_ADXL345_Unified accel(12345);

void setup() {
  Serial.begin(115200);
  if (!accel.begin()) {
    Serial.println("ADXL345 not found");
    while (1) delay(10);
  }
  accel.setRange(ADXL345_RANGE_4_G);
}

void loop() {
  sensors_event_t event;
  accel.getEvent(&event);
  Serial.printf("X %.2f  Y %.2f  Z %.2f m/s^2\\n",
                event.acceleration.x, event.acceleration.y, event.acceleration.z);
  delay(200);
}
""",
            },
        },
    },
    {
        "id": "hmc5883l",
        "type": "sensor",
        "name": "HMC5883L Magnetometer (Compass)",
        "aliases": ["hmc5883l", "qmc5883l", "magnetometer", "digital compass", "gy-271"],
        "description": "Three-axis magnetic field sensor used as a heading reference. "
        "Pair it with an accelerometer for a tilt-compensated compass.",
        "package": "Module (GY-271)",
        "tags": ["sensor", "i2c", "navigation", "robotics"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 5, "name": "DRDY", "type": "digital", "description": "Data ready output"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                ],
                "notes": [
                    "Keep it away from motors, speakers and current-carrying wires.",
                    "Many 'HMC5883L' boards are actually QMC5883L — different registers.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "mpu9250",
        "type": "sensor",
        "name": "MPU-9250 9-axis IMU",
        "aliases": ["mpu9250", "mpu-9250", "9 axis imu", "9dof", "icm20948"],
        "description": "Gyroscope, accelerometer and magnetometer in one package — "
        "full orientation for drones, gimbals and AHRS projects.",
        "package": "Module",
        "tags": ["sensor", "i2c", "motion", "robotics"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 5, "name": "INT", "type": "digital", "description": "Interrupt output"},
            {"number": 6, "name": "NCS", "type": "spi", "description": "SPI chip select (tie high for I2C)"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": "Not 5V tolerant"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                ],
                "notes": ["Calibrate the magnetometer by rotating it through a figure-of-eight."],
            },
        },
        "code": {},
    },
    {
        "id": "hx711",
        "type": "sensor",
        "name": "HX711 Load Cell Amplifier",
        "aliases": ["hx711", "load cell", "weight sensor", "strain gauge amplifier", "digital scale"],
        "description": "24-bit ADC built for strain gauges: connect a load cell and "
        "you have a digital scale accurate to a gram.",
        "package": "Module",
        "tags": ["sensor", "weight", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "2.7-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "DT", "type": "digital", "description": "Data out"},
            {"number": 4, "name": "SCK", "type": "digital", "description": "Clock in"},
            {"number": 5, "name": "E+/E-", "type": "power", "description": "Load-cell excitation (red / black)"},
            {"number": 6, "name": "A+/A-", "type": "analog", "description": "Load-cell signal (white / green)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "DT", "to_pin": "D3", "note": ""},
                    {"from_pin": "SCK", "to_pin": "D2", "note": ""},
                ],
                "notes": [
                    "Load cell colours: red=E+, black=E-, white=A-, green=A+.",
                    "Mount the cell rigidly — flex in the frame shows up as drift.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Digital scale with tare",
                "libraries": ["HX711"],
                "code": """#include <HX711.h>

const int DT_PIN = 3;
const int SCK_PIN = 2;
const float CALIBRATION = 420.0;   // find yours with a known weight

HX711 scale;

void setup() {
  Serial.begin(9600);
  scale.begin(DT_PIN, SCK_PIN);
  scale.set_scale(CALIBRATION);
  scale.tare();                    // zero with the pan empty
  Serial.println("Ready");
}

void loop() {
  Serial.print(scale.get_units(5), 1);
  Serial.println(" g");
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "ky040_encoder",
        "type": "sensor",
        "name": "KY-040 Rotary Encoder",
        "aliases": ["ky-040", "rotary encoder", "encoder knob", "ec11"],
        "description": "A knob that reports direction and steps instead of an absolute "
        "position — endless scrolling, menus, volume control.",
        "package": "Module with push switch",
        "tags": ["input", "digital", "ui"],
        "pins": [
            {"number": 1, "name": "CLK", "type": "digital", "description": "Encoder channel A"},
            {"number": 2, "name": "DT", "type": "digital", "description": "Encoder channel B"},
            {"number": 3, "name": "SW", "type": "digital", "description": "Push switch (active low)"},
            {"number": 4, "name": "+", "type": "power", "description": "3.3-5V"},
            {"number": 5, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "+", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "CLK", "to_pin": "D2", "note": "Interrupt pin"},
                    {"from_pin": "DT", "to_pin": "D3", "note": ""},
                    {"from_pin": "SW", "to_pin": "D4", "note": "Use INPUT_PULLUP"},
                ],
                "notes": ["Add 100nF from CLK/DT to GND if the count jitters."],
            },
        },
        "code": {
            "uno": {
                "title": "Count rotary steps and clicks",
                "libraries": [],
                "code": """const int CLK_PIN = 2, DT_PIN = 3, SW_PIN = 4;

volatile int position = 0;
int lastClk = HIGH;

void setup() {
  pinMode(CLK_PIN, INPUT_PULLUP);
  pinMode(DT_PIN, INPUT_PULLUP);
  pinMode(SW_PIN, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  int clk = digitalRead(CLK_PIN);
  if (clk != lastClk && clk == LOW) {
    position += (digitalRead(DT_PIN) != clk) ? 1 : -1;
    Serial.println(position);
  }
  lastClk = clk;

  if (digitalRead(SW_PIN) == LOW) {
    Serial.println("Knob pressed");
    delay(250);            // crude debounce
  }
}
""",
            },
        },
    },
    {
        "id": "joystick_module",
        "type": "sensor",
        "name": "Analog Joystick Module",
        "aliases": ["joystick", "ky-023", "thumb joystick", "analog stick"],
        "description": "Two potentiometers and a push switch under a thumbstick — "
        "the standard input for robot and camera-gimbal control.",
        "package": "Module",
        "tags": ["input", "analog", "beginner"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 2, "name": "+5V", "type": "power", "description": "Supply"},
            {"number": 3, "name": "VRx", "type": "analog", "description": "X axis"},
            {"number": 4, "name": "VRy", "type": "analog", "description": "Y axis"},
            {"number": 5, "name": "SW", "type": "digital", "description": "Push switch (active low)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "+5V", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "VRx", "to_pin": "A0", "note": ""},
                    {"from_pin": "VRy", "to_pin": "A1", "note": ""},
                    {"from_pin": "SW", "to_pin": "D2", "note": "INPUT_PULLUP"},
                ],
                "notes": ["Centre rarely reads exactly 512 — add a small dead zone."],
            },
        },
        "code": {
            "uno": {
                "title": "Read joystick position and click",
                "libraries": [],
                "code": """const int X_PIN = A0, Y_PIN = A1, SW_PIN = 2;

void setup() {
  pinMode(SW_PIN, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  int x = analogRead(X_PIN) - 512;
  int y = analogRead(Y_PIN) - 512;
  if (abs(x) < 30) x = 0;          // dead zone
  if (abs(y) < 30) y = 0;

  Serial.print("X: "); Serial.print(x);
  Serial.print("  Y: "); Serial.print(y);
  Serial.print("  SW: ");
  Serial.println(digitalRead(SW_PIN) == LOW ? "pressed" : "-");
  delay(100);
}
""",
            },
        },
    },
    {
        "id": "hall_a3144",
        "type": "sensor",
        "name": "A3144 Hall Effect Sensor",
        "aliases": ["a3144", "hall sensor", "hall effect sensor", "ky-003", "magnet sensor"],
        "description": "Digital magnetic switch: output goes low near a magnet's south "
        "pole. Contactless RPM counting and door sensing.",
        "package": "TO-92",
        "tags": ["sensor", "digital", "magnetic"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "4.5-24V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "OUT", "type": "digital", "description": "Open collector — needs a pull-up"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "D2", "note": "10kΩ pull-up, or use INPUT_PULLUP"},
                ],
                "notes": ["Latching types stay switched until the opposite pole passes."],
            },
        },
        "code": {
            "uno": {
                "title": "Measure RPM with a magnet on the shaft",
                "libraries": [],
                "code": """const int HALL_PIN = 2;
volatile unsigned long pulses = 0;

void countPulse() { pulses++; }

void setup() {
  pinMode(HALL_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(HALL_PIN), countPulse, FALLING);
  Serial.begin(9600);
}

void loop() {
  pulses = 0;
  delay(1000);
  noInterrupts();
  unsigned long count = pulses;
  interrupts();
  Serial.print(count * 60);        // one magnet = one pulse per turn
  Serial.println(" RPM");
}
""",
            },
        },
    },
    {
        "id": "tcrt5000",
        "type": "sensor",
        "name": "TCRT5000 Reflective IR Sensor",
        "aliases": ["tcrt5000", "line follower sensor", "ir reflective sensor", "line sensor"],
        "description": "IR emitter and phototransistor facing the same way: detects "
        "whether the surface below is light or dark. The line-follower staple.",
        "package": "Module / bare part",
        "tags": ["sensor", "ir", "robotics"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "DO", "type": "digital", "description": "Digital output (threshold)"},
            {"number": 4, "name": "AO", "type": "analog", "description": "Analog reflectance"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "DO", "to_pin": "D4", "note": ""},
                    {"from_pin": "AO", "to_pin": "A0", "note": "Better for PID line following"},
                ],
                "notes": ["Works best 3-8mm above the surface; shield it from room light."],
            },
        },
        "code": {},
    },
    {
        "id": "ir_obstacle",
        "type": "sensor",
        "name": "IR Obstacle Avoidance Sensor",
        "aliases": ["ir obstacle sensor", "obstacle avoidance sensor", "fc-51", "proximity sensor"],
        "description": "IR LED plus receiver with an adjustable range pot — outputs "
        "LOW when something is in front of it. Bumper sensor for robots.",
        "package": "Module",
        "tags": ["sensor", "digital", "robotics", "beginner"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "OUT", "type": "digital", "description": "LOW when an obstacle is detected"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "D2", "note": ""},
                ],
                "notes": ["Dark and shiny surfaces reflect poorly — test with your real target."],
            },
        },
        "code": {},
    },
    {
        "id": "ttp223",
        "type": "sensor",
        "name": "TTP223 Capacitive Touch Sensor",
        "aliases": ["ttp223", "touch sensor", "capacitive touch button", "touch pad"],
        "description": "Solid-state touch button that works through plastic or glass — "
        "no moving parts to wear out.",
        "package": "Module",
        "tags": ["input", "digital", "ui"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "2-5.5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SIG", "type": "digital", "description": "HIGH while touched"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SIG", "to_pin": "GPIO14", "note": ""},
                ],
                "notes": [
                    "Solder jumpers on the back switch between momentary and toggle modes.",
                    "The ESP32 also has ten touch-capable GPIOs of its own — no module needed.",
                ],
            },
        },
        "code": {
            "esp32": {
                "title": "Use the ESP32's built-in touch pins",
                "libraries": [],
                "code": """const int TOUCH_PIN = T0;      // GPIO4
const int THRESHOLD = 40;

void setup() {
  Serial.begin(115200);
}

void loop() {
  int value = touchRead(TOUCH_PIN);
  Serial.printf("touch=%d %s\\n", value, value < THRESHOLD ? "<- touched" : "");
  delay(200);
}
""",
            },
        },
    },
    {
        "id": "vibration_sw420",
        "type": "sensor",
        "name": "SW-420 Vibration Sensor",
        "aliases": ["sw-420", "vibration sensor", "shock sensor", "sw-18010p"],
        "description": "A spring-loaded switch that closes when shaken. Tamper alarms, "
        "knock detection, machine-running detection.",
        "package": "Module",
        "tags": ["sensor", "digital", "security"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "DO", "type": "digital", "description": "Digital output"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "DO", "to_pin": "D2", "note": "Interrupt pin"},
                ],
                "notes": ["Debounce in software — a single knock produces a burst of pulses."],
            },
        },
        "code": {},
    },
    {
        "id": "tilt_switch",
        "type": "switch",
        "name": "Tilt Switch (SW-520D)",
        "aliases": ["tilt switch", "sw-520d", "ball switch", "tilt sensor"],
        "description": "A rolling ball closes two contacts when the part is tipped — "
        "the simplest possible orientation sensor.",
        "package": "Cylindrical THT",
        "tags": ["input", "digital", "beginner"],
        "pins": [
            {"number": 1, "name": "Pin 1", "type": "digital", "description": "To the MCU pin"},
            {"number": 2, "name": "Pin 2", "type": "ground", "description": "To ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Pin 1", "to_pin": "D2", "note": "INPUT_PULLUP"},
                    {"from_pin": "Pin 2", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Bounces badly while moving — filter over ~50ms."],
            },
        },
        "code": {},
    },
    {
        "id": "reed_switch",
        "type": "switch",
        "name": "Reed Switch",
        "aliases": ["reed switch", "magnetic switch", "door sensor", "window sensor"],
        "description": "Sealed contacts that close near a magnet. The classic door and "
        "window sensor in alarm systems, and a cheap RPM pickup.",
        "package": "Glass THT / cased pair",
        "tags": ["input", "digital", "security"],
        "pins": [
            {"number": 1, "name": "Pin 1", "type": "digital", "description": "To the MCU pin"},
            {"number": 2, "name": "Pin 2", "type": "ground", "description": "To ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Pin 1", "to_pin": "GPIO27", "note": "INPUT_PULLUP"},
                    {"from_pin": "Pin 2", "to_pin": "GND", "note": ""},
                ],
                "notes": ["A GPIO wake source lets a battery door sensor sleep for months."],
            },
        },
        "code": {},
    },
    {
        "id": "limit_switch",
        "type": "switch",
        "name": "Micro Limit Switch",
        "aliases": ["limit switch", "micro switch", "endstop", "microswitch"],
        "description": "Lever-actuated snap switch with common, normally-open and "
        "normally-closed contacts — 3D printer endstops, machine limits.",
        "package": "Micro switch",
        "tags": ["input", "digital", "cnc"],
        "pins": [
            {"number": 1, "name": "COM", "type": "ground", "description": "Common"},
            {"number": 2, "name": "NO", "type": "digital", "description": "Normally open"},
            {"number": 3, "name": "NC", "type": "digital", "description": "Normally closed"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "COM", "to_pin": "GND", "note": ""},
                    {"from_pin": "NC", "to_pin": "D3", "note": "INPUT_PULLUP; a broken wire then reads as triggered"},
                ],
                "notes": ["Wiring endstops normally-closed makes cable faults fail safe."],
            },
        },
        "code": {},
    },
    {
        "id": "rcwl0516",
        "type": "sensor",
        "name": "RCWL-0516 Microwave Radar Sensor",
        "aliases": ["rcwl-0516", "microwave sensor", "radar motion sensor", "doppler sensor"],
        "description": "Doppler radar motion detector that sees through plastic and "
        "thin walls, and unlike a PIR is unaffected by temperature.",
        "package": "Module",
        "tags": ["sensor", "motion", "security", "iot"],
        "pins": [
            {"number": 1, "name": "VIN", "type": "power", "description": "4-28V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "OUT", "type": "digital", "description": "HIGH ~2s on motion"},
            {"number": 4, "name": "3V3", "type": "power", "description": "Regulated 3.3V output (100mA)"},
            {"number": 5, "name": "CDS", "type": "analog", "description": "Light-sensor input to disable in daylight"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VIN", "to_pin": "5V (VIN)", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "GPIO27", "note": "3.3V logic, safe direct"},
                ],
                "notes": [
                    "Very sensitive — it will trigger through a wall, which is sometimes a bug.",
                    "Keep it away from the Wi-Fi antenna and switching supplies.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "flex_sensor",
        "type": "sensor",
        "name": "Flex / Bend Sensor",
        "aliases": ["flex sensor", "bend sensor", "flexible resistor"],
        "description": "A strip whose resistance rises as it bends — gesture gloves, "
        "robotic-hand feedback, hinge angle sensing.",
        "package": "2.2\" / 4.5\" strip",
        "tags": ["sensor", "analog", "wearable"],
        "pins": [
            {"number": 1, "name": "Terminal A", "type": "analog", "description": "Non-polarised"},
            {"number": 2, "name": "Terminal B", "type": "analog", "description": "Non-polarised"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal A", "to_pin": "5V", "note": ""},
                    {"from_pin": "Terminal B", "to_pin": "A0", "note": "47kΩ from A0 to GND"},
                ],
                "notes": ["Never crease it — bend it over a curve or it cracks."],
            },
        },
        "code": {},
    },
    {
        "id": "current_acs712",
        "type": "sensor",
        "name": "ACS712 Current Sensor",
        "aliases": ["acs712", "current sensor", "hall current sensor"],
        "description": "Hall-effect current sensor (5A/20A/30A) with galvanic isolation "
        "— measures DC or AC current as an analog voltage around VCC/2.",
        "package": "Module",
        "tags": ["sensor", "analog", "power", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "OUT", "type": "analog", "description": "VCC/2 at zero current"},
            {"number": 4, "name": "IP+", "type": "power", "description": "Load current in"},
            {"number": 5, "name": "IP-", "type": "power", "description": "Load current out"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "A0", "note": ""},
                    {"from_pin": "IP+", "to_pin": "Supply +", "note": "In series with the load"},
                    {"from_pin": "IP-", "to_pin": "Load +", "note": ""},
                ],
                "notes": [
                    "Zero it in software at boot with no load connected.",
                    "The 5A version has the best resolution — don't over-spec it.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Measure DC current (ACS712-05B)",
                "libraries": [],
                "code": """const int SENSOR_PIN = A0;
const float SENSITIVITY = 0.185;   // V per amp for the 5A version
float zeroVolts = 2.5;

void setup() {
  Serial.begin(9600);
  delay(200);
  zeroVolts = analogRead(SENSOR_PIN) * 5.0 / 1023.0;   // calibrate unloaded
}

void loop() {
  float volts = analogRead(SENSOR_PIN) * 5.0 / 1023.0;
  float amps = (volts - zeroVolts) / SENSITIVITY;
  Serial.print(amps, 3);
  Serial.println(" A");
  delay(300);
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
]
