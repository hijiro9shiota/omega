"""Risk filters for market conditions."""
from __future__ import annotations

from typing import Dict

import pandas as pd


def volatility_filter(vol_percentile: float, threshold: float = 90) -> bool:
    """Return True if volatility is within acceptable range."""
    return vol_percentile <= threshold


def liquidity_filter(df: pd.DataFrame, min_volume: float) -> bool:
    rolling = df["volume"].rolling(10).mean()
    recent_volume = rolling.iloc[-1]
    if pd.isna(recent_volume):
        recent_volume = df["volume"].iloc[-1]
    return recent_volume >= min_volume


def combine_filters(result_map: Dict[str, bool]) -> bool:
    return all(result_map.values())
