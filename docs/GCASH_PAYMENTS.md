# GCash payments — automatic Pro, no admin approval

Customers pay with GCash inside the app; the payment gateway confirms the
payment to our backend; the backend writes the Firestore entitlement the app
already listens to. Nobody grants anything by hand.

```
App ──POST /payments/checkout──►  Backend ──creates hosted checkout──► PayMongo
 │                                                                        │
 │  opens checkout URL (browser / GCash app) ◄────────────────────────────┘
 │                                    customer approves in GCash
 │                                                                        │
 │  ◄── webhook: checkout_session.payment.paid ───────────────────────────┘
 │        backend writes entitlements/{email} = {premium: true, expiresAt}
 └──► app's Firestore listener flips to Pro (and /status polling as a backup)
```

Two independent paths grant Pro, so a lost callback never strands a paying
customer:

1. **Webhook** — signed callback from the gateway (instant).
2. **Polling** — the app calls `GET /payments/status/{reference}` every few
   seconds; if the payment is still pending the backend re-checks the gateway
   itself and activates on the spot.

Activation is idempotent: a reference that is already `paid` is never granted
twice, and an early renewal stacks onto the days still remaining.

---

## 1. Get a gateway account

The app never talks to GCash directly — a licensed gateway does. The default
implementation uses **PayMongo** (Philippine, supports GCash, Maya, GrabPay and
cards through one hosted checkout page).

1. Sign up at https://dashboard.paymongo.com and complete business verification.
2. Copy the **secret key** (`sk_test_…` while testing, `sk_live_…` in production).
3. Create a webhook pointing at your server:
   `https://YOUR-HOST/api/v1/payments/webhook`, subscribing to
   `checkout_session.payment.paid` (plus `payment.paid` / `payment.failed`).
4. Copy the **webhook secret** (`whsk_…`).

A different gateway (Xendit, Maya Business, Dragonpay) only needs a new class in
`backend/app/payments/providers.py` implementing `create_checkout`,
`fetch_status` and `parse_webhook` — nothing above that layer changes.

## 2. Give the backend Firebase credentials

Pro is granted by writing `entitlements/{email}` with the Firebase Admin SDK,
which bypasses the Firestore rules (clients can only ever read their own
entitlement — see `firebase/firestore.rules`).

Create a service-account key in the Firebase console
(**Project settings → Service accounts → Generate new private key**) and put it
on the server **outside the repository**:

```bash
# option A — file on disk
export FIREBASE_SERVICE_ACCOUNT=/etc/secrets/firebase-admin.json

# option B — inline JSON (container secrets, Vast.ai env, GitHub Actions)
export FIREBASE_SERVICE_ACCOUNT_JSON="$(cat firebase-admin.json)"
```

> ⚠️ **Never commit a service-account key.** It grants full admin access to the
> Firebase project — anyone holding it can read all data and grant themselves
> Pro. `.gitignore` blocks the usual filenames, but the safest habit is to keep
> the file out of the working tree entirely. If a key has ever been shared over
> chat, email or a screenshot, revoke it in the Firebase console
> (**Service accounts → Manage service account permissions → Keys**) and
> generate a new one.

Without credentials the service still runs: entitlements are written to the
local JSON ledger at `PAYMENTS_DB_PATH` instead, which is fine for development
but does **not** unlock the app (the app reads Firestore).

## 3. Configure and run

| Variable | Default | What it does |
|---|---|---|
| `PAYMENT_PROVIDER` | `auto` | `auto` \| `paymongo` \| `mock` |
| `PAYMONGO_SECRET_KEY` | — | Gateway secret key |
| `PAYMONGO_WEBHOOK_SECRET` | — | Verifies callback signatures (required for webhooks) |
| `PAYMENT_METHODS` | `gcash` | Rails on the checkout page, e.g. `gcash,paymaya,card` |
| `PAYMENT_PLANS` | built-in | JSON list to override pricing |
| `PAYMENTS_SUCCESS_URL` | website `payment-success.html` | Where the customer lands after paying |
| `PAYMENTS_CANCEL_URL` | website `payment-cancelled.html` | Where they land if they back out |
| `PAYMENTS_REQUIRE_ID_TOKEN` | `false` | Require a verified Firebase ID token to start a checkout |
| `WEBHOOK_TOLERANCE_SECONDS` | `300` | Replay-protection window |
| `FIREBASE_SERVICE_ACCOUNT` / `_JSON` | — | Admin credentials (see above) |
| `PAYMENTS_DB_PATH` | `payments-db.json` | Fallback ledger when Firebase is absent |

```bash
cd backend
export PAYMONGO_SECRET_KEY=sk_test_xxx
export PAYMONGO_WEBHOOK_SECRET=whsk_xxx
export FIREBASE_SERVICE_ACCOUNT=/etc/secrets/firebase-admin.json
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`GET /api/v1/payments/config` reports which gateway is live and what the plans
cost — the app calls it to build the paywall, so pricing changes need no new
build.

## 4. Point the app at it

```bash
flutter build apk --release \
  --dart-define=PAYMENTS_BASE_URL=https://pay.example.com
```

If `PAYMENTS_BASE_URL` is omitted the app falls back to `API_BASE_URL`. When the
payment service is unreachable the paywall degrades to the old
"email us" instructions instead of showing a broken button.

The website's `account.html` has the same flow; set `PAYMENTS_BASE_URL` near the
top of its script block to enable it there.

## 5. Plans

Defaults (override with `PAYMENT_PLANS`):

| Plan | Price | Length |
|---|---|---|
| `monthly` | ₱199 | 30 days |
| `yearly` | ₱1,499 | 365 days |
| `lifetime` | ₱2,999 | never expires |

```bash
export PAYMENT_PLANS='[
  {"id":"monthly","name":"Pro Monthly","price":149,"days":30},
  {"id":"lifetime","name":"Pro Lifetime","price":1999,"days":null}
]'
```

## 6. Test the whole flow without money

With no `PAYMONGO_SECRET_KEY` set, the backend selects the built-in **mock**
gateway. `GET /payments/config` reports `"sandbox": true`, the paywall shows a
**Simulate payment (dev)** button, and the activation path is identical to a
real payment:

```bash
REF=$(curl -s -X POST localhost:8000/api/v1/payments/checkout \
  -H 'Content-Type: application/json' \
  -d '{"plan_id":"monthly","email":"you@example.com"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["reference"])')

curl -s -X POST localhost:8000/api/v1/payments/mock/pay/$REF
curl -s "localhost:8000/api/v1/payments/entitlement?email=you@example.com"
```

Then switch to `sk_test_…` keys and pay with PayMongo's GCash test wallet before
going live.

## What the customer sees

1. Opens **Go Pro**, picks a plan, taps **Pay ₱199 with GCash**.
2. The GCash checkout page opens; they approve the payment.
3. They return to the app — it has already unlocked, with a "Payment received"
   confirmation. Account shows the plan and its renewal date.

## Data written

```
payments/{reference}      email, uid, plan, amount, status, provider,
                          sessionId, createdAt, paidAt, premiumUntil
entitlements/{email}      premium, plan, planName, expiresAt, source: "gcash",
                          provider, reference, grantedBy: "auto-payment",
                          activatedAt
```

`payments/*` is server-write-only and admin-read-only; `entitlements/{email}` is
readable by its owner, which is what unlocks the app.

## Refunds and revocations

Refund in the gateway dashboard, then set `premium: false` on the entitlement
(the admin panel in the app or on `account.html` does this). The app follows the
document, so access ends within seconds.
