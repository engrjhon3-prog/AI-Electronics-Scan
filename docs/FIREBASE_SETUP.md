# Firebase — what it's for and exactly what to provide

**Short version: the app works today without Firebase.** Scan history is stored
on-device and the backend is stateless. Firebase becomes worthwhile when you
want (a) user accounts, (b) history synced across devices / surviving
reinstalls, and (c) server-verified subscriptions. When you're ready, here is
*exactly* what to do and what to hand over.

## What you need to do (all doable from a phone browser)

1. Go to [console.firebase.google.com](https://console.firebase.google.com)
   → **Add project** → name it e.g. `ai-electronics-scan` (Analytics optional).

2. In the project, click **Add app → Android** and enter:
   - **Package name**: `com.aielectronics.electronics_scanner`
     (must match exactly — it's set in
     `frontend/android/app/build.gradle.kts`)
   - Nickname: anything. SHA-1 can be skipped for now (needed later only for
     Google Sign-In).

3. Download the **`google-services.json`** file it gives you.

4. In the console, enable these products (left sidebar → Build):
   - **Authentication** → Sign-in method → enable **Anonymous** (and
     optionally **Google**).
   - **Cloud Firestore** → Create database → production mode → nearest region.

5. Create a backend service account key:
   - Project settings (gear icon) → **Service accounts** →
     **Generate new private key** → downloads a JSON file.

## What to give me

| Item | How to share | Sensitivity |
|---|---|---|
| `google-services.json` | Commit to the repo is acceptable (it contains identifiers, not secrets) — or paste its contents in chat | Low |
| Service-account JSON | **Never commit.** Add as a GitHub Actions secret named `FIREBASE_SERVICE_ACCOUNT`, and set it as the `FIREBASE_SERVICE_ACCOUNT_JSON` env var on the Vast.ai instance | **High — treat like a password** |
| Project ID (e.g. `ai-electronics-scan-1a2b3`) | Paste in chat | Low |

## What I'll wire up once you provide those

- **App**: `firebase_core`, `firebase_auth` (anonymous sign-in on first launch),
  `cloud_firestore` — `HistoryService` gets a Firestore-backed implementation
  (it was designed as an interface for exactly this swap).
- **Backend**: `firebase-admin` — `_require_premium` in `backend/app/main.py`
  switches from the dev token to verifying a Firebase ID token + custom
  `premium` claim, which gets set on successful purchase.
- **Firestore rules**: users can only read/write their own
  `users/{uid}/scans/...` documents.

## Billing note

Firebase's free Spark plan covers this app comfortably at hobby scale
(50k Firestore reads/day, unlimited auth users). No card required.
