"""Delete expired cloud uploads from Firestore.

Runs on a schedule via GitHub Actions (.github/workflows/cleanup.yml).
Retention is: free users 12h, Pro users 7 days — the expiry is stamped on
each document at upload time, so this job just deletes anything past it.

Credentials: set FIREBASE_SERVICE_ACCOUNT to the service-account JSON
(as a GitHub Actions secret — never commit it).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore


def main() -> int:
    raw = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not raw:
        print("FIREBASE_SERVICE_ACCOUNT not set - nothing to do.")
        return 0

    firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)))
    db = firestore.client()
    now = datetime.now(timezone.utc)

    deleted = 0
    scanned_users = 0
    # list_documents() also yields "missing" parent docs that only exist as
    # subcollection ancestors, so no user-profile document is required.
    for user_ref in db.collection("users").list_documents():
        scanned_users += 1
        expired = (
            user_ref.collection("uploads")
            .where("expiresAt", "<=", now)
            .stream()
        )
        for doc in expired:
            doc.reference.delete()
            deleted += 1

    print(f"Scanned {scanned_users} users, deleted {deleted} expired uploads.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
