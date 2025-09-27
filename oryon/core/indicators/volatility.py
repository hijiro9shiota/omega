"""Volatility analytics."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class VolatilitySuite:
    atr: pd.Series
    atr_percentile: pd.Series
    realized_vol: pd.Series


def average_true_range(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)
    prev_close = close.shift(1)
    tr_components = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1)
    true_range = tr_components.max(axis=1)
    return true_range.rolling(period).mean()


def atr_percentile(atr: pd.Series, lookback: int = 100) -> pd.Series:
    def percentile(values: pd.Series) -> float:
        return float((values <= values.iloc[-1]).mean() * 100)

    return atr.rolling(lookback).apply(percentile, raw=False)


def realized_volatility(df: pd.DataFrame, period: int = 20) -> pd.Series:
    returns = df["close"].pct_change()
    return returns.rolling(period).std() * np.sqrt(252)


def compute_volatility_suite(df: pd.DataFrame) -> VolatilitySuite:
    atr = average_true_range(df)
    atr_pct = atr_percentile(atr.fillna(0))
    rv = realized_volatility(df)
    return VolatilitySuite(atr=atr, atr_percentile=atr_pct, realized_vol=rv)
