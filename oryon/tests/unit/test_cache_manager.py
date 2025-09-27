from pathlib import Path

from oryon.data.ingestion import cache_manager
from oryon.data.ingestion.cache_manager import CacheManager


def test_cache_manager_roundtrip(tmp_path: Path) -> None:
    cache = CacheManager(tmp_path, ttl_seconds=10)
    cache.set("ns", "key", [1, 2, 3])
    data = cache.get("ns", "key")
    assert data["value"] == [1, 2, 3]


def test_cache_manager_expiry(tmp_path: Path, monkeypatch) -> None:
    cache = CacheManager(tmp_path, ttl_seconds=1)
    monkeypatch.setattr(cache_manager.time, "time", lambda: 0)
    cache.set("ns", "key", {"value": [1]})
    monkeypatch.setattr(cache_manager.time, "time", lambda: 10)
    assert cache.get("ns", "key") is None
