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
| **Monetisation** | Freemium — free scans & pinouts, Pro (~$3–5/mo) for wiring, code gen, unlimited scans & full history |

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
backend/     Python FastAPI service (vision + knowledge base + generators)
frontend/    Flutter app
docs/        Deployment & architecture guides
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

Enforcement is server-side: the wiring and code endpoints return **HTTP 402**
without a valid entitlement. The current build ships with a *demo* entitlement
(the paywall's Subscribe button unlocks locally, no charge) so the full flow can
be tested end-to-end. For production, wire the paywall to Google Play Billing /
RevenueCat and verify receipts in `backend/app/main.py::_require_premium`.

## Component knowledge base

Ships with 14 curated components: 5mm LED, resistor (with live colour-band
decoding), push button, potentiometer, NE555, DHT11, HC-SR04, HC-SR501 PIR,
SG90 servo, SSD1306 OLED, MPU-6050, HC-05 Bluetooth, relay module, L293D.

Adding a component = appending one dict in
`backend/app/components/database.py` (pins + wiring + code). No other changes needed.

## Safety

Wiring suggestions are a starting point — always verify voltage levels and
polarity before powering a circuit. Never work with mains voltage unless
qualified.
