"""Moving average indicator computations.

These helpers operate on pandas Series objects and return aligned Series with
NaNs preserved at the head of the window.  They are designed to be composable
and fast enough for multi-timeframe analysis where hundreds of thousands of
rows might be processed during a typical research session.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd

from ..utils.math_utils import ema


@dataclass
class MovingAverageSuite:
    """Container returned by :func:`compute_moving_averages`.

    Attributes
    ----------
    sma : Dict[int, pd.Series]
        Simple moving averages indexed by period.
    ema : Dict[int, pd.Series]
        Exponential moving averages indexed by period.
    wma : Dict[int, pd.Series]
        Weighted moving averages (linear weights) indexed by period.
    kama : Dict[int, pd.Series]
        Kaufman's adaptive moving averages indexed by period.
    """

    sma: Dict[int, pd.Series]
    ema: Dict[int, pd.Series]
    wma: Dict[int, pd.Series]
    kama: Dict[int, pd.Series]


def _kama(series: pd.Series, period: int, fast: int = 2, slow: int = 30) -> pd.Series:
    price = series.astype(float)
    change = price.diff(period).abs()
    volatility = price.diff().abs().rolling(period).sum()
    er = change / np.where(volatility == 0, np.nan, volatility)
    er = er.clip(0, 1)
    sc = (er * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)) ** 2
    kama = price.copy()
    for i in range(1, len(price)):
        if np.isnan(sc.iloc[i]):
            kama.iloc[i] = kama.iloc[i - 1]
        else:
            kama.iloc[i] = kama.iloc[i - 1] + sc.iloc[i] * (price.iloc[i] - kama.iloc[i - 1])
    return kama


def _wma(series: pd.Series, period: int) -> pd.Series:
    weights = np.arange(1, period + 1)
    def weighted(values: pd.Series) -> float:
        return float(np.dot(values.to_numpy(), weights) / weights.sum())

    return series.rolling(period).apply(weighted, raw=False)


def _ema(series: pd.Series, period: int) -> pd.Series:
    values = ema(series.fillna(method="ffill").fillna(method="bfill"), period)
    return pd.Series(values, index=series.index)


def compute_moving_averages(series: pd.Series, periods: tuple[int, ...]) -> MovingAverageSuite:
    """Compute a suite of moving averages for the given close series."""
    if series.empty:
        raise ValueError("series must not be empty")
    unique_periods = sorted(set(int(p) for p in periods if p > 0))
    if not unique_periods:
        raise ValueError("at least one positive period required")

    sma = {p: series.rolling(p).mean() for p in unique_periods}
    ema_values = {p: _ema(series, p) for p in unique_periods}
    wma = {p: _wma(series, p) for p in unique_periods}
    kama = {p: _kama(series, p) for p in unique_periods}
    return MovingAverageSuite(sma=sma, ema=ema_values, wma=wma, kama=kama)
