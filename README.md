# AI Electronics Scanner

Point your phone at an electronic component — a resistor, IC, sensor, or module —
and get its **pinout**, a **wiring diagram**, and **ready-to-flash Arduino/ESP32
code** in seconds. Built for makers and hobbyists who want to skip the datasheet
hunt and start building.

| | |
|---|---|
| **Frontend** | Flutter (Android APK; iOS-ready codebase) |
| **Backend** | Python · FastAPI · OpenCV · Tesseract OCR |
| **Hosting** | Any Docker host (built for Vast.ai) |
| **Monetisation** | Freemium — free scans & pinouts, Pro (~$3–5/mo) for wiring, code gen, unlimited scans & full history |

---

## How it works

```
┌────────────┐   photo    ┌─────────────────────────────┐
│ Flutter app ├──────────►│ FastAPI backend             │
│  (Android)  │           │  1. OCR silk-screen labels  │
│             │◄──────────┤  2. Resistor colour bands   │
└────────────┘  match +   │  3. Shape heuristics        │
                pinout    │  → component knowledge base │
                          └─────────────────────────────┘
```

The vision pipeline combines three signals:

1. **OCR** (Tesseract) reads part numbers printed on chips/modules (`NE555`,
   `MPU-6050`, `HC-SR04`, …) and matches them against the knowledge base.
2. **Colour-band decoding** (OpenCV) isolates a resistor body, samples its
   bands, and computes the resistance value (e.g. `10kΩ ±5%`).
3. **Shape heuristics** provide a low-confidence fallback and photo-quality tips.

A trained CNN classifier can be added later as a fourth signal without touching
the API (see `backend/app/vision/pipeline.py`).

## Repository layout

```
backend/     Python FastAPI service (vision + knowledge base + generators)
frontend/    Flutter app
docs/        Deployment & architecture guides
.github/     CI: tests + automatic APK builds
```

## Quick start — backend

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

To bake your backend server URL into the APK, set the repository variable
`API_BASE_URL` (Settings → Secrets and variables → Actions → Variables) to e.g.
`http://YOUR-VAST-IP:PORT`, then re-run the workflow. You can also pass the URL
directly when triggering the workflow manually (Actions → Build & Test →
Run workflow).

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
