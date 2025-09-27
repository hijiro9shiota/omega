from datetime import datetime, timedelta
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from oryon.api.server import create_app
from oryon.data.connectors.base import Candle
from oryon.data.ingestion.symbol_universe import SymbolRecord


def _make_candles(symbol: str, timeframe: str, start: datetime, periods: int, delta: timedelta):
    candles = []
    price = 100.0
    for i in range(periods):
        ts = start + i * delta
        price += 0.3 if timeframe.endswith("m") else 0.6
        candle = Candle(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=ts,
            open=price - 0.5,
            high=price + 1.0,
            low=price - 1.0,
            close=price,
            volume=1000 + i,
            source="test",
        )
        candles.append(candle)
    return candles


def _bootstrap_app(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    data_dir = tmp_path / "data"
    sqlite_path = data_dir / "oryon.sqlite"
    universe_path = data_dir / "symbols.jsonl"
    data_dir.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        """
defaults:
  data_dir: {data_dir}
  sqlite_path: {sqlite_path}
  symbol_universe_path: {universe_path}
  timeframes:
    - 1h
    - 15m
""".format(
            data_dir=data_dir.as_posix(),
            sqlite_path=sqlite_path.as_posix(),
            universe_path=universe_path.as_posix(),
        ),
        encoding="utf-8",
    )
    app = create_app(config_path)
    resources = app.state.resources
    resources.sql_store.initialize(Path("oryon/data/storage/schema.sql"))
    symbol = SymbolRecord(symbol="BTCUSDT", exchange="binance", asset_type="crypto", base="BTC", quote="USDT")
    resources.sql_store.upsert_symbols([symbol])
    resources.universe.bulk_update([symbol])
    start = datetime(2023, 1, 1)
    data = {
        "1h": _make_candles("BTCUSDT", "1h", start, 400, timedelta(hours=1)),
        "15m": _make_candles("BTCUSDT", "15m", start, 400, timedelta(minutes=15)),
    }
    for timeframe, candles in data.items():
        resources.sql_store.insert_candles(candles)
    return app


def test_search_history_and_analyze(tmp_path):
    app = _bootstrap_app(tmp_path)
    client = TestClient(app)

    search_resp = client.get("/search", params={"q": "BTC", "limit": 5})
    assert search_resp.status_code == 200
    assert any(item["symbol"] == "BTCUSDT" for item in search_resp.json())

    history_resp = client.get("/history", params={"symbol": "BTCUSDT", "timeframe": "15m", "limit": 50})
    assert history_resp.status_code == 200
    candles = history_resp.json()
    assert len(candles) <= 50
    assert "timestamp" in candles[0]

    live_resp = client.get("/live", params={"symbol": "BTCUSDT", "timeframe": "15m"})
    assert live_resp.status_code == 200
    payload = live_resp.json()
    assert payload["symbol"] == "BTCUSDT"

    analyze_resp = client.post(
        "/analyze",
        json={"symbol": "BTCUSDT", "timeframes": ["1h", "15m"], "lookback": 300},
    )
    assert analyze_resp.status_code == 200
    body = analyze_resp.json()
    assert "signals" in body
    assert "generated_at" in body
