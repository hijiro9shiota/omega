"""Adaptive zig-zag swing detection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from ..indicators.volatility import average_true_range


@dataclass
class SwingPoint:
    index: int
    timestamp: pd.Timestamp
    price: float
    type: str  # "high" or "low"


def compute_swings(df: pd.DataFrame, atr_period: int = 14, atr_multiplier: float = 1.5) -> List[SwingPoint]:
    if df.empty:
        return []
    atr = average_true_range(df, period=atr_period).fillna(method="bfill").fillna(method="ffill")
    closes = df["close"].to_numpy()
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    swing_points: List[SwingPoint] = []
    last_swing_idx = 0
    last_swing_price = closes[0]
    last_swing_type = "low"
    threshold = atr_multiplier * atr.iloc[0]
    for i in range(1, len(df)):
        if np.isnan(threshold):
            threshold = atr_multiplier * atr.iloc[i]
        price = closes[i]
        move = price - last_swing_price
        if last_swing_type == "low" and move >= threshold:
            high_idx = highs[last_swing_idx:i + 1].argmax() + last_swing_idx
            swing_points.append(SwingPoint(index=high_idx, timestamp=df.index[high_idx], price=float(highs[high_idx]), type="high"))
            last_swing_idx = high_idx
            last_swing_price = highs[high_idx]
            last_swing_type = "high"
            threshold = atr_multiplier * atr.iloc[high_idx]
        elif last_swing_type == "high" and move <= -threshold:
            low_idx = lows[last_swing_idx:i + 1].argmin() + last_swing_idx
            swing_points.append(SwingPoint(index=low_idx, timestamp=df.index[low_idx], price=float(lows[low_idx]), type="low"))
            last_swing_idx = low_idx
            last_swing_price = lows[low_idx]
            last_swing_type = "low"
            threshold = atr_multiplier * atr.iloc[low_idx]
    if not swing_points or swing_points[0].index != 0:
        first_type = "high" if closes[0] > closes[1] else "low"
        swing_points.insert(0, SwingPoint(index=0, timestamp=df.index[0], price=float(closes[0]), type=first_type))
    return swing_points
