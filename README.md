# AI Electronics Scanner

Point your phone at an electronic component — a resistor, IC, sensor, or module —
and get its **pinout**, a **wiring diagram**, and **ready-to-flash Arduino/ESP32
code** in seconds. Built for makers and hobbyists who want to skip the datasheet
hunt and start building.

| | |
|---|---|
| **App** | Flutter (Android APK; iOS-ready codebase) — **AI runs fully on-device, zero hosting cost** |
| **Recognition** | Google ML Kit OCR (offline) + pure-Dart resistor colour-band decoder |
| **Website** | GitHub Pages (free) — APK download + subscriptions |
| **Backend (optional)** | Python · FastAPI · OpenCV · Tesseract — same pipeline, for future server-side scale |
| **Payments** | **GCash** via PayMongo — Pro activates automatically, no admin approval |
| **Monetisation** | Freemium — free scans & pinouts, Pro (₱199/mo, ₱1,499/yr, ₱2,999 lifetime) for wiring, code gen, unlimited scans & full history |

**Website:** https://engrjhon3-prog.github.io/AI-Electronics-Scan/

---

## How it works

```
┌──────────────────────── Flutter app (all on-device) ────────────────────────┐
│  photo ─► 1. ML Kit OCR reads silk-screen labels (NE555, HC-SR04, …)        │
│           2. Dart colour-band decoder reads resistor values (10kΩ ±5%)      │
│               ─► ranked matches ─► bundled knowledge base                   │
│                   (pinouts · wiring SVGs · Arduino/ESP32 code)              │
└─────────────────────────────────────────────────────────────────────────────┘
```

Everything works offline: the component knowledge base (with pre-rendered
wiring diagrams) is exported from the backend into `frontend/assets/components.json`
by `backend/scripts/export_assets.py` and ships inside the APK.

The Python backend implements the identical pipeline server-side (Tesseract
OCR + OpenCV colour-band decoding) and remains in the repo as an optional
upgrade path — e.g. for a future CNN classifier too heavy to run on-device.

## Repository layout

```
backend/
  app/components/catalog/   knowledge base, one module per category
  app/payments/             GCash checkout, webhooks, entitlement writes
  app/vision/               OCR + resistor colour-band pipeline
frontend/    Flutter app
website/     GitHub Pages site (APK download, account, payment result pages)
docs/        Deployment, Firebase and payment guides
.github/     CI: tests + automatic APK builds
```

## Quick start — backend (optional)

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Interactive API docs: `http://localhost:8000/docs`

Run tests: `pip install pytest httpx && pytest -q`

### Docker (what you'd run on Vast.ai)

```bash
cd backend
docker build -t electronics-scanner-api .
docker run -p 8000:8000 electronics-scanner-api
```

See **[docs/DEPLOY_VASTAI.md](docs/DEPLOY_VASTAI.md)** for the full Vast.ai guide.

## Quick start — app (APK)

**You don't need a computer.** Every push to this repo triggers a GitHub Actions
build that produces an installable APK:

1. Go to the repo's **Releases** page → **"Latest APK build"**.
2. Download `ai-electronics-scanner.apk` on your phone and install it
   (allow "unknown sources" when prompted).

Or just point people at the website — it links the same APK:
https://engrjhon3-prog.github.io/AI-Electronics-Scan/

(The optional `API_BASE_URL` repo variable only matters if you later deploy
the server-side pipeline; the app itself is fully offline.)

## Freemium model

| Feature | Free | Pro |
|---|---|---|
| Component scans | 20 / month | Unlimited |
| Pinout reference | ✅ | ✅ |
| Component catalog | ✅ | ✅ |
| Wiring diagrams | — | ✅ |
| Arduino/ESP32 code generation | — | ✅ |
| Scan history | Last 3 | Full |

### Paying with GCash (no admin approval)

The paywall creates a hosted GCash checkout, the gateway confirms the payment to
`/api/v1/payments/webhook`, and the backend writes the Firestore entitlement the
app is already listening to — so Pro switches on by itself, usually within a
couple of seconds. If the callback is ever lost, the app's `/payments/status`
polling makes the backend re-check the gateway and activate anyway.

| Plan | Price |
|---|---|
| Monthly | ₱199 |
| Yearly | ₱1,499 |
| Lifetime | ₱2,999 |

Prices, plans and the gateway all come from the server
(`GET /api/v1/payments/config`), so changing them needs no new APK. Setup —
gateway keys, Firebase Admin credentials, testing with the built-in mock
gateway — is in **[docs/GCASH_PAYMENTS.md](docs/GCASH_PAYMENTS.md)**.

Enforcement stays server-side: wiring and code endpoints return **HTTP 402**
without a live entitlement (`backend/app/main.py::_require_premium` accepts a
Firebase ID token whose account has one).

## Component knowledge base

**179 curated components**, IoT-heavy, organised into browsable categories:

| Category | Count | Examples |
|---|---|---|
| Passives | 16 | resistors (live colour-band decoding), capacitors, inductors, crystals, LDR, NTC |
| Semiconductors | 17 | LEDs, WS2812B, diodes, MOSFETs, transistors, optocouplers, TRIAC |
| ICs | 16 | NE555, LM358, 74HC595, ULN2003, L293D, MCP23017, ADS1115, TCA9548A |
| Environment sensors | 19 | DHT11/22, DS18B20, BME280, BH1750, MQ-2, MH-Z19 CO2, PMS5003, soil, pH, TDS |
| Motion & distance | 22 | HC-SR04, PIR, MPU-6050/9250, VL53L0X, HX711, encoders, hall, ACS712 |
| Wireless & IoT | 17 | ESP-01, nRF24L01, LoRa SX1278, HC-12, HM-10 BLE, SIM800L, SIM7600 4G, NEO-6M GPS, RC522, PN532, W5500, RS-485, CAN, ESP32-CAM |
| Displays | 11 | SSD1306, SH1106, 16x2/20x4 LCD, ST7735, ILI9341, MAX7219, TM1637, e-paper |
| Motors & actuators | 16 | SG90/MG996R servos, 28BYJ-48, NEMA 17 + A4988, L298N, relays, solenoids, pumps, ESC, Peltier |
| Power | 12 | 7805, AMS1117, LM2596, MT3608, TP4056, 18650, solar, INA219, PZEM-004T |
| Boards | 12 | Uno, Nano, Mega, ESP32, ESP32-S3, NodeMCU, D1 Mini, Pico W, Raspberry Pi, Blue Pill, ATtiny85, XIAO |
| Audio | 8 | buzzers, DFPlayer Mini, MAX9814, INMP441 I2S mic, MAX98357A, PAM8403 |
| Storage & interface | 13 | DS3231 RTC, microSD, EEPROM, keypad, switches, connectors |

Most entries carry pinouts, per-board wiring (Uno and/or ESP32) and a working
sketch — including IoT recipes such as MQTT publishing, LoRa nodes, deep-sleep
battery sensors and Wi-Fi relay control.

Adding a component = appending one dict to the right module in
`backend/app/components/catalog/`, then re-running
`python scripts/export_assets.py` to refresh the bundled asset.

## Safety

Wiring suggestions are a starting point — always verify voltage levels and
polarity before powering a circuit. Never work with mains voltage unless
qualified.
