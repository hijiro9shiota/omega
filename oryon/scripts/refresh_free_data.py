"""Refresh local datasets using free data connectors."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from oryon.core.utils.config_loader import load_config
from oryon.core.utils.logging_setup import configure_logging
from oryon.data.connectors.binance_rest_public import BinanceRestPublic
from oryon.data.connectors.ccxt_public_client import CCXTPublicClient
from oryon.data.connectors.file_csv_client import FileCSVClient
from oryon.data.connectors.stooq_client import StooqClient
from oryon.data.connectors.yfinance_client import YFinanceClient
from oryon.data.ingestion.cache_manager import CacheManager
from oryon.data.ingestion.fetch_scheduler import FetchScheduler
from oryon.data.ingestion.rate_limit import RateLimiter
from oryon.data.storage.ETL_json_to_sql import bulk_sync
from oryon.data.storage.json_store import JsonStore
from oryon.data.storage.sql_store import SQLStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Oryon local datasets")
    parser.add_argument("--config", type=Path, default=Path("oryon_config.yaml"))
    parser.add_argument("--symbol", action="append", help="Symbol(s) to refresh")
    parser.add_argument("--timeframe", action="append", help="Timeframe(s) to refresh")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    configure_logging()
    config = load_config(args.config)
    defaults = config.get("defaults", {})

    json_store = JsonStore(Path(defaults.get("data_dir", "data_store")) / "json",
                           snapshot_interval=defaults.get("json_snapshot_interval", 1000),
                           snapshot_retention=defaults.get("json_snapshot_retention", 5))
    cache = CacheManager(Path(defaults.get("cache_dir", "cache")),
                         ttl_seconds=defaults.get("cache_ttl_minutes", 120) * 60)
    rate_limiter = RateLimiter(defaults.get("rate_limit_max_requests", 90),
                               defaults.get("rate_limit_window_seconds", 60))

    connectors = [
        YFinanceClient(max_chunk_days=defaults.get("connectors", {}).get("yfinance", {}).get("max_chunk_days", 60)),
        StooqClient(),
        CCXTPublicClient(exchange=defaults.get("connectors", {}).get("ccxt", {}).get("exchange", "binance")),
        BinanceRestPublic(),
    ]
    demo_cfg = defaults.get("demo_bundle", {})
    if demo_cfg.get("enabled"):
        connectors.append(FileCSVClient(Path(demo_cfg.get("path", "demo_data"))))

    scheduler = FetchScheduler(connectors, json_store, cache, rate_limiter)

    timeframes = args.timeframe or defaults.get("timeframes", [])
    symbols = args.symbol or []
    start = datetime.fromisoformat(args.start) if args.start else None
    end = datetime.fromisoformat(args.end) if args.end else None

    for symbol in symbols:
        scheduler.fetch_symbol(symbol, timeframes, start=start, end=end, force_refresh=args.force)
    sql_store = SQLStore(Path(defaults.get("sqlite_path", "data_store/oryon.sqlite")))
    schema_path = Path("oryon/data/storage/schema.sql")
    sql_store.initialize(schema_path)
    bulk_sync(json_store, sql_store, [(symbol, tf) for symbol in symbols for tf in timeframes])


if __name__ == "__main__":
    main()
