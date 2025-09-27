"""Risk-to-reward and trade level helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pandas as pd


@dataclass
class RiskResult:
    entry: float
    stop_loss: float
    targets: Tuple[float, ...]
    rr: float


def compute_rr(direction: str, entry: float, stop_loss: float, targets: Tuple[float, ...]) -> RiskResult:
    if direction not in {"long", "short"}:
        raise ValueError("direction must be 'long' or 'short'")
    if stop_loss <= 0 or entry <= 0:
        raise ValueError("prices must be positive")
    if not targets:
        raise ValueError("at least one target required")
    rr_values = []
    for target in targets:
        if direction == "long":
            rr = (target - entry) / (entry - stop_loss)
        else:
            rr = (entry - target) / (stop_loss - entry)
        rr_values.append(rr)
    return RiskResult(entry=entry, stop_loss=stop_loss, targets=targets, rr=float(sum(rr_values) / len(rr_values)))


def default_levels(direction: str, recent_low: float, recent_high: float, atr: float) -> Tuple[float, Tuple[float, ...]]:
    if direction == "long":
        entry = recent_high
        targets = (recent_high + atr, recent_high + atr * 1.5, recent_high + atr * 2)
    else:
        entry = recent_low
        targets = (recent_low - atr, recent_low - atr * 1.5, recent_low - atr * 2)
    return entry, targets


def build_trade_levels(direction: str, df: pd.DataFrame, atr_series: pd.Series) -> RiskResult:
    swing_low = df["low"].iloc[-5:].min()
    swing_high = df["high"].iloc[-5:].max()
    atr = float(atr_series.iloc[-1]) if not atr_series.empty else float((swing_high - swing_low) / 2)
    entry, targets = default_levels(direction, swing_low, swing_high, atr)
    stop = swing_low if direction == "long" else swing_high
    if direction == "long":
        stop = min(stop, entry - atr * 0.5)
    else:
        stop = max(stop, entry + atr * 0.5)
    return compute_rr(direction=direction, entry=entry, stop_loss=stop, targets=targets)
