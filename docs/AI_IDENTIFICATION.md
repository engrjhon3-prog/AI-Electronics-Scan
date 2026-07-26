# AI identification — recognising parts that aren't in the catalog

The app ships with 179 curated components. That covers what most people
actually pull out of a parts drawer, but there are hundreds of thousands of
components in the world, and no hand-written list will ever hold them all.

So the catalog is the *fast path*, not the limit. When the on-device scanner
comes up empty — or names something you don't think is right — the photo goes
to Claude's vision model, which works out what the part is and writes a full
catalog entry for it: description, package, pinout, per-board wiring and a
working sketch. The entry is merged into the phone's catalog and saved there,
so from that moment on the part behaves exactly like a bundled one, offline
included.

```
photo ─► on-device OCR + colour bands ─► bundled catalog ── match ─► done
                                              │
                                          no match
                                              ▼
                                   POST /api/v1/ai/identify
                                              │
                                   shared cache hit? ─ yes ─► instant, free
                                              │ no
                                              ▼
                                   Claude vision (structured output)
                                              │
                            validate ─► render wiring SVGs ─► cache
                                              ▼
                                merged into the device catalog (offline)
```

## Switching it on

One environment variable on the backend:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Without it the endpoint returns a clear `503` and the app simply doesn't show
the AI card — everything else keeps working. Nothing else is required.

| Variable | Default | What it does |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(empty)* | Enables the feature. Keep it out of git. |
| `AI_MODEL` | `claude-opus-5` | Vision model. `claude-sonnet-5` is cheaper and still good on clearly-marked parts. |
| `AI_EFFORT` | `medium` | Reasoning depth: `low` … `max`. Higher reads worn/ambiguous markings better and costs more. |
| `AI_MAX_TOKENS` | `32000` | Ceiling for one identification (a full entry with wiring and code is long). |
| `AI_CACHE_THRESHOLD` | `0.6` | Minimum confidence before an answer is shared with everyone else. |
| `AI_CACHE_PATH` | `ai-components.json` | Local cache file, used when Firebase isn't configured. |

When Firebase Admin credentials are present (the same ones the payments
service uses — see [GCASH_PAYMENTS.md](GCASH_PAYMENTS.md)) the cache lives in
the Firestore collection `ai_components` instead, so every server instance
shares it.

## Cost, and why it stays small

Identifications are cached **per component, not per request**. The first person
to photograph a TB6612FNG pays for the model call; everyone after that gets the
same entry from the cache instantly and for nothing. The catalog effectively
grows itself with use.

Rough per-identification cost with Opus 5 at $5/$25 per million tokens: an
image plus prompt is ~2–3k input tokens and a full entry is ~1.5–3k output
tokens, so **roughly $0.05–0.09 for a part nobody has scanned before**, and
$0.00 for one that's already known. Two further reductions are built in:

- the system prompt is sent with `cache_control`, so its tokens are billed at
  the cached rate on every call after the first;
- answers below `AI_CACHE_THRESHOLD` confidence are returned to the user but
  **not** cached, so a guess never becomes the shared answer.

`GET /api/v1/ai/status` reports `cached_components` — that number is how many
model calls you're no longer paying for.

## Who can use it

Pro only. `POST /api/v1/ai/identify` goes through the same
`app/security.py::require_premium` check as wiring and code generation: a
Firebase ID token whose account holds a live entitlement, or the development
token. Free accounts get a `402`, and the app turns that into the paywall
rather than an error.

That is deliberate — this is the one feature with a real marginal cost per use,
so it's the one that pays for itself.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/ai/status` | Is it on, which model, how many components learned |
| `POST` | `/api/v1/ai/identify` | multipart: `image`, `ocr_text`, `hint` → identification |
| `GET` | `/api/v1/ai/components` | Everything the AI has learned so far |
| `GET` | `/api/v1/ai/components/{id}` | One learned component, catalog-shaped |

Example:

```bash
curl -X POST http://localhost:8000/api/v1/ai/identify \
  -H "X-Premium-Token: premium-dev" \
  -F image=@part.jpg \
  -F ocr_text="TB6612FNG" \
  -F hint="motor driver breakout"
```

```jsonc
{
  "identified": true,
  "confidence": 0.91,
  "detected_text": "TB6612FNG",
  "reasoning": "Silkscreen reads TB6612FNG on a 16-pin dual H-bridge breakout.",
  "cached": false,
  "component": {
    "id": "tb6612fng",
    "name": "TB6612FNG Dual Motor Driver",
    "category": "ai-identified",
    "source": "ai",
    "pins": [ /* … */ ],
    "wiring": { "esp32": { "connections": [ /* … */ ], "svg": "<svg …" } },
    "code":   { "esp32": { "code": "#include …" } }
  }
}
```

## What keeps the output trustworthy

The model can't reply with free-form prose. The request uses a strict JSON
schema (`app/ai/schema.py`) that pins every field, and the server then:

- normalises the id (`TB6612FNG` → `tb6612fng`) so the same part can't be
  learned twice under two spellings;
- drops any board it doesn't support and any pin type it doesn't recognise,
  rather than letting an invented value into the catalog;
- renders the wiring diagram itself, with the same renderer the curated entries
  use — the model supplies connections, never the SVG;
- refuses to invent datasheet URLs (an empty string becomes `null`);
- returns a readable `502` if the model declines or runs out of output budget,
  instead of half an entry.

The model is instructed to prefer *accuracy over completeness*: if it can't
read the markings it says so, with advice on retaking the photo, and that
answer is never cached.

## Testing without an API key

`backend/tests/test_ai.py` stubs the model and covers the whole contract —
schema strictness, catalog conversion, Pro gating, the cache serving the second
scan, low-confidence answers not being cached, refusals, and bad uploads. It
runs in CI with no key and no network:

```bash
cd backend && pytest tests/test_ai.py -q
```
