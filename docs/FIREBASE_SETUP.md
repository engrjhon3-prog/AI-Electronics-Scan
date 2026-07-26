# Firebase — current setup

Project: **electronics-cf10c** (configured and live).

## What's wired up

| Piece | Status |
|---|---|
| Email/Password sign-in | ✅ Enabled |
| Firestore database | ✅ `(default)` created |
| Security rules | ✅ Deployed from `firebase/firestore.rules` |
| Admin account | ✅ `jhonisaacalegre@gmail.com` with `admin` + `premium` custom claims |
| Android app config | ✅ `frontend/android/app/google-services.json` (package `com.aielectronics.electronics_scanner`) |
| Website auth | ✅ `website/account.html` (web app config) |

## Data model

```
entitlements/{email}         premium: bool, plan, planName, expiresAt,
                             source, reference, grantedBy, activatedAt
    Written automatically by the payment backend the moment a GCash payment
    clears (Admin SDK, so it bypasses the rules), or by an admin for comped
    accounts. The app/website read this (plus the `premium` custom claim) to
    unlock Pro. `expiresAt` is null on the lifetime plan.

payments/{reference}         email, uid, plan, amount, status, provider,
                             sessionId, createdAt, paidAt, premiumUntil
    Server-write-only payment ledger (idempotency + support history).
    Readable by admins only.

users/{uid}/uploads/{id}     name, componentId, imageB64, createdAt, expiresAt
    Scan photos as compressed JPEG (base64) — Firestore instead of Cloud
    Storage so everything stays on the free Spark plan.
    Retention: free = 12 hours (max 3 active), Pro = 7 days.
```

Retention is enforced in three layers:
1. **Rules** — creates must set `expiresAt` within the tier's window
   (rules check the entitlement), and expired docs can't be read at all.
2. **App** — purges the signed-in user's expired uploads on launch.
3. **Scheduled job** — `.github/workflows/cleanup.yml` runs every 6 hours
   and deletes expired docs across all users.

## One manual step: the cleanup job's credential

The scheduled cleanup needs the Firebase service-account key as a GitHub
secret (it must NEVER be committed to the repo):

1. GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**
2. Name: `FIREBASE_SERVICE_ACCOUNT`
3. Value: paste the entire service-account JSON (the file named
   `electronics-cf10c-firebase-adminsdk-....json`)

Until the secret is added the job runs and exits harmlessly; rules + in-app
purge still keep expired images inaccessible.

## Paid subscriptions (GCash)

Customers subscribe from the app or `account.html` and Pro activates without
anyone approving it — see **[GCASH_PAYMENTS.md](GCASH_PAYMENTS.md)**. The
payment backend needs the same service-account key described above, supplied
as `FIREBASE_SERVICE_ACCOUNT` (path) or `FIREBASE_SERVICE_ACCOUNT_JSON`
(inline) in its environment. Keep it out of the repository; if the key has
ever been shared in chat or email, revoke it and generate a new one.

## Granting Pro to a customer manually

Sign in as the admin account in the app (Settings → Account) or on the
website (`/account.html`) and use the **Admin — manage subscriptions** panel:
enter the customer's email → Grant Pro. Their app unlocks on next refresh.

## Security notes

- `google-services.json` and the web config contain public identifiers, not
  secrets — safe in the repo.
- The service-account JSON is a master key — GitHub secret / local only.
  If it ever leaks, revoke it in Firebase console → Project settings →
  Service accounts.
- The admin password was set from a chat message; consider changing it in
  the app/website via "Forgot password?" or the Firebase console.
