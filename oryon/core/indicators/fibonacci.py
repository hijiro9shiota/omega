"""Fibonacci utilities built on top of swing analysis."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import pandas as pd


LEVELS = {
    "0.236": 0.236,
    "0.382": 0.382,
    "0.5": 0.5,
    "0.618": 0.618,
    "0.786": 0.786,
    "1.272": 1.272,
    "1.618": 1.618,
}


@dataclass
class FibonacciLevels:
    anchor_high: float
    anchor_low: float
    levels: Dict[str, float]


def project_levels(high: float, low: float) -> FibonacciLevels:
    if high <= low:
        raise ValueError("high must be greater than low")
    diff = high - low
    levels = {name: low + diff * ratio for name, ratio in LEVELS.items()}
    return FibonacciLevels(anchor_high=high, anchor_low=low, levels=levels)


def align_with_swings(df: pd.DataFrame, swing_high: Tuple[pd.Timestamp, float], swing_low: Tuple[pd.Timestamp, float]) -> FibonacciLevels:
    high_ts, high_val = swing_high
    low_ts, low_val = swing_low
    if high_ts <= low_ts:
        anchor_high = float(df.loc[high_ts, "high"])
        anchor_low = float(df.loc[low_ts, "low"])
    else:
        anchor_high = float(df.loc[swing_high[0], "high"])
        anchor_low = float(df.loc[swing_low[0], "low"])
    return project_levels(anchor_high, anchor_low)
