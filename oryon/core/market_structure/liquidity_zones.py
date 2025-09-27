"""Liquidity zone and equal high/low detection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class LiquidityZone:
    level: float
    kind: str
    start: pd.Timestamp
    end: pd.Timestamp
    touches: int


def _group_levels(levels: Iterable[Tuple[pd.Timestamp, float]], tolerance: float) -> List[LiquidityZone]:
    zones: List[LiquidityZone] = []
    for ts, level in levels:
        matched = None
        for zone in zones:
            if abs(zone.level - level) <= tolerance:
                matched = zone
                break
        if matched:
            matched.level = (matched.level * matched.touches + level) / (matched.touches + 1)
            matched.end = ts
            matched.touches += 1
        else:
            zones.append(LiquidityZone(level=level, kind="equal", start=ts, end=ts, touches=2))
    return [zone for zone in zones if zone.touches >= 2]


def detect_equal_highs_lows(df: pd.DataFrame, lookback: int = 20, tolerance: float = 0.0005) -> List[LiquidityZone]:
    highs = df["high"]
    lows = df["low"]
    equal_highs: List[Tuple[pd.Timestamp, float]] = []
    equal_lows: List[Tuple[pd.Timestamp, float]] = []
    for idx in range(1, len(df)):
        if idx < lookback:
            continue
        window_highs = highs.iloc[idx - lookback : idx]
        window_lows = lows.iloc[idx - lookback : idx]
        last_high = highs.iloc[idx - 1]
        last_low = lows.iloc[idx - 1]
        if np.isclose(window_highs.max(), last_high, atol=tolerance * last_high):
            prev_high = window_highs[window_highs != last_high].max()
            if prev_high is not None and np.isclose(prev_high, last_high, atol=tolerance * last_high):
                equal_highs.append((df.index[idx - 1], float(last_high)))
        if np.isclose(window_lows.min(), last_low, atol=tolerance * last_low if last_low != 0 else tolerance):
            prev_low = window_lows[window_lows != last_low].min()
            if prev_low is not None and np.isclose(prev_low, last_low, atol=tolerance * max(abs(last_low), 1e-6)):
                equal_lows.append((df.index[idx - 1], float(last_low)))
    zones = _group_levels(equal_highs, tolerance)
    for zone in zones:
        zone.kind = "equal_high"
    zones_low = _group_levels(equal_lows, tolerance)
    for zone in zones_low:
        zone.kind = "equal_low"
    return zones + zones_low


def session_labels(timestamp: pd.Timestamp) -> str:
    hour = timestamp.hour
    if 23 <= hour or hour < 7:
        return "asia"
    if 7 <= hour < 13:
        return "europe"
    return "us"


def session_high_low(df: pd.DataFrame) -> List[LiquidityZone]:
    grouped = df.groupby(df.index.map(session_labels))
    zones: List[LiquidityZone] = []
    for session, session_df in grouped:
        if session_df.empty:
            continue
        high_idx = session_df["high"].idxmax()
        low_idx = session_df["low"].idxmin()
        zones.append(LiquidityZone(level=float(session_df.loc[high_idx, "high"]), kind=f"{session}_high", start=high_idx, end=high_idx, touches=1))
        zones.append(LiquidityZone(level=float(session_df.loc[low_idx, "low"]), kind=f"{session}_low", start=low_idx, end=low_idx, touches=1))
    return zones


def daily_levels(df: pd.DataFrame) -> List[LiquidityZone]:
    grouped = df.groupby(df.index.date)
    zones: List[LiquidityZone] = []
    for _, day_df in grouped:
        if day_df.empty:
            continue
        high_idx = day_df["high"].idxmax()
        low_idx = day_df["low"].idxmin()
        zones.append(LiquidityZone(level=float(day_df.loc[high_idx, "high"]), kind="daily_high", start=high_idx, end=high_idx, touches=1))
        zones.append(LiquidityZone(level=float(day_df.loc[low_idx, "low"]), kind="daily_low", start=low_idx, end=low_idx, touches=1))
    return zones


def merge_zones(*zone_groups: Iterable[LiquidityZone]) -> List[LiquidityZone]:
    merged: List[LiquidityZone] = []
    for group in zone_groups:
        for zone in group:
            merged.append(zone)
    merged.sort(key=lambda z: z.level)
    return merged
