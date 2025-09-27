"""Walk-forward backtesting utilities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Sequence

import pandas as pd

from oryon.backtest.loader import BacktestDataBundle
from oryon.core.pipelines.analyze_asset import AnalyzeAssetPipeline
from oryon.core.signals.signal_schema import TradingSignal


@dataclass
class BacktestTrade:
    signal: TradingSignal
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    outcome: str
    rr_realized: float
    max_adverse: float
    max_favorable: float


@dataclass
class WalkForwardConfig:
    lookback: int = 400
    forward: int = 40
    step: int = 5


@dataclass
class WalkForwardResult:
    trades: List[BacktestTrade]
    started_at: datetime
    finished_at: datetime


class WalkForwardBacktester:
    def __init__(
        self,
        pipeline: AnalyzeAssetPipeline,
        execution_timeframe: str,
        config: WalkForwardConfig,
    ) -> None:
        self.pipeline = pipeline
        self.execution_timeframe = execution_timeframe
        self.config = config

    def run(self, bundle: BacktestDataBundle) -> WalkForwardResult:
        started_at = datetime.utcnow()
        exec_df = bundle.candles[self.execution_timeframe]
        trades: List[BacktestTrade] = []
        for idx in range(self.config.lookback, len(exec_df) - self.config.forward, self.config.step):
            current_ts = exec_df.index[idx]
            window = bundle.window(current_ts, lookback=self.config.lookback)
            signals = self.pipeline.run(bundle.symbol, window)
            if not signals:
                continue
            forward_df = exec_df.iloc[idx + 1 : idx + 1 + self.config.forward]
            for signal in signals:
                trade = evaluate_signal(signal, forward_df)
                if trade is not None:
                    trades.append(trade)
        finished_at = datetime.utcnow()
        return WalkForwardResult(trades=trades, started_at=started_at, finished_at=finished_at)


def evaluate_signal(signal: TradingSignal, forward_df: pd.DataFrame) -> BacktestTrade | None:
    if forward_df.empty:
        return None
    entry_time = forward_df.index[0]
    direction = signal.direction
    stop = signal.stop_loss
    targets = list(signal.take_profits)
    if not targets:
        return None
    rr_realized = 0.0
    outcome = "open"
    max_fav = 0.0
    max_adv = 0.0
    exit_time = forward_df.index[-1]
    for ts, candle in forward_df.iterrows():
        high = candle["high"]
        low = candle["low"]
        exit_time = ts
        if direction == "long":
            max_fav = max(max_fav, float(high - signal.entry))
            max_adv = max(max_adv, float(max(0.0, signal.entry - low)))
            if low <= stop:
                rr_realized = -1.0
                outcome = "stop"
                break
            for target in targets:
                if high >= target:
                    denom = max(signal.entry - stop, 1e-9)
                    rr_realized = (target - signal.entry) / denom
                    outcome = "target"
                    break
            if outcome == "target":
                break
        else:
            max_fav = max(max_fav, float(signal.entry - low))
            max_adv = max(max_adv, float(max(0.0, high - signal.entry)))
            if high >= stop:
                rr_realized = -1.0
                outcome = "stop"
                break
            for target in targets:
                if low <= target:
                    denom = max(stop - signal.entry, 1e-9)
                    rr_realized = (signal.entry - target) / denom
                    outcome = "target"
                    break
            if outcome == "target":
                break
    if outcome == "open":
        outcome = "forward_end"
    return BacktestTrade(
        signal=signal,
        entry_time=entry_time,
        exit_time=exit_time,
        outcome=outcome,
        rr_realized=rr_realized,
        max_favorable=max_fav,
        max_adverse=max_adv,
    )


__all__ = [
    "BacktestTrade",
    "WalkForwardConfig",
    "WalkForwardResult",
    "WalkForwardBacktester",
    "evaluate_signal",
]
