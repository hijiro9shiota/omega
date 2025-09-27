"""Run a sample walk-forward backtest using local data."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from oryon.backtest.loader import BacktestDataLoader
from oryon.backtest.metrics import summarize
from oryon.backtest.reports.report_builder import build_report, export_csv, export_html
from oryon.backtest.walk_forward import WalkForwardBacktester, WalkForwardConfig
from oryon.core.pipelines.analyze_asset import AnalyzeAssetPipeline
from oryon.core.utils.config_loader import load_config
from oryon.core.utils.logging_setup import configure_logging
from oryon.data.storage.json_store import JsonStore
from oryon.data.storage.sql_store import SQLStore


def run(symbol: str = "BTCUSDT") -> None:
    configure_logging()
    config = load_config(Path("oryon_config.yaml"))
    defaults = config.get("defaults", {})
    data_dir = Path(defaults.get("data_dir", "data_store"))
    json_store = JsonStore(data_dir / "json")
    sql_path = Path(defaults.get("sqlite_path", data_dir / "oryon.sqlite"))
    sql_store = SQLStore(sql_path)
    schema_path = Path("oryon/data/storage/schema.sql")
    if not sql_path.exists():
        sql_store.initialize(schema_path)
    loader = BacktestDataLoader(json_store=json_store, sql_store=sql_store)
    timeframes = defaults.get("timeframes", ["1d", "4h", "1h", "15m", "5m"])
    pipeline = AnalyzeAssetPipeline(timeframes=timeframes, execution_timeframe=timeframes[-1])
    bundle = loader.load_bundle(symbol, timeframes, limit=2000)
    config = WalkForwardConfig(lookback=400, forward=40, step=5)
    backtester = WalkForwardBacktester(pipeline, execution_timeframe=timeframes[-1], config=config)
    result = backtester.run(bundle)
    frame, metrics = build_report(result.trades)
    report_dir = Path("backtest_reports") / f"{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    report_dir.mkdir(parents=True, exist_ok=True)
    export_csv(frame, report_dir / "trades.csv")
    export_html(frame, metrics, report_dir / "report.html")
    print("Backtest complete", summarize(result.trades))


if __name__ == "__main__":
    run()
