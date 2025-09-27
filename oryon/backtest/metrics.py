"""Backtest metrics computations."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable

from .walk_forward import BacktestTrade


@dataclass
class BacktestMetrics:
    total_trades: int
    win_rate: float
    avg_rr: float
    expectancy: float
    max_adverse: float
    max_favorable: float


def summarize(trades: Iterable[BacktestTrade]) -> BacktestMetrics:
    trades = list(trades)
    if not trades:
        return BacktestMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0)
    wins = [t for t in trades if t.outcome == "target"]
    realized_rr = [t.rr_realized for t in trades]
    max_adv = max((t.max_adverse for t in trades), default=0.0)
    max_fav = max((t.max_favorable for t in trades), default=0.0)
    expectancy = mean(realized_rr) if realized_rr else 0.0
    avg_rr = mean([rr for rr in realized_rr if rr != 0]) if realized_rr else 0.0
    win_rate = len(wins) / len(trades)
    return BacktestMetrics(
        total_trades=len(trades),
        win_rate=win_rate,
        avg_rr=avg_rr,
        expectancy=expectancy,
        max_adverse=max_adv,
        max_favorable=max_fav,
    )


__all__ = ["BacktestMetrics", "summarize"]
