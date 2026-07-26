"""Environmental sensors: temperature, humidity, pressure, gas, light, water."""
from __future__ import annotations

from typing import List

ITEMS: List[dict] = [
    {
        "id": "dht11",
        "type": "sensor",
        "name": "DHT11 Temperature & Humidity Sensor",
        "aliases": ["dht11", "dht", "temperature humidity sensor"],
        "description": "A low-cost digital temperature and humidity sensor using a "
        "single-wire protocol. DHT22 is the higher-precision sibling.",
        "package": "4-pin module",
        "tags": ["sensor", "digital", "temperature", "humidity", "beginner"],
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
                "notes": ["Read no faster than once per second."],
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
        "id": "dht22",
        "type": "sensor",
        "name": "DHT22 Temperature & Humidity Sensor",
        "aliases": ["dht22", "am2302", "rht03"],
        "description": "Higher-accuracy sibling of the DHT11: -40 to +80°C, 0-100% RH, "
        "one decimal place of resolution.",
        "package": "4-pin module",
        "tags": ["sensor", "digital", "temperature", "humidity", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "DATA", "type": "digital", "description": "Single-wire data, 10k pull-up"},
            {"number": 3, "name": "NC", "type": "nc", "description": "Not connected"},
            {"number": 4, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "DATA", "to_pin": "GPIO4", "note": "10kΩ pull-up to 3V3"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Needs 2s between readings."],
            },
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "DATA", "to_pin": "D2", "note": "10kΩ pull-up to 5V"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "esp32": {
                "title": "Publish temperature to MQTT every minute",
                "libraries": ["DHT sensor library (Adafruit)", "PubSubClient", "WiFi"],
                "code": """#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHT_PIN 4
#define DHT_TYPE DHT22

const char* WIFI_SSID = "your-wifi";
const char* WIFI_PASS = "your-password";
const char* MQTT_HOST = "broker.hivemq.com";

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient net;
PubSubClient mqtt(net);

void connectAll() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) delay(400);
  mqtt.setServer(MQTT_HOST, 1883);
  while (!mqtt.connected()) mqtt.connect("esp32-dht22");
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  connectAll();
}

void loop() {
  if (!mqtt.connected()) connectAll();
  mqtt.loop();

  float tempC = dht.readTemperature();
  float humidity = dht.readHumidity();
  if (!isnan(tempC)) {
    char payload[64];
    snprintf(payload, sizeof(payload),
             "{\\"temp\\":%.1f,\\"humidity\\":%.1f}", tempC, humidity);
    mqtt.publish("home/livingroom/climate", payload);
    Serial.println(payload);
  }
  delay(60000);
}
""",
            },
        },
    },
    {
        "id": "ds18b20",
        "type": "sensor",
        "name": "DS18B20 Digital Thermometer",
        "aliases": ["ds18b20", "1-wire temperature", "waterproof temperature sensor", "onewire"],
        "description": "One-wire digital thermometer, ±0.5°C, available as a "
        "waterproof stainless probe. Many sensors share a single data pin.",
        "package": "TO-92 / waterproof probe",
        "tags": ["sensor", "temperature", "onewire", "iot"],
        "pins": [
            {"number": 1, "name": "GND", "type": "ground", "description": "Ground (black wire)"},
            {"number": 2, "name": "DQ", "type": "digital", "description": "1-Wire data (yellow), 4.7k pull-up"},
            {"number": 3, "name": "VDD", "type": "power", "description": "3-5.5V (red wire)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VDD", "to_pin": "5V", "note": ""},
                    {"from_pin": "DQ", "to_pin": "D2", "note": "4.7kΩ pull-up to VDD — required"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["Every probe has a unique 64-bit address, so they can share one pin."],
            },
            "esp32": {
                "connections": [
                    {"from_pin": "VDD", "to_pin": "3V3", "note": ""},
                    {"from_pin": "DQ", "to_pin": "GPIO4", "note": "4.7kΩ pull-up to 3V3"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "uno": {
                "title": "Read every DS18B20 on the bus",
                "libraries": ["OneWire", "DallasTemperature"],
                "code": """#include <OneWire.h>
#include <DallasTemperature.h>

const int ONE_WIRE_PIN = 2;

OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(9600);
  sensors.begin();
  Serial.print("Sensors found: ");
  Serial.println(sensors.getDeviceCount());
}

void loop() {
  sensors.requestTemperatures();
  for (int i = 0; i < sensors.getDeviceCount(); i++) {
    Serial.print("Sensor ");
    Serial.print(i);
    Serial.print(": ");
    Serial.print(sensors.getTempCByIndex(i));
    Serial.println(" C");
  }
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "lm35",
        "type": "sensor",
        "name": "LM35 Analog Temperature Sensor",
        "aliases": ["lm35", "tmp36", "analog temperature sensor"],
        "description": "Outputs 10mV per °C straight from a three-pin TO-92 package — "
        "no library, no protocol, just analogRead.",
        "package": "TO-92",
        "tags": ["sensor", "analog", "temperature", "beginner"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "4-30V"},
            {"number": 2, "name": "OUT", "type": "analog", "description": "10mV per °C"},
            {"number": 3, "name": "GND", "type": "ground", "description": "Ground"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "OUT", "to_pin": "A0", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                ],
                "notes": ["TMP36 looks identical but offsets by 500mV — check before wiring."],
            },
        },
        "code": {
            "uno": {
                "title": "Read an LM35 in °C",
                "libraries": [],
                "code": """const int LM35_PIN = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int raw = analogRead(LM35_PIN);
  float millivolts = raw * (5000.0 / 1023.0);
  float celsius = millivolts / 10.0;
  Serial.print(celsius, 1);
  Serial.println(" C");
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "bmp280",
        "type": "sensor",
        "name": "BMP280 Pressure & Temperature Sensor",
        "aliases": ["bmp280", "bmp180", "barometer", "pressure sensor", "gy-bmp280"],
        "description": "Barometric pressure and temperature over I2C or SPI. Precise "
        "enough to measure altitude changes of about a metre.",
        "package": "Module (GY-BMP280)",
        "tags": ["sensor", "i2c", "pressure", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V (modules usually have a regulator)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 5, "name": "CSB", "type": "spi", "description": "SPI chip select (tie high for I2C)"},
            {"number": 6, "name": "SDO", "type": "digital", "description": "Address select: GND=0x76, VCC=0x77"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                ],
                "notes": ["Default address is 0x76 on most breakout boards."],
            },
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "Module regulator handles 5V; bare chips do not"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "A4", "note": ""},
                    {"from_pin": "SCL", "to_pin": "A5", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "esp32": {
                "title": "Read pressure, temperature and altitude",
                "libraries": ["Adafruit BMP280 Library"],
                "code": """#include <Adafruit_BMP280.h>

Adafruit_BMP280 bmp;

void setup() {
  Serial.begin(115200);
  if (!bmp.begin(0x76)) {
    Serial.println("BMP280 not found — check wiring and address");
    while (1) delay(10);
  }
}

void loop() {
  Serial.printf("%.2f C  %.1f hPa  %.1f m\\n",
                bmp.readTemperature(),
                bmp.readPressure() / 100.0,
                bmp.readAltitude(1013.25));
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "bme280",
        "type": "sensor",
        "name": "BME280 Environmental Sensor",
        "aliases": ["bme280", "environmental sensor", "temperature humidity pressure"],
        "description": "Temperature, humidity and pressure in one I2C chip — the "
        "standard sensor for a weather station or an indoor-climate node.",
        "package": "Module (GY-BME280)",
        "tags": ["sensor", "i2c", "iot", "weather"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
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
                "notes": ["Address 0x76 or 0x77. A BMP280 looks identical but has no humidity."],
            },
        },
        "code": {
            "esp32": {
                "title": "Weather node with deep sleep",
                "libraries": ["Adafruit BME280 Library", "Adafruit Unified Sensor"],
                "code": """#include <Adafruit_BME280.h>

#define SLEEP_MINUTES 10

Adafruit_BME280 bme;

void setup() {
  Serial.begin(115200);
  if (!bme.begin(0x76)) {
    Serial.println("BME280 not found");
  } else {
    Serial.printf("%.1f C  %.1f %%RH  %.1f hPa\\n",
                  bme.readTemperature(),
                  bme.readHumidity(),
                  bme.readPressure() / 100.0);
  }
  // Sleep between readings — a battery node can run for months this way.
  esp_sleep_enable_timer_wakeup(SLEEP_MINUTES * 60ULL * 1000000ULL);
  esp_deep_sleep_start();
}

void loop() {}
""",
            },
        },
    },
    {
        "id": "aht10",
        "type": "sensor",
        "name": "AHT10 / AHT20 Humidity Sensor",
        "aliases": ["aht10", "aht20", "asair humidity sensor"],
        "description": "Small, accurate I2C temperature and humidity sensor that has "
        "largely replaced the DHT series in new designs.",
        "package": "Module",
        "tags": ["sensor", "i2c", "humidity", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "2.2-5.5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
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
                "notes": ["Fixed address 0x38 — only one per bus without a multiplexer."],
            },
        },
        "code": {
            "esp32": {
                "title": "Read AHT10 temperature and humidity",
                "libraries": ["Adafruit AHTX0"],
                "code": """#include <Adafruit_AHTX0.h>

Adafruit_AHTX0 aht;

void setup() {
  Serial.begin(115200);
  if (!aht.begin()) {
    Serial.println("AHT10 not found");
    while (1) delay(10);
  }
}

void loop() {
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);
  Serial.printf("%.1f C  %.1f %%RH\\n",
                temp.temperature, humidity.relative_humidity);
  delay(2000);
}
""",
            },
        },
    },
    {
        "id": "bh1750",
        "type": "sensor",
        "name": "BH1750 Light Sensor",
        "aliases": ["bh1750", "gy-302", "lux sensor", "digital light sensor"],
        "description": "Measures illuminance directly in lux over I2C — far more "
        "useful than an LDR when the number has to mean something.",
        "package": "Module (GY-302)",
        "tags": ["sensor", "i2c", "light", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SCL", "type": "i2c", "description": "I2C clock"},
            {"number": 4, "name": "SDA", "type": "i2c", "description": "I2C data"},
            {"number": 5, "name": "ADDR", "type": "digital", "description": "Address select (0x23 / 0x5C)"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SDA", "to_pin": "GPIO21", "note": ""},
                    {"from_pin": "SCL", "to_pin": "GPIO22", "note": ""},
                    {"from_pin": "ADDR", "to_pin": "GND", "note": "Address 0x23"},
                ],
                "notes": [],
            },
        },
        "code": {
            "esp32": {
                "title": "Read illuminance in lux",
                "libraries": ["BH1750"],
                "code": """#include <Wire.h>
#include <BH1750.h>

BH1750 meter;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  meter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
}

void loop() {
  float lux = meter.readLightLevel();
  Serial.printf("%.1f lx\\n", lux);
  delay(1000);
}
""",
            },
        },
    },
    {
        "id": "mq2",
        "type": "sensor",
        "name": "MQ-2 Gas & Smoke Sensor",
        "aliases": ["mq2", "mq-2", "gas sensor", "smoke sensor", "lpg sensor"],
        "description": "Heated tin-dioxide sensor for LPG, propane, methane and smoke. "
        "Analog output plus an adjustable digital threshold.",
        "package": "Module",
        "tags": ["sensor", "analog", "gas", "safety"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V — the heater draws ~150mA"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "AOUT", "type": "analog", "description": "Analog concentration"},
            {"number": 4, "name": "DOUT", "type": "digital", "description": "Goes low past the trim-pot threshold"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "Needs a real 5V supply, not a weak USB hub"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "AOUT", "to_pin": "A0", "note": ""},
                    {"from_pin": "DOUT", "to_pin": "D2", "note": "Optional alarm trigger"},
                ],
                "notes": [
                    "Let it burn in for 24-48h when new, and warm up ~3 min on each boot.",
                    "The MQ family is not a certified safety device — treat it as an indicator.",
                ],
            },
        },
        "code": {
            "uno": {
                "title": "Smoke alarm with a buzzer",
                "libraries": [],
                "code": """const int GAS_PIN = A0;
const int BUZZER_PIN = 8;
const int ALARM_LEVEL = 400;    // calibrate in clean air first

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(9600);
  delay(180000UL / 60);          // short warm-up; 3 min is ideal
}

void loop() {
  int level = analogRead(GAS_PIN);
  Serial.println(level);
  digitalWrite(BUZZER_PIN, level > ALARM_LEVEL ? HIGH : LOW);
  delay(500);
}
""",
            },
        },
    },
    {
        "id": "mq135",
        "type": "sensor",
        "name": "MQ-135 Air Quality Sensor",
        "aliases": ["mq135", "mq-135", "air quality sensor", "co2 sensor module"],
        "description": "Broad-spectrum air-quality sensor (ammonia, benzene, smoke, "
        "CO2-ish). Good for relative trends, not for absolute ppm.",
        "package": "Module",
        "tags": ["sensor", "analog", "gas", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "AOUT", "type": "analog", "description": "Analog output"},
            {"number": 4, "name": "DOUT", "type": "digital", "description": "Threshold output"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": "Heater needs 5V"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "AOUT", "to_pin": "GPIO34", "note": "Divide to stay under 3.3V"},
                ],
                "notes": ["The analog output can exceed 3.3V — use a 2:1 divider into the ESP32."],
            },
        },
        "code": {},
    },
    {
        "id": "mhz19",
        "type": "sensor",
        "name": "MH-Z19 CO2 Sensor",
        "aliases": ["mh-z19", "mhz19", "mh-z19b", "ndir co2 sensor", "co2 sensor"],
        "description": "True NDIR CO2 sensor (0-5000 ppm) over UART or PWM — the "
        "reliable way to log indoor air quality.",
        "package": "Module",
        "tags": ["sensor", "uart", "iot", "air"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V, 150mA peak"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "TX", "type": "uart", "description": "Sensor transmit -> MCU RX"},
            {"number": 4, "name": "RX", "type": "uart", "description": "Sensor receive <- MCU TX"},
            {"number": 5, "name": "PWM", "type": "pwm", "description": "Alternative PWM output"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "TX", "to_pin": "GPIO16", "note": "ESP32 RX2"},
                    {"from_pin": "RX", "to_pin": "GPIO17", "note": "ESP32 TX2"},
                ],
                "notes": [
                    "Logic is 3.3V-friendly even though the supply is 5V.",
                    "Let it warm up 3 minutes before trusting a reading.",
                ],
            },
        },
        "code": {
            "esp32": {
                "title": "Read CO2 over UART",
                "libraries": ["MH-Z19"],
                "code": """#include <MHZ19.h>

MHZ19 sensor;
HardwareSerial mhz(2);          // UART2: RX=16, TX=17

void setup() {
  Serial.begin(115200);
  mhz.begin(9600, SERIAL_8N1, 16, 17);
  sensor.begin(mhz);
  sensor.autoCalibration(true);
}

void loop() {
  int co2 = sensor.getCO2();
  Serial.printf("CO2: %d ppm  (sensor %d C)\\n", co2, sensor.getTemperature());
  delay(10000);
}
""",
            },
        },
    },
    {
        "id": "soil_moisture",
        "type": "sensor",
        "name": "Capacitive Soil Moisture Sensor",
        "aliases": ["soil moisture sensor", "capacitive soil sensor", "hygrometer", "yl-69"],
        "description": "Measures how wet the soil is. Capacitive versions do not "
        "corrode like the older resistive YL-69 probes.",
        "package": "Probe module",
        "tags": ["sensor", "analog", "garden", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "AOUT", "type": "analog", "description": "Lower voltage = wetter"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "AOUT", "to_pin": "GPIO34", "note": "ADC1 channel"},
                ],
                "notes": ["Calibrate twice: dry in air, then fully submerged."],
            },
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "AOUT", "to_pin": "A0", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {
            "esp32": {
                "title": "Auto-watering trigger",
                "libraries": [],
                "code": """const int SOIL_PIN = 34;
const int PUMP_PIN = 26;
const int DRY_VALUE = 3200;      // reading in dry air
const int WET_VALUE = 1400;      // reading in water

void setup() {
  pinMode(PUMP_PIN, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  int raw = analogRead(SOIL_PIN);
  int percent = map(raw, DRY_VALUE, WET_VALUE, 0, 100);
  percent = constrain(percent, 0, 100);
  Serial.printf("Soil moisture: %d%%\\n", percent);

  if (percent < 30) {
    digitalWrite(PUMP_PIN, HIGH);   // water for 3 seconds
    delay(3000);
    digitalWrite(PUMP_PIN, LOW);
  }
  delay(60000);
}
""",
            },
        },
    },
    {
        "id": "rain_sensor",
        "type": "sensor",
        "name": "Rain / Water Detection Sensor",
        "aliases": ["rain sensor", "water sensor", "raindrop sensor", "yl-83"],
        "description": "A comb-patterned board whose resistance drops when water "
        "bridges the traces — rain alarms and leak detection.",
        "package": "Plate + comparator module",
        "tags": ["sensor", "analog", "water"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "AOUT", "type": "analog", "description": "Analog wetness"},
            {"number": 4, "name": "DOUT", "type": "digital", "description": "Threshold output"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": "Power it only while sampling to slow corrosion"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "AOUT", "to_pin": "A0", "note": ""},
                    {"from_pin": "DOUT", "to_pin": "D2", "note": ""},
                ],
                "notes": ["Driving VCC from a GPIO pin makes the plate last far longer."],
            },
        },
        "code": {},
    },
    {
        "id": "water_level",
        "type": "sensor",
        "name": "Water Level Sensor",
        "aliases": ["water level sensor", "liquid level sensor", "tank level sensor"],
        "description": "A ladder of exposed traces: the more of it is submerged, the "
        "higher the analog output. Cheap tank-level indication.",
        "package": "Strip module",
        "tags": ["sensor", "analog", "water"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "SIG", "type": "analog", "description": "Analog level"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "D7", "note": "Power from a GPIO to reduce corrosion"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SIG", "to_pin": "A0", "note": ""},
                ],
                "notes": ["Not for drinking water — the traces corrode into the liquid."],
            },
        },
        "code": {},
    },
    {
        "id": "yfs201",
        "type": "sensor",
        "name": "YF-S201 Water Flow Sensor",
        "aliases": ["yf-s201", "flow sensor", "water flow meter", "hall flow sensor"],
        "description": "A pinwheel and a hall sensor in a plastic housing: pulses out "
        "at roughly 7.5 Hz per litre/minute.",
        "package": "1/2\" inline",
        "tags": ["sensor", "digital", "water", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5-18V (red)"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground (black)"},
            {"number": 3, "name": "SIG", "type": "digital", "description": "Pulse output (yellow)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "SIG", "to_pin": "D2", "note": "Interrupt-capable pin, 10kΩ pull-up"},
                ],
                "notes": ["Mount it horizontally with the arrow pointing downstream."],
            },
        },
        "code": {
            "uno": {
                "title": "Measure water flow in L/min",
                "libraries": [],
                "code": """const int FLOW_PIN = 2;
volatile unsigned int pulses = 0;

void countPulse() { pulses++; }

void setup() {
  pinMode(FLOW_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(FLOW_PIN), countPulse, FALLING);
  Serial.begin(9600);
}

void loop() {
  pulses = 0;
  delay(1000);
  noInterrupts();
  unsigned int count = pulses;
  interrupts();

  float litresPerMinute = count / 7.5;
  Serial.print(litresPerMinute, 2);
  Serial.println(" L/min");
}
""",
            },
        },
    },
    {
        "id": "ph_sensor",
        "type": "sensor",
        "name": "pH Sensor (PH-4502C)",
        "aliases": ["ph sensor", "ph meter", "ph-4502c", "hydroponics sensor"],
        "description": "Glass electrode plus a signal-conditioning board for measuring "
        "the pH of a liquid — hydroponics, aquariums, aquaponics.",
        "package": "Probe + BNC module",
        "tags": ["sensor", "analog", "water", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "PO", "type": "analog", "description": "Analog pH output"},
            {"number": 4, "name": "TO", "type": "analog", "description": "Temperature output (optional)"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "PO", "to_pin": "A0", "note": ""},
                ],
                "notes": [
                    "Calibrate with pH 4.0 and 7.0 buffer solutions.",
                    "Keep the probe wet in storage solution or it dies.",
                ],
            },
        },
        "code": {},
    },
    {
        "id": "tds_sensor",
        "type": "sensor",
        "name": "TDS / Conductivity Sensor",
        "aliases": ["tds sensor", "conductivity sensor", "water quality sensor", "ec sensor"],
        "description": "Measures dissolved solids in water (ppm) by conductivity — "
        "nutrient strength in hydroponics, filter monitoring.",
        "package": "Probe + module",
        "tags": ["sensor", "analog", "water", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5.5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "AOUT", "type": "analog", "description": "Analog TDS output"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3V3", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "AOUT", "to_pin": "GPIO35", "note": "ADC1 channel"},
                ],
                "notes": ["Compensate for temperature — conductivity climbs about 2%/°C."],
            },
        },
        "code": {},
    },
    {
        "id": "uv_sensor",
        "type": "sensor",
        "name": "UV Sensor (ML8511 / GUVA-S12SD)",
        "aliases": ["uv sensor", "ml8511", "guva-s12sd", "ultraviolet sensor"],
        "description": "Analog UV-intensity sensor used to compute a UV index — a "
        "natural add-on for a weather station.",
        "package": "Module",
        "tags": ["sensor", "analog", "light", "weather"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "3.3-5V"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "OUT", "type": "analog", "description": "Analog UV level"},
            {"number": 4, "name": "EN", "type": "digital", "description": "Enable, tie to VCC"},
        ],
        "wiring": {
            "uno": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "3.3V", "note": "Also feed 3.3V to AREF for accuracy"},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "OUT", "to_pin": "A0", "note": ""},
                    {"from_pin": "EN", "to_pin": "3.3V", "note": ""},
                ],
                "notes": [],
            },
        },
        "code": {},
    },
    {
        "id": "pms5003",
        "type": "sensor",
        "name": "PMS5003 Particulate Sensor",
        "aliases": ["pms5003", "pms7003", "dust sensor", "pm2.5 sensor", "air particle sensor"],
        "description": "Laser particle counter reporting PM1.0, PM2.5 and PM10 over "
        "UART — the sensor behind most DIY air-quality monitors.",
        "package": "Module",
        "tags": ["sensor", "uart", "air", "iot"],
        "pins": [
            {"number": 1, "name": "VCC", "type": "power", "description": "5V, ~100mA with the fan running"},
            {"number": 2, "name": "GND", "type": "ground", "description": "Ground"},
            {"number": 3, "name": "TX", "type": "uart", "description": "Data out (3.3V logic)"},
            {"number": 4, "name": "RX", "type": "uart", "description": "Commands in"},
            {"number": 5, "name": "SET", "type": "digital", "description": "Low = sleep"},
            {"number": 6, "name": "RESET", "type": "digital", "description": "Active low reset"},
        ],
        "wiring": {
            "esp32": {
                "connections": [
                    {"from_pin": "VCC", "to_pin": "5V (VIN)", "note": ""},
                    {"from_pin": "GND", "to_pin": "GND", "note": ""},
                    {"from_pin": "TX", "to_pin": "GPIO16", "note": "ESP32 RX2"},
                    {"from_pin": "RX", "to_pin": "GPIO17", "note": "ESP32 TX2"},
                ],
                "notes": ["Give it 30s of fan time before reading, then sleep it to save the fan."],
            },
        },
        "code": {
            "esp32": {
                "title": "Read PM2.5 and PM10",
                "libraries": ["PMS Library"],
                "code": """#include <PMS.h>

HardwareSerial pmsSerial(2);     // RX=16, TX=17
PMS pms(pmsSerial);
PMS::DATA data;

void setup() {
  Serial.begin(115200);
  pmsSerial.begin(9600, SERIAL_8N1, 16, 17);
  pms.passiveMode();
}

void loop() {
  pms.wakeUp();
  delay(30000);                  // let the fan clear the chamber
  pms.requestRead();
  if (pms.readUntil(data)) {
    Serial.printf("PM1.0 %u  PM2.5 %u  PM10 %u ug/m3\\n",
                  data.PM_AE_UG_1_0, data.PM_AE_UG_2_5, data.PM_AE_UG_10_0);
  }
  pms.sleep();
  delay(5 * 60000);
}
""",
            },
        },
    },
]
