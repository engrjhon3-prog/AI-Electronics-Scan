"""Shared cache of AI-identified components.

Every part the model identifies is stored once and served from the cache for
everyone afterwards — so the catalog grows itself, each new component is paid
for a single time, and repeat scans are instant and free.

Firestore is used when the Admin SDK is configured (same credentials as the
payment service); otherwise entries land in a local JSON file so the service
still works in development.
"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import settings
from app.payments.entitlements import firebase_app

log = logging.getLogger("ai")

COLLECTION = "ai_components"
_ID_RE = re.compile(r"[^a-z0-9_]+")


def normalise_id(value: str) -> str:
    """Fold a part number into the id form the model is asked to produce."""
    return _ID_RE.sub("_", value.strip().lower()).strip("_")


class ComponentCache:
    backend = "none"

    def get(self, component_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def put(self, entry: Dict[str, Any]) -> None:
        raise NotImplementedError

    def all_entries(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def find_by_alias(self, text: str) -> Optional[Dict[str, Any]]:
        """Match a scanned token against cached ids and aliases."""
        token = text.strip().lower()
        if not token:
            return None
        direct = self.get(normalise_id(token))
        if direct is not None:
            return direct
        for entry in self.all_entries():
            aliases = {a.lower() for a in entry.get("aliases", [])}
            aliases.add(entry.get("id", "").lower())
            aliases.add(entry.get("name", "").lower())
            if any(alias and len(alias) >= 3 and alias in token for alias in aliases):
                return entry
        return None


class FirestoreCache(ComponentCache):
    backend = "firestore"

    def __init__(self, client: Any) -> None:
        self._db = client

    def get(self, component_id: str) -> Optional[Dict[str, Any]]:
        snap = self._db.collection(COLLECTION).document(component_id).get()
        return snap.to_dict() if snap.exists else None

    def put(self, entry: Dict[str, Any]) -> None:
        self._db.collection(COLLECTION).document(entry["id"]).set(entry)

    def all_entries(self) -> List[Dict[str, Any]]:
        return [doc.to_dict() for doc in self._db.collection(COLLECTION).stream()]


class JsonFileCache(ComponentCache):
    backend = "json"

    def __init__(self, path: str) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._data: Dict[str, Dict[str, Any]] = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    self._data = loaded
            except (OSError, ValueError):
                log.warning("Could not read AI cache %s; starting empty.", path)

    def get(self, component_id: str) -> Optional[Dict[str, Any]]:
        return self._data.get(component_id)

    def put(self, entry: Dict[str, Any]) -> None:
        with self._lock:
            self._data[entry["id"]] = entry
            try:
                directory = os.path.dirname(os.path.abspath(self._path))
                os.makedirs(directory, exist_ok=True)
                with open(self._path, "w", encoding="utf-8") as handle:
                    json.dump(self._data, handle, ensure_ascii=False, indent=1)
            except OSError as exc:
                log.warning("Could not persist AI cache: %s", exc)

    def all_entries(self) -> List[Dict[str, Any]]:
        return list(self._data.values())


_cache: Optional[ComponentCache] = None


def get_cache() -> ComponentCache:
    global _cache
    if _cache is not None:
        return _cache
    app = firebase_app()
    if app is not None:
        try:
            from firebase_admin import firestore

            _cache = FirestoreCache(firestore.client(app))
            log.info("AI components will be cached in Firestore.")
            return _cache
        except Exception as exc:
            log.warning("Firestore unavailable for the AI cache (%s).", exc)
    _cache = JsonFileCache(settings.ai_cache_path)
    return _cache


def reset_cache() -> None:
    """Drop the cached handle (used by tests)."""
    global _cache
    _cache = None


def stamp(entry: Dict[str, Any], *, model: str) -> Dict[str, Any]:
    """Attach provenance so the app can show where an entry came from."""
    entry = dict(entry)
    entry["source"] = "ai"
    entry["model"] = model
    entry["identified_at"] = datetime.now(timezone.utc).isoformat()
    return entry
