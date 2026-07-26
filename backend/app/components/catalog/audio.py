"""Sound in and out: buzzers, microphones, amplifiers, players."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "buzzer_active",
        "type": "audio",
        "name": "Active Buzzer",
        "aliases": ["active buzzer", "buzzer", "beeper"],
        "description": "Contains its own oscillator: apply voltage and it beeps at a "
        "fixed pitch. One digital pin, no timing code.",
        "package": "12mm THT",
        "tags": ["output", "audio", "beginner"],
        "pins": [
            {"number": 1, "name": "+", "type": "digital", "description": "Longer leg / marked +"},
            {"number": 2, "name": "-", "type": "ground", "description": "To ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "+", "to_pin": "D8", "note": "Under 20mA, so a pin can drive it"},
                    {"from_pin": "-", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Louder buzzers need a transistor — check the current rating."],
            },
        },
        "code": {
            "uno": {
                "title": "Beep on a schedule",
                "libraries": [],
                "code": """const int BUZZER_PIN = 8;

void beep(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(120);
    digitalWrite(BUZZER_PIN, LOW);
    delay(120);
  }
}

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  beep(2);
  delay(3000);
}
""",
            },
        },
    },
    {
        "id": "buzzer_passive",
        "type": "audio",
        "name": "Passive Buzzer",
        "aliases": ["passive buzzer", "piezo buzzer", "piezo speaker", "tone buzzer"],
        "description": "A bare piezo element — you supply the frequency, so it can play "
        "melodies and alarm patterns rather than a single beep.",
        "package": "12mm THT",
        "tags": ["output", "audio", "pwm", "beginner"],
        "pins": [
            {"number": 1, "name": "+", "type": "pwm", "description": "Drive with a square wave"},
            {"number": 2, "name": "-", "type": "ground", "description": "To ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "+", "to_pin": "D8", "note": "Use tone()"},
                    {"from_pin": "-", "to_pin": "GND", "note": "100Ω in series lowers the volume"},
                ],
                "notes": ["tone() ties up Timer2, which breaks PWM on pins 3 and 11."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "+", "to_pin": "GPIO25", "note": "Use ledcWriteTone()"},
                    {"from_pin": "-", "to_pin": "GND", "note": ""},
                ],
                "notes": ["The ESP32 core's tone() support varies — LEDC is reliable."],
            },
        },
        "code": {
            "uno": {
                "title": "Play a short melody",
                "libraries": [],
                "code": """const int BUZZER_PIN = 8;

