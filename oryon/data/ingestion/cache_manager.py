"""Disk-backed cache for connector responses."""
from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from typing import Any, Optional

import json


class CacheManager:
    """Persist simple JSON payloads with TTL semantics."""

    def __init__(self, cache_dir: Path, ttl_seconds: int = 3600) -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._ttl = ttl_seconds

    def _key_path(self, namespace: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self._cache_dir / namespace / f"{digest}.json"

    def get(self, namespace: str, key: str) -> Optional[Any]:
        path = self._key_path(namespace, key)
        if not path.exists():
            return None
        if self._is_expired(path):
            try:
                path.unlink()
            except FileNotFoundError:  # pragma: no cover - race condition guard
                pass
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def set(self, namespace: str, key: str, value: Any) -> None:
        path = self._key_path(namespace, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"ts": time.time(), "value": value}
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh)

    def _is_expired(self, path: Path) -> bool:
        stat = path.stat()
        age = time.time() - stat.st_mtime
        if age > self._ttl:
            return True
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return time.time() - data.get("ts", 0) > self._ttl

    def clear(self) -> None:
        for root, _, files in os.walk(self._cache_dir):
            for file in files:
                Path(root, file).unlink(missing_ok=True)
