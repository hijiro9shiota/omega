"""Generate simple HTML/CSV reports for backtests."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from oryon.backtest.metrics import BacktestMetrics, summarize
from oryon.backtest.walk_forward import BacktestTrade
from oryon.backtest.loader import ensure_directory


def trades_to_frame(trades: Iterable[BacktestTrade]) -> pd.DataFrame:
    rows = []
    for trade in trades:
        rows.append(
            {
                "signal_id": trade.signal.id,
                "symbol": trade.signal.symbol,
                "timeframe": trade.signal.timeframe,
                "direction": trade.signal.direction,
                "entry": trade.signal.entry,
                "stop": trade.signal.stop_loss,
                "rr_expected": trade.signal.rr,
                "rr_realized": trade.rr_realized,
                "outcome": trade.outcome,
                "entry_time": trade.entry_time,
                "exit_time": trade.exit_time,
                "max_favorable": trade.max_favorable,
                "max_adverse": trade.max_adverse,
            }
        )
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.sort_values("entry_time")
    return frame


def build_report(trades: Iterable[BacktestTrade]) -> tuple[pd.DataFrame, BacktestMetrics]:
    trades = list(trades)
    metrics = summarize(trades)
    frame = trades_to_frame(trades)
    return frame, metrics


def export_csv(frame: pd.DataFrame, path: Path) -> None:
    ensure_directory(path)
    frame.to_csv(path, index=False)


def export_html(frame: pd.DataFrame, metrics: BacktestMetrics, path: Path) -> None:
    ensure_directory(path)
    stats = {
        "Total trades": metrics.total_trades,
        "Win rate": f"{metrics.win_rate:.2%}",
        "Average RR": f"{metrics.avg_rr:.2f}",
        "Expectancy": f"{metrics.expectancy:.2f}",
        "Max favorable move": f"{metrics.max_favorable:.2f}",
        "Max adverse move": f"{metrics.max_adverse:.2f}",
    }
    stats_html = "".join(
        f"<li><strong>{name}:</strong> {value}</li>" for name, value in stats.items()
    )
    if frame.empty:
        table_html = "<p>No trades generated.</p>"
    else:
        frame = frame.copy()
        frame["entry_time"] = frame["entry_time"].astype(str)
        frame["exit_time"] = frame["exit_time"].astype(str)
        table_html = frame.to_html(index=False, classes="table table-dark", border=0)
    html = f"""
    <html>
      <head>
        <meta charset=\"utf-8\" />
        <title>Oryon Backtest Report</title>
        <style>
          body {{ font-family: Arial, sans-serif; background: #0b1220; color: #f5f5f5; }}
          h1 {{ color: #7ad7ff; }}
          .table-dark {{ width: 100%; border-collapse: collapse; }}
          .table-dark th, .table-dark td {{ border: 1px solid #1f2a40; padding: 6px; }}
          .table-dark th {{ background: #162033; }}
          .table-dark tr:nth-child(even) {{ background: #111a2b; }}
        </style>
      </head>
      <body>
        <h1>Oryon Backtest Report</h1>
        <ul>{stats_html}</ul>
        {table_html}
      </body>
    </html>
    """
    path.write_text(html, encoding="utf-8")


__all__ = [
    "build_report",
    "export_csv",
    "export_html",
    "trades_to_frame",
]
