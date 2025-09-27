"""Integration tests for FastAPI backend and frontend serving."""
from __future__ import annotations

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



def _bootstrap_app(tmp_path: Path, ui_dist_path: Path | None = None):

def _bootstrap_app(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    data_dir = tmp_path / "data"
    sqlite_path = data_dir / "oryon.sqlite"
    universe_path = data_dir / "symbols.jsonl"
    data_dir.mkdir(parents=True, exist_ok=True)
    config_lines = [
        "defaults:",
        f"  data_dir: {data_dir.as_posix()}",
        f"  sqlite_path: {sqlite_path.as_posix()}",
        f"  symbol_universe_path: {universe_path.as_posix()}",
        "  timeframes:",
        "    - 1h",
        "    - 15m",
    ]
    if ui_dist_path is not None:
        config_lines.insert(4, f"  ui_dist_path: {ui_dist_path.as_posix()}")
    config_path.write_text("\n".join(config_lines) + "\n", encoding="utf-8")

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


    search_resp = client.get("/api/search", params={"q": "BTC", "limit": 5})
    assert search_resp.status_code == 200
    assert any(item["symbol"] == "BTCUSDT" for item in search_resp.json())

    history_resp = client.get("/api/history", params={"symbol": "BTCUSDT", "timeframe": "15m", "limit": 50})

    search_resp = client.get("/search", params={"q": "BTC", "limit": 5})
    assert search_resp.status_code == 200
    assert any(item["symbol"] == "BTCUSDT" for item in search_resp.json())

    history_resp = client.get("/history", params={"symbol": "BTCUSDT", "timeframe": "15m", "limit": 50})

    assert history_resp.status_code == 200
    candles = history_resp.json()
    assert len(candles) <= 50
    assert "timestamp" in candles[0]


    live_resp = client.get("/api/live", params={"symbol": "BTCUSDT", "timeframe": "15m"})

    live_resp = client.get("/live", params={"symbol": "BTCUSDT", "timeframe": "15m"})

    assert live_resp.status_code == 200
    payload = live_resp.json()
    assert payload["symbol"] == "BTCUSDT"

    analyze_resp = client.post(

        "/api/analyze",

        "/analyze",

        json={"symbol": "BTCUSDT", "timeframes": ["1h", "15m"], "lookback": 300},
    )
    assert analyze_resp.status_code == 200
    body = analyze_resp.json()
    assert "signals" in body
    assert "generated_at" in body



def test_frontend_assets_and_fallback(tmp_path):
    ui_dist = tmp_path / "ui_dist"
    assets_dir = ui_dist / "assets"
    assets_dir.mkdir(parents=True)
    index_html = (
        "<!doctype html><html><body><div id='root'></div>"
        "<script type='module' src='/assets/app.js'></script></body></html>"
    )
    (ui_dist / "index.html").write_text(index_html, encoding="utf-8")
    (ui_dist / "logo.svg").write_text("<svg></svg>", encoding="utf-8")
    (assets_dir / "app.js").write_text("console.log('test');", encoding="utf-8")
    app = _bootstrap_app(tmp_path, ui_dist_path=ui_dist)
    client = TestClient(app)

    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert "<div id='root'></div>" in root_resp.text

    asset_resp = client.get("/assets/app.js")
    assert asset_resp.status_code == 200
    assert "console.log" in asset_resp.text

    svg_resp = client.get("/logo.svg")
    assert svg_resp.status_code == 200
    assert svg_resp.text.startswith("<svg")

    fallback_resp = client.get("/dashboard")
    assert fallback_resp.status_code == 200
    assert "<div id='root'></div>" in fallback_resp.text

