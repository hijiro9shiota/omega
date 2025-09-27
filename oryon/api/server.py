"""FastAPI application exposing Oryon services."""
from __future__ import annotations


import logging
from pathlib import Path
from typing import Any, Dict, Iterable

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

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


logger = logging.getLogger(__name__)


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
    api_prefix = defaults.get("api_prefix", "/api")
    for router in (search.router, history.router, live.router, analyze.router):
        app.include_router(router, prefix=api_prefix)
    _configure_frontend(app, defaults=defaults, api_prefix=str(api_prefix))
    app.include_router(search.router)
    app.include_router(history.router)
    app.include_router(live.router)
    app.include_router(analyze.router)

    return app


app = create_app()


__all__ = ["create_app", "app"]


def _configure_frontend(app: FastAPI, *, defaults: Dict[str, Any], api_prefix: str) -> None:
    """Attach static frontend assets and SPA fallbacks if a build is present."""

    ui_path_raw = defaults.get("ui_dist_path", "ui/dist")
    ui_dist_path = Path(ui_path_raw).expanduser()
    if not ui_dist_path.exists():
        logger.info("UI dist path %s not found; frontend static serving disabled", ui_dist_path)
        return

    index_path = ui_dist_path / "index.html"
    if not index_path.exists():
        logger.warning("UI dist path %s missing index.html; skipping frontend mounting", ui_dist_path)
        return

    index_html = index_path.read_text(encoding="utf-8")
    assets_dir = ui_dist_path / "assets"
    if assets_dir.exists():
        logger.info("Mounting UI assets from %s", assets_dir)
        app.mount("/assets", StaticFiles(directory=assets_dir), name="ui-assets")
    else:
        logger.warning("UI assets directory %s not found", assets_dir)

    for static_file in _iter_root_static_files(ui_dist_path):
        route_path = f"/{static_file.name}"

        @app.get(route_path, include_in_schema=False)  # type: ignore[misc]
        async def _serve_static(file_path: Path = static_file) -> FileResponse:
            return FileResponse(file_path)

    @app.get("/", include_in_schema=False, response_class=HTMLResponse)
    async def serve_index() -> HTMLResponse:  # pragma: no cover - exercised via integration test
        return HTMLResponse(index_html)

    api_prefix_clean = api_prefix.lstrip("/")

    @app.get("/{spa_path:path}", include_in_schema=False, response_class=HTMLResponse)
    async def spa_fallback(spa_path: str) -> HTMLResponse:
        first_segment = spa_path.split("/", 1)[0]
        if first_segment == api_prefix_clean:
            raise HTTPException(status_code=404)
        return HTMLResponse(index_html)


def _iter_root_static_files(ui_dist_path: Path) -> Iterable[Path]:
    for candidate in ui_dist_path.iterdir():
        if candidate.is_file() and candidate.name != "index.html":
            yield candidate
