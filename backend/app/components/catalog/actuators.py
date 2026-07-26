"""Things that move, switch or make noise: motors, servos, relays, valves."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "mg996r",
        "type": "actuator",
        "name": "MG996R Metal-gear Servo",
        "aliases": ["mg996r", "mg995", "metal gear servo", "high torque servo"],
        "description": "Beefier 180° servo with metal gears, around 10kg·cm. Needs its "
        "own supply — it can pull 2.5A when it stalls.",
        "package": "Standard servo",
        "tags": ["motor", "servo", "robotics"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Brown wire"},
            {"number": 2, "name": "VCC", "type": "power", "description": "Red wire, 4.8-7.2V"},
            {"number": 3, "name": "Signal", "type": "pwm", "description": "Orange wire, 50Hz PWM"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "External 6V", "note": "Never from the Arduino's 5V pin"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Tie to the Arduino ground too"},
                    {"from_pin": "Signal", "to_pin": "D9", "note": ""},
                ],
                "notes": [
                    "Add 470-1000µF across the servo supply to absorb current spikes.",
                    "Powering it from the board is the usual cause of random resets.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Sweep a servo",
                "libraries": ["Servo"],
                "code": """#include <Servo.h>

Servo servo;

void setup() {
  servo.attach(9);
}

void loop() {
  for (int angle = 0; angle <= 180; angle += 2) {
    servo.write(angle);
    delay(15);
  }
  for (int angle = 180; angle >= 0; angle -= 2) {
    servo.write(angle);
    delay(15);
  }
}
""",
            },
        },
    },
    {
        "id": "servo_continuous",
        "type": "actuator",
        "name": "Continuous Rotation Servo",
        "aliases": ["continuous servo", "360 servo", "fs90r", "continuous rotation servo"],
        "description": "A servo modified to spin freely: the signal sets speed and "
        "direction instead of angle. Cheap geared drive for small robots.",
        "package": "Micro / standard servo",
        "tags": ["motor", "servo", "robotics"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Brown wire"},
            {"number": 2, "name": "VCC", "type": "power", "description": "Red wire, 4.8-6V"},
            {"number": 3, "name": "Signal", "type": "pwm", "description": "Orange wire"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "External 5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Common ground"},
                    {"from_pin": "Signal", "to_pin": "D9", "note": ""},
                ],
                "notes": ["write(90) should stop it; trim the pot inside if it creeps."],
            },
        },
        "code": {
            "uno": {
                "title": "Drive forward, stop, reverse",
                "libraries": ["Servo"],
                "code": """#include <Servo.h>

Servo wheel;

void setup() {
  wheel.attach(9);
}

