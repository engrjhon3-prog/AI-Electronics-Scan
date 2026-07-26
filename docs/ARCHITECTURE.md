# Architecture

## Overview

```
┌───────────────────────────── Flutter app ─────────────────────────────┐
│ screens/    UI (scan, result, detail tabs, catalog, history, paywall) │
│ state/      AppState (ChangeNotifier via provider)                    │
│ services/   ApiClient · HistoryService · SubscriptionService          │
│ models/     JSON contract mirrors of backend models                   │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │ HTTPS/HTTP (multipart + JSON)
┌──────────────────────────────────▼────────────────────────────────────┐
│                          FastAPI backend                              │
│  api: /scan  /components  /components/{id}[/wiring|/code]             │
│                                                                       │
│  vision/pipeline.py — orchestrates detectors, ranks candidates        │
│    ├─ ocr.py        Tesseract silk-screen part numbers                │
│    ├─ resistor.py   OpenCV colour-band decoder                        │
│    └─ (future)      CNN classifier slot                               │
│                                                                       │
│  components/database.py — curated knowledge base                      │
│    pins · per-board wiring · per-board code snippets                  │
│                                                                       │
│  generators/wiring_svg.py — renders diagrams as inline SVG            │
└───────────────────────────────────────────────────────────────────────┘
```

## Key design decisions

**Recognition is multi-signal, not a single model.** OCR of the printed part
number is by far the most reliable identifier for ICs/modules; colour-band
decoding handles resistors; heuristics catch the rest. Each detector emits
`DetectionCandidate`s with a confidence and a human-readable reason; the
pipeline ranks and dedupes. A trained CNN can be added as one more candidate
source without touching the API or app.

**The knowledge base is data, not code.** One dict per component in
`database.py` holds pins, wiring per board, and code per board. Growing the
catalog is an append, and the integrity test
(`test_database_integrity`) validates every entry.

**Wiring diagrams are server-rendered SVG.** The backend knows the connection
data; shipping SVG means the app needs zero drawing logic and diagrams improve
without app updates.

**Freemium is enforced server-side.** `/wiring` and `/code` return HTTP 402
without an entitlement. The app's `PremiumRequiredException` maps to the
paywall. Client-side flags alone would be trivially bypassed.

**The Flutter side keeps services swappable.** `HistoryService` (local
shared_preferences) and `SubscriptionService` (local demo entitlement) are
deliberately thin so Firebase/Firestore and Play Billing implementations can
drop in behind the same interfaces.

## Contract

`backend/app/models.py` and `frontend/lib/models/` are mirrors. If you change
one, change the other. Field names use `snake_case` on the wire.

## Roadmap slots

- CNN component classifier (train on scans; add as pipeline signal #4)
- Firebase auth + Firestore history sync (see FIREBASE_SETUP.md)
- Google Play Billing + server receipt verification
- Multi-component detection (detect several parts in one photo)
- Project builder: combine scanned parts into one wiring plan + merged sketch