const int MELODY[] = {262, 294, 330, 349, 392};   // C D E F G
const int DURATION = 250;

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  for (int note : MELODY) {
    tone(BUZZER_PIN, note, DURATION);
    delay(DURATION * 1.3);
  }
  noTone(BUZZER_PIN);
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "dfplayer_mini",
        "type": "audio",
        "name": "DFPlayer Mini MP3 Module",
        "aliases": ["dfplayer", "dfplayer mini", "mp3 module", "yx5300"],
        "description": "Plays MP3 files from a microSD card over a two-wire serial "
        "link, with a built-in 3W amplifier. Voice prompts and alarm sounds.",
        "package": "Module",
        "tags": ["audio", "uart", "storage"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.2-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "RX", "type": "uart", "description": "Commands in (needs a 1kΩ series resistor)"},
            {"number": 4, "name": "TX", "type": "uart", "description": "Status out"},
            {"number": 5, "name": "SPK1/SPK2", "type": "signal", "description": "Speaker output (3W, 4-8Ω)"},
            {"number": 6, "name": "DAC_R/DAC_L", "type": "analog", "description": "Line out to an external amp"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "RX", "to_pin": "D11", "note": "1kΩ in series cuts the noise"},
                    {"from_pin": "TX", "to_pin": "D10", "note": ""},
                    {"from_pin": "SPK1/SPK2", "to_pin": "Speaker", "note": "Never ground either speaker terminal"},
                ],
                "notes": [
                    "Files must be named 0001.mp3, 0002.mp3 … inside an /mp3 folder.",
                    "Copy them in order — the module plays by index, not by name.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Play track 1 on demand",
                "libraries": ["DFRobotDFPlayerMini", "SoftwareSerial"],
                "code": """#include <SoftwareSerial.h>
#include <DFRobotDFPlayerMini.h>

SoftwareSerial playerSerial(10, 11);   // RX, TX
DFRobotDFPlayerMini player;

void setup() {
  Serial.begin(9600);
  playerSerial.begin(9600);
  if (!player.begin(playerSerial)) {
    Serial.println("DFPlayer not responding — check wiring and the SD card");
    while (true) delay(10);
  }
  player.volume(22);                   // 0..30
  player.play(1);                      // /mp3/0001.mp3
}

void loop() {}
""",
            },
        },
    },
    {
        "id": "max9814_mic",
        "type": "audio",
        "name": "MAX9814 Microphone Amplifier",
        "aliases": ["max9814", "microphone module", "mic amplifier", "electret mic"],
        "description": "Electret microphone with automatic gain control — sound-level "
        "sensing, clap switches, noise logging.",
        "package": "Module",
        "tags": ["audio", "analog", "sensor"],
        "pins": [
            {"number": 1, "name": "VDD", "type": "power", "description": "2.7-5.5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "OUT", "type": "analog", "description": "Audio biased at ~1.25V"},
            {"number": 4, "name": "GAIN", "type": "analog", "description": "Open=60dB, GND=50dB, VDD=40dB"},
            {"number": 5, "name": "AR", "type": "analog", "description": "Attack/release timing"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VDD", "to_pin": "3V3", "note": "Use a clean supply — it picks up noise"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "GPIO34", "note": "ADC1 input"},
                ],
                "notes": ["Sample fast and track peak-to-peak; a single reading tells you nothing."],
            },
        },
        "code": {
            "esp32": {
                "title": "Measure sound level",
                "libraries": [],
                "code": """const int MIC_PIN = 34;
const int WINDOW_MS = 50;

void setup() {
  Serial.begin(115200);
}

void loop() {
  unsigned long start = millis();
  int high = 0, low = 4095;
  while (millis() - start < WINDOW_MS) {
    int sample = analogRead(MIC_PIN);
    if (sample > high) high = sample;
    if (sample < low) low = sample;
  }
  int amplitude = high - low;          // peak-to-peak
  Serial.println(amplitude);
  delay(50);
}
""",
            },
        },
    },
    {
        "id": "inmp441",
        "type": "audio",
        "name": "INMP441 I2S Microphone",
        "aliases": ["inmp441", "i2s microphone", "digital microphone", "mems mic"],
        "description": "MEMS microphone with a digital I2S output — no analog noise, "
        "and the right choice for voice recognition on an ESP32.",
        "package": "Module",
        "tags": ["audio", "i2s", "iot", "ai"],
        "pins": [
            {"number": 1, "name": "VDD", "type": "power", "description": "1.8-3.3V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SD", "type": "signal", "description": "Serial data out"},
            {"number": 4, "name": "SCK", "type": "signal", "description": "Bit clock"},
            {"number": 5, "name": "WS", "type": "signal", "description": "Word select (L/R clock)"},
            {"number": 6, "name": "L/R", "type": "digital", "description": "Channel select: GND=left"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VDD", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SCK", "to_pin": "GPIO14", "note": "I2S bit clock"},
                    {"from_pin": "WS", "to_pin": "GPIO15", "note": "I2S word select"},
                    {"from_pin": "SD", "to_pin": "GPIO32", "note": "I2S data in"},
                    {"from_pin": "L/R", "to_pin": "GND", "note": "Left channel"},
                ],
                "notes": ["Samples arrive as 32-bit words with the audio in the upper bits."],
            },
        },
        "code": {},
    },
    {
        "id": "max98357a",
        "type": "audio",
        "name": "MAX98357A I2S Amplifier",
        "aliases": ["max98357a", "i2s amplifier", "i2s dac", "class d amplifier"],
        "description": "I2S digital-to-analog converter and 3W class-D amplifier in "
        "one — internet radio, TTS voice output, sound effects.",
        "package": "Module",
        "tags": ["audio", "i2s", "iot"],
        "pins": [
            {"number": 1, "name": "VIN", "type": "power", "description": "2.5-5.5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "DIN", "type": "signal", "description": "I2S data in"},
            {"number": 4, "name": "BCLK", "type": "signal", "description": "Bit clock"},
            {"number": 5, "name": "LRC", "type": "signal", "description": "Left/right clock"},
            {"number": 6, "name": "GAIN", "type": "analog", "description": "Sets 3-15dB"},
            {"number": 7, "name": "SPK+/-", "type": "signal", "description": "Speaker output (4-8Ω)"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VIN", "to_pin": "5V", "note": "5V gives the full 3W"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "BCLK", "to_pin": "GPIO27", "note": ""},
                    {"from_pin": "LRC", "to_pin": "GPIO26", "note": ""},
                    {"from_pin": "DIN", "to_pin": "GPIO25", "note": ""},
                ],
                "notes": ["Speaker outputs are bridged — never connect either side to ground."],
            },
        },
        "code": {},
    },
    {
        "id": "pam8403",
        "type": "audio",
        "name": "PAM8403 Stereo Amplifier",
        "aliases": ["pam8403", "audio amplifier", "class d amp module", "3w amplifier"],
        "description": "Tiny 2x3W class-D amplifier for analog audio — pair it with a "
        "DAC or an MP3 module to drive real speakers.",
        "package": "Module",
        "tags": ["audio", "analog"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "2.5-5.5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "L IN / R IN", "type": "analog", "description": "Line-level inputs"},
            {"number": 4, "name": "L OUT / R OUT", "type": "signal", "description": "Speaker outputs"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "Add 470µF — bass makes it dip"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "L IN / R IN", "to_pin": "Audio source", "note": "Through a 10µF coupling cap"},
                ],
                "notes": ["Bridged outputs again: do not ground the negative speaker terminal."],
            },
        },
        "code": {},
    },
    {
        "id": "isd1820",
        "type": "audio",
        "name": "ISD1820 Voice Recorder Module",
        "aliases": ["isd1820", "voice recorder module", "sound recorder"],
        "description": "Records up to 20 seconds of audio to on-board memory and plays "
        "it back at the press of a button — talking props and doorbells.",
        "package": "Module",
        "tags": ["audio", "storage"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "REC", "type": "digital", "description": "HIGH while recording"},
            {"number": 4, "name": "PLAYE", "type": "digital", "description": "Edge trigger — plays the whole clip"},
            {"number": 5, "name": "PLAYL", "type": "digital", "description": "Level trigger — plays while high"},
            {"number": 6, "name": "SP+/SP-", "type": "signal", "description": "8Ω speaker"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "PLAYE", "to_pin": "D7", "note": "Pulse HIGH to play"},
                    {"from_pin": "REC", "to_pin": "D8", "note": "Hold HIGH to record"},
                ],
                "notes": ["Recording time is set by the on-board resistor — 20s stock."],
            },
        },
        "code": {},
    },
]
