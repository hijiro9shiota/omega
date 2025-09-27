"""Market regime detection using volatility and trend metrics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from ..indicators.moving_averages import compute_moving_averages
from ..indicators.volatility import compute_volatility_suite


@dataclass
class RegimeState:
    label: Literal["trending", "ranging"]
    hurst: float
    trend_strength: float
    volatility_percentile: float


def hurst_exponent(series: pd.Series, max_lag: int = 20) -> float:
    lags = range(2, max_lag)
    tau = [np.sqrt(np.std(np.subtract(series[lag:], series[:-lag]))) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    return poly[0] * 2.0


def detect_regime(df: pd.DataFrame) -> RegimeState:
    ma_suite = compute_moving_averages(df["close"], (20, 50))
    trend_strength = (ma_suite.ema[20] - ma_suite.ema[50]).abs() / df["close"].rolling(50).mean()
    trend_strength = trend_strength.fillna(0)
    vol_suite = compute_volatility_suite(df)
    vol_percentile = vol_suite.atr_percentile.fillna(method="bfill").fillna(0)
    hurst = hurst_exponent(df["close"].dropna()) if len(df) > 40 else 0.5
    trend_metric = float(trend_strength.iloc[-1])
    vol_metric = float(vol_suite.realized_vol.fillna(0).iloc[-1])
    label = "trending"
    if trend_metric < 0.005 or vol_metric < np.nanmedian(vol_suite.realized_vol.fillna(0)):
        label = "ranging"
    return RegimeState(
        label=label,
        hurst=float(hurst),
        trend_strength=float(trend_strength.iloc[-1]),
        volatility_percentile=float(vol_percentile.iloc[-1]),
    )
