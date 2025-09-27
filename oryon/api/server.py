"""FastAPI application exposing Oryon services."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from oryon.api.dependencies import AppResources
from oryon.api.routers import analyze, history, live, search
from oryon.backtest.loader import BacktestDataLoader
from oryon.core.pipelines.analyze_asset import AnalyzeAssetPipeline
from oryon.core.utils.config_loader import load_config
from oryon.core.utils.logging_setup import configure_logging
from oryon.data.ingestion.symbol_universe import SymbolUniverse
from oryon.data.storage.json_store import JsonStore
from oryon.data.storage.sql_store import SQLStore


def create_app(config_path: str | Path = "oryon_config.yaml") -> FastAPI:
    configure_logging()
    config = load_config(config_path)
    defaults: Dict[str, Any] = config.get("defaults", {})
    data_dir = Path(defaults.get("data_dir", "data_store"))
    json_store = JsonStore(data_dir / "json")
    sqlite_path = Path(defaults.get("sqlite_path", data_dir / "oryon.sqlite"))
    sql_store = SQLStore(sqlite_path)
    schema_path = Path("oryon/data/storage/schema.sql")
    if not sqlite_path.exists():
        sql_store.initialize(schema_path)
    loader = BacktestDataLoader(json_store=json_store, sql_store=sql_store)
    timeframes = defaults.get("timeframes", ["1d", "4h", "1h", "15m", "5m"])
    execution_tf = timeframes[-1]
    pipeline = AnalyzeAssetPipeline(timeframes=timeframes, execution_timeframe=execution_tf)
    universe_path = Path(defaults.get("symbol_universe_path", data_dir / "symbols.jsonl"))
    universe = SymbolUniverse(universe_path)

    app = FastAPI(title="Oryon API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost", "http://127.0.0.1", "http://0.0.0.0", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.resources = AppResources(
        config=config,
        pipeline=pipeline,
        data_loader=loader,
        sql_store=sql_store,
        universe=universe,
    )
    app.include_router(search.router)
    app.include_router(history.router)
    app.include_router(live.router)
    app.include_router(analyze.router)
    return app


app = create_app()


__all__ = ["create_app", "app"]
