"""Turtle soup liquidity grab detection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class TurtleSoupSignal:
    timestamp: pd.Timestamp
    direction: str
    level: float


def detect_turtle_soup(df: pd.DataFrame, lookback: int = 20) -> List[TurtleSoupSignal]:
    signals: List[TurtleSoupSignal] = []
    rolling_high = df["high"].rolling(lookback)
    rolling_low = df["low"].rolling(lookback)
    for idx in range(lookback, len(df)):
        high = df["high"].iloc[idx]
        low = df["low"].iloc[idx]
        prior_high = rolling_high.max().iloc[idx - 1]
        prior_low = rolling_low.min().iloc[idx - 1]
        prev_close = df["close"].iloc[idx - 1]
        close = df["close"].iloc[idx]
        if high > prior_high and close < prev_close:
            signals.append(TurtleSoupSignal(timestamp=df.index[idx], direction="bearish", level=float(prior_high)))
        if low < prior_low and close > prev_close:
            signals.append(TurtleSoupSignal(timestamp=df.index[idx], direction="bullish", level=float(prior_low)))
    return signals