void loop() {
  wheel.write(180);   // full speed one way
  delay(2000);
  wheel.write(90);    // stop
  delay(1000);
  wheel.write(0);     // full speed the other way
  delay(2000);
  wheel.write(90);
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "stepper_28byj48",
        "type": "actuator",
        "name": "28BYJ-48 Stepper Motor",
        "aliases": ["28byj-48", "28byj48", "stepper motor", "unipolar stepper"],
        "description": "Geared 5V unipolar stepper sold with a ULN2003 driver board. "
        "Slow but precise — 2048 steps per revolution in half-step mode.",
        "package": "Motor + ULN2003 board",
        "tags": ["motor", "stepper", "beginner"],
        "pins": [
            {"number": 1, "name": "IN1", "type": "digital", "description": "Driver input 1"},
            {"number": 2, "name": "IN2", "type": "digital", "description": "Driver input 2"},
            {"number": 3, "name": "IN3", "type": "digital", "description": "Driver input 3"},
            {"number": 4, "name": "IN4", "type": "digital", "description": "Driver input 4"},
            {"number": 5, "name": "VCC", "type": "power", "description": "5V to the driver board"},
            {"number": 6, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "IN1", "to_pin": "D8", "note": ""},
                    {"from_pin": "IN2", "to_pin": "D9", "note": ""},
                    {"from_pin": "IN3", "to_pin": "D10", "note": ""},
                    {"from_pin": "IN4", "to_pin": "D11", "note": ""},
                    {"from_pin": "VCC", "to_pin": "External 5V", "note": "~240mA, more than USB likes"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Common ground"},
                ],
                "notes": ["Stepper library order is IN1, IN3, IN2, IN4 — not sequential."],
            },
        },
        "code": {
            "uno": {
                "title": "Turn one full revolution",
                "libraries": ["Stepper"],
                "code": """#include <Stepper.h>

const int STEPS_PER_REV = 2048;          // 28BYJ-48 with gearbox

// Note the pin order: IN1, IN3, IN2, IN4.
Stepper motor(STEPS_PER_REV, 8, 10, 9, 11);

void setup() {
  motor.setSpeed(10);                    // RPM
  Serial.begin(9600);
}

void loop() {
  motor.step(STEPS_PER_REV);             // one turn clockwise
  delay(1000);
  motor.step(-STEPS_PER_REV);            // and back
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "nema17_a4988",
        "type": "actuator",
        "name": "NEMA 17 Stepper + A4988 Driver",
        "aliases": ["nema 17", "a4988", "drv8825", "stepper driver", "nema17"],
        "description": "The 3D-printer standard: a bipolar stepper driven by an A4988 "
        "or DRV8825 module. Two pins — step and direction — do everything.",
        "package": "NEMA 17 motor + driver module",
        "tags": ["motor", "stepper", "cnc"],
        "pins": [
            {"number": 1, "name": "STEP", "type": "digital", "description": "One pulse = one step"},
            {"number": 2, "name": "DIR", "type": "digital", "description": "Direction"},
            {"number": 3, "name": "EN", "type": "digital", "description": "Enable (active low)"},
            {"number": 4, "name": "VMOT", "type": "power", "description": "8-35V motor supply"},
            {"number": 5, "name": "GND", "type": "ground", "description": "Ground (logic and motor)"},
            {"number": 6, "name": "1A/1B/2A/2B", "type": "signal", "description": "Motor coils"},
            {"number": 7, "name": "MS1/MS2/MS3", "type": "digital", "description": "Microstep selection"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "STEP", "to_pin": "D3", "note": ""},
                    {"from_pin": "DIR", "to_pin": "D4", "note": ""},
                    {"from_pin": "EN", "to_pin": "D5", "note": "LOW enables the driver"},
                    {"from_pin": "VMOT", "to_pin": "12V supply", "note": "100µF across VMOT/GND — mandatory"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Both grounds"},
                ],
                "notes": [
                    "Set the current limit with the trim pot before running the motor.",
                    "Never unplug the motor while the driver is powered — it kills the chip.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Accelerated moves with AccelStepper",
                "libraries": ["AccelStepper"],
                "code": """#include <AccelStepper.h>

AccelStepper stepper(AccelStepper::DRIVER, 3, 4);   // STEP, DIR
const int EN_PIN = 5;

void setup() {
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);            // enable the driver
  stepper.setMaxSpeed(1000);
  stepper.setAcceleration(500);
  stepper.moveTo(3200);                 // 16 microsteps x 200 steps = 1 turn
}

void loop() {
  if (stepper.distanceToGo() == 0) {
    stepper.moveTo(-stepper.currentPosition());
  }
  stepper.run();
}
""",
            },
        },
    },
    {
        "id": "dc_motor",
        "type": "actuator",
        "name": "Brushed DC Motor",
        "aliases": ["dc motor", "gear motor", "tt motor", "hobby motor"],
        "description": "Simple two-wire motor. It must never connect straight to a "
        "GPIO pin — always drive it through a transistor or an H-bridge.",
        "package": "TT gearbox / 130 motor",
        "tags": ["motor", "robotics", "beginner"],
        "pins": [
            {"number": 1, "name": "Terminal +", "type": "power", "description": "Swap for reverse"},
            {"number": 2, "name": "Terminal -", "type": "ground", "description": "Swap for reverse"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Terminal +", "to_pin": "Driver OUT1", "note": "L293D / L298N / MOSFET"},
                    {"from_pin": "Terminal -", "to_pin": "Driver OUT2", "note": ""},
                ],
                "notes": [
                    "Solder 100nF across the terminals to tame brush noise.",
                    "Motors and logic on one battery need good decoupling, or the MCU resets.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "l298n",
        "type": "actuator",
        "name": "L298N Dual Motor Driver Module",
        "aliases": ["l298n", "l298", "motor driver module", "dual h-bridge"],
        "description": "The red 2A dual H-bridge board on almost every hobby robot. "
        "Drives two DC motors or one stepper, with an on-board 5V regulator.",
        "package": "Module",
        "tags": ["driver", "motor", "robotics"],
        "pins": [
            {"number": 1, "name": "ENA", "type": "pwm", "description": "Motor A speed (PWM)"},
            {"number": 2, "name": "IN1", "type": "digital", "description": "Motor A direction"},
            {"number": 3, "name": "IN2", "type": "digital", "description": "Motor A direction"},
            {"number": 4, "name": "IN3", "type": "digital", "description": "Motor B direction"},
            {"number": 5, "name": "IN4", "type": "digital", "description": "Motor B direction"},
            {"number": 6, "name": "ENB", "type": "pwm", "description": "Motor B speed (PWM)"},
            {"number": 7, "name": "12V", "type": "power", "description": "Motor supply 6-12V"},
            {"number": 8, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 9, "name": "5V", "type": "power", "description": "Regulator output (or input above 12V)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "ENA", "to_pin": "D9", "note": "Remove the jumper to use PWM"},
                    {"from_pin": "IN1", "to_pin": "D8", "note": ""},
                    {"from_pin": "IN2", "to_pin": "D7", "note": ""},
                    {"from_pin": "IN3", "to_pin": "D6", "note": ""},
                    {"from_pin": "IN4", "to_pin": "D5", "note": ""},
                    {"from_pin": "ENB", "to_pin": "D10", "note": ""},
                    {"from_pin": "12V", "to_pin": "Battery +", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Battery - and Arduino GND"},
                ],
                "notes": [
                    "It drops about 2V across the bridge — a 6V motor wants ~8V in.",
                    "Modern MX1508 / TB6612 boards are far more efficient.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Two-wheel robot: forward, turn, stop",
                "libraries": [],
                "code": """const int ENA = 9, IN1 = 8, IN2 = 7;
const int ENB = 10, IN3 = 6, IN4 = 5;

void wheels(int left, int right) {      // -255..255 each
  digitalWrite(IN1, left >= 0);
  digitalWrite(IN2, left < 0);
  analogWrite(ENA, abs(left));
  digitalWrite(IN3, right >= 0);
  digitalWrite(IN4, right < 0);
  analogWrite(ENB, abs(right));
}

void setup() {
  int pins[] = {ENA, IN1, IN2, ENB, IN3, IN4};
  for (int pin : pins) pinMode(pin, OUTPUT);
}

void loop() {
  wheels(200, 200);   // forward
  delay(1500);
  wheels(180, -180);  // spin on the spot
  delay(700);
  wheels(0, 0);       // stop
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "solenoid_valve",
        "type": "actuator",
        "name": "12V Solenoid Valve",
        "aliases": ["solenoid valve", "water valve", "12v valve", "irrigation valve"],
        "description": "Electrically opens or closes a water line — automatic "
        "irrigation, pet fountains, dosing systems.",
        "package": "1/2\" inline valve",
        "tags": ["actuator", "water", "iot"],
        "pins": [
            {"number": 1, "name": "Coil +", "type": "power", "description": "12V"},
            {"number": 2, "name": "Coil -", "type": "ground", "description": "Switched to ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Coil +", "to_pin": "12V supply", "note": "Flyback diode across the coil"},
                    {"from_pin": "Coil -", "to_pin": "MOSFET drain", "note": "Gate from GPIO26 via 220Ω"},
                ],
                "notes": [
                    "A 1N4007 across the coil (band to +12V) protects the driver.",
                    "Most valves are one-directional — check the arrow before plumbing.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "water_pump",
        "type": "actuator",
        "name": "Submersible Water Pump",
        "aliases": ["water pump", "submersible pump", "mini pump", "peristaltic pump"],
        "description": "Small 3-12V pump for plant watering and fountains. Peristaltic "
        "versions dose precise volumes for hydroponics.",
        "package": "Submersible / peristaltic",
        "tags": ["actuator", "water", "garden", "iot"],
        "pins": [
            {"number": 1, "name": "Motor +", "type": "power", "description": "Supply positive"},
            {"number": 2, "name": "Motor -", "type": "ground", "description": "Switched to ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Motor +", "to_pin": "12V supply", "note": "Flyback diode across the motor"},
                    {"from_pin": "Motor -", "to_pin": "Relay / MOSFET", "note": "Switched low side"},
                ],
                "notes": ["Never run a submersible pump dry — it burns out in minutes."],
            },
        },
        "code": {},
    },
    {
        "id": "solenoid_lock",
        "type": "actuator",
        "name": "12V Solenoid Door Lock",
        "aliases": ["solenoid lock", "door lock", "electric lock", "door strike"],
        "description": "Retracts a bolt when energised — pair it with an RFID reader "
        "or keypad for an access-control project.",
        "package": "Cabinet / door lock",
        "tags": ["actuator", "security", "iot"],
        "pins": [
            {"number": 1, "name": "Coil +", "type": "power", "description": "12V, 500mA-1.5A"},
            {"number": 2, "name": "Coil -", "type": "ground", "description": "Switched to ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Coil +", "to_pin": "12V supply", "note": ""},
                    {"from_pin": "Coil -", "to_pin": "Relay COM/NO", "note": "Flyback diode across the coil"},
                ],
                "notes": [
                    "Energise it for a couple of seconds, not continuously — the coil gets hot.",
                    "Fail-secure locks stay locked without power; fail-safe ones unlock. Choose deliberately.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "vibration_motor",
        "type": "actuator",
        "name": "Coin Vibration Motor",
        "aliases": ["vibration motor", "vibrator motor", "haptic motor", "coin motor"],
        "description": "Tiny eccentric-mass motor that provides haptic buzzes for "
        "wearables and alerts. Drive it through a transistor, not from a pin.",
        "package": "Coin / cylindrical",
        "tags": ["actuator", "haptic", "wearable"],
        "pins": [
            {"number": 1, "name": "Motor +", "type": "power", "description": "2.5-3.7V typical"},
            {"number": 2, "name": "Motor -", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Motor +", "to_pin": "3V3", "note": "Flyback diode across the motor"},
                    {"from_pin": "Motor -", "to_pin": "2N7000 drain", "note": "Gate from GPIO27"},
                ],
                "notes": ["PWM changes the buzz intensity."],
            },
        },
        "code": {},
    },
    {
        "id": "cooling_fan",
        "type": "actuator",
        "name": "12V Cooling Fan (PWM)",
        "aliases": ["cooling fan", "12v fan", "pwm fan", "case fan"],
        "description": "Standard 4-wire PC fan: 12V power, a 25kHz PWM control input "
        "and a tacho output you can read for RPM.",
        "package": "40-120mm fan",
        "tags": ["actuator", "thermal"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Black"},
            {"number": 2, "name": "12V", "type": "power", "description": "Yellow / red"},
            {"number": 3, "name": "TACH", "type": "digital", "description": "Green — 2 pulses per revolution"},
            {"number": 4, "name": "PWM", "type": "pwm", "description": "Blue — 25kHz control"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "12V", "to_pin": "12V supply", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Common with the ESP32"},
                    {"from_pin": "PWM", "to_pin": "GPIO25", "note": "25kHz LEDC channel"},
                    {"from_pin": "TACH", "to_pin": "GPIO26", "note": "Pull up to 3.3V, count pulses"},
                ],
                "notes": ["PWM the control wire, not the supply — chopping 12V makes fans whine."],
            },
        },
        "code": {
            "esp32": {
                "title": "Temperature-controlled fan",
                "libraries": [],
                "code": """const int FAN_PWM_PIN = 25;
const int PWM_CHANNEL = 0;

void setFanPercent(int percent) {
  ledcWrite(PWM_CHANNEL, map(constrain(percent, 0, 100), 0, 100, 0, 255));
}

void setup() {
  ledcSetup(PWM_CHANNEL, 25000, 8);     // 25kHz is the PC-fan standard
  ledcAttachPin(FAN_PWM_PIN, PWM_CHANNEL);
  Serial.begin(115200);
}

void loop() {
  float tempC = 42.0;                   // swap in a real sensor reading
  int percent = map((int)tempC, 30, 60, 20, 100);
  setFanPercent(percent);
  Serial.printf("%.1f C -> fan %d%%\\n", tempC, percent);
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "bldc_esc",
        "type": "actuator",
        "name": "Brushless Motor + ESC",
        "aliases": ["brushless motor", "bldc", "esc", "electronic speed controller", "drone motor"],
        "description": "Brushless motor driven by an ESC that takes the same 50Hz "
        "servo signal — drones, RC vehicles, high-speed fans.",
        "package": "Motor + ESC",
        "tags": ["motor", "drone", "power"],
        "pins": [
            {"number": 1, "name": "Signal", "type": "pwm", "description": "Servo-style PWM from the MCU"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Common ground"},
            {"number": 3, "name": "BEC 5V", "type": "power", "description": "5V output from the ESC (if fitted)"},
            {"number": 4, "name": "Battery +/-", "type": "power", "description": "LiPo input"},
            {"number": 5, "name": "A/B/C", "type": "signal", "description": "Three motor phases"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Signal", "to_pin": "D9", "note": "Servo library, 1000-2000µs"},
                    {"from_pin": "GND", "to_pin": "GND", "note": "Common ground"},
                ],
                "notes": [
                    "Arm the ESC with minimum throttle for a couple of seconds at power-up.",
                    "Take the propeller off before testing. Always.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Arm an ESC and ramp the throttle",
                "libraries": ["Servo"],
                "code": """#include <Servo.h>

Servo esc;

void setup() {
  esc.attach(9, 1000, 2000);
  esc.writeMicroseconds(1000);     // arming: minimum throttle
  delay(3000);
}

void loop() {
  for (int us = 1000; us <= 1400; us += 10) {   // gentle ramp only
    esc.writeMicroseconds(us);
    delay(50);
  }
  esc.writeMicroseconds(1000);
  delay(3000);
}
""",
            },
        },
    },
    {
        "id": "electromagnet",
        "type": "actuator",
        "name": "Electromagnet",
        "aliases": ["electromagnet", "holding magnet", "magnetic lock", "solenoid magnet"],
        "description": "A coil that becomes a magnet on demand — pick-and-place "
        "grippers, magnetic door holders, levitation demos.",
        "package": "Puck / cylindrical",
        "tags": ["actuator", "magnetic"],
        "pins": [
            {"number": 1, "name": "Coil +", "type": "power", "description": "5-12V"},
            {"number": 2, "name": "Coil -", "type": "ground", "description": "Switched to ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "Coil +", "to_pin": "12V supply", "note": "Flyback diode across the coil"},
                    {"from_pin": "Coil -", "to_pin": "MOSFET drain", "note": "Gate from D9 via 220Ω"},
                ],
                "notes": ["The switch-off spike is fierce — never skip the flyback diode."],
            },
        },
        "code": {},
    },
    {
        "id": "peltier",
        "type": "actuator",
        "name": "Peltier Module (TEC1-12706)",
        "aliases": ["peltier", "tec1-12706", "thermoelectric cooler", "peltier module"],
        "description": "Solid-state heat pump: one face gets cold, the other hot. Mini "
        "fridges, dehumidifiers, dew-point experiments.",
        "package": "40x40mm plate",
        "tags": ["actuator", "thermal", "power"],
        "pins": [
            {"number": 1, "name": "Red", "type": "power", "description": "12V positive"},
            {"number": 2, "name": "Black", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "Red", "to_pin": "12V supply", "note": "Draws 5-6A — size the supply properly"},
                    {"from_pin": "Black", "to_pin": "MOSFET drain", "note": "Logic-level MOSFET + heatsink"},
                ],
                "notes": [
                    "Without a heatsink and fan on the hot side it destroys itself in minutes.",
                    "Do not PWM it fast; switch slowly (seconds) or use full on/off.",
                ],
            },
        },
        "code": {},
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
        "id": "relay_module",
        "type": "actuator",
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
]
