from datetime import datetime, timezone
from pathlib import Path

from oryon.data.connectors.base import Candle, DataConnector
from oryon.data.ingestion.cache_manager import CacheManager
from oryon.data.ingestion.fetch_scheduler import FetchScheduler
from oryon.data.ingestion.rate_limit import RateLimiter
from oryon.data.storage.json_store import JsonStore


class DummyConnector(DataConnector):
    name = "dummy"

    def __init__(self) -> None:
        self.calls = 0

    def fetch(self, symbol, timeframe, start=None, end=None, limit=None):
        self.calls += 1
        yield Candle(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.fromtimestamp(0, tz=timezone.utc),
            open=1.0,
            high=2.0,
            low=0.5,
            close=1.5,
            volume=10.0,
            source=self.name,
        )


def test_fetch_scheduler_caches_results(tmp_path: Path) -> None:
    json_store = JsonStore(tmp_path / "json")
    cache = CacheManager(tmp_path / "cache", ttl_seconds=100)
    limiter = RateLimiter(10, 1)
    connector = DummyConnector()
    scheduler = FetchScheduler([connector], json_store, cache, limiter)

    scheduler.fetch_symbol("BTCUSDT", ["1h"])
    assert connector.calls == 1
    scheduler.fetch_symbol("BTCUSDT", ["1h"])
    assert connector.calls == 1
