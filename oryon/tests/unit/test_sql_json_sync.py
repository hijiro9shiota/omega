from datetime import datetime, timezone
from pathlib import Path

from oryon.data.connectors.base import Candle
from oryon.data.storage.ETL_json_to_sql import bulk_sync
from oryon.data.storage.json_store import JsonStore
from oryon.data.storage.sql_store import SQLStore


def test_bulk_sync(tmp_path: Path) -> None:
    json_root = tmp_path / "json"
    sql_path = tmp_path / "oryon.sqlite"
    schema_path = Path("oryon/data/storage/schema.sql")
    store = JsonStore(json_root)
    candle = Candle(
        symbol="BTCUSDT",
        timeframe="1h",
        timestamp=datetime.fromtimestamp(1000, tz=timezone.utc),
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=100.0,
        source="test",
    )
    store.append("BTCUSDT", "1h", [candle])

    sql_store = SQLStore(sql_path)
    sql_store.initialize(schema_path)
    read, written = bulk_sync(store, sql_store, [("BTCUSDT", "1h")])
    assert read == 1
    assert written == 1
    fetched = sql_store.fetch_candles("BTCUSDT", "1h")
    assert len(fetched) == 1
    assert fetched[0].close == 1.5
