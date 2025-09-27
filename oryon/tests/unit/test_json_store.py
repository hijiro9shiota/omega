from datetime import datetime, timezone
from pathlib import Path

from oryon.data.connectors.base import Candle
from oryon.data.storage.json_store import JsonStore


def make_candle(ts: int) -> Candle:
    return Candle(
        symbol="BTCUSDT",
        timeframe="1h",
        timestamp=datetime.fromtimestamp(ts, tz=timezone.utc),
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=100.0,
        source="test",
    )


def test_json_store_append_and_read(tmp_path: Path) -> None:
    store = JsonStore(tmp_path)
    candles = [make_candle(1000), make_candle(2000)]
    store.append("BTCUSDT", "1h", candles)
    loaded = list(store.read("BTCUSDT", "1h"))
    assert len(loaded) == 2
    assert loaded[0].timestamp == candles[0].timestamp


def test_json_store_snapshot(tmp_path: Path) -> None:
    store = JsonStore(tmp_path, snapshot_interval=1, snapshot_retention=1)
    store.append("BTCUSDT", "1h", [make_candle(3000)])
    snapshots = list((tmp_path / "BTCUSDT" / "snapshots" / "1h").glob("*.json"))
    assert snapshots
