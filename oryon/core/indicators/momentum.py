"""Momentum and oscillator indicators."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


@dataclass
class MomentumSuite:
    rsi: pd.Series
    macd: pd.DataFrame
    stochastic: pd.DataFrame
    divergences: Dict[str, pd.Series]


def relative_strength_index(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({"macd": macd_line, "signal": signal_line, "hist": histogram})


def stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, k: int = 14, d: int = 3) -> pd.DataFrame:
    lowest_low = low.rolling(k).min()
    highest_high = high.rolling(k).max()
    k_values = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d_values = k_values.rolling(d).mean()
    return pd.DataFrame({"k": k_values, "d": d_values})


def detect_divergences(price: pd.Series, oscillator: pd.Series, lookback: int = 30) -> Dict[str, pd.Series]:
    """Detect classical bullish/bearish divergences using simple swing comparisons."""
    highs = price.rolling(lookback).apply(lambda x: x.argmax(), raw=False)
    lows = price.rolling(lookback).apply(lambda x: x.argmin(), raw=False)
    bullish = pd.Series(False, index=price.index)
    bearish = pd.Series(False, index=price.index)
    for idx in range(lookback, len(price)):
        window = price.iloc[idx - lookback : idx]
        osc_window = oscillator.iloc[idx - lookback : idx]
        if window.empty or osc_window.empty:
            continue
        price_low_idx = window.idxmin()
        prev_price_low_idx = window[:price_low_idx].idxmin() if window[:price_low_idx].size else None
        if prev_price_low_idx is not None:
            if price[price_low_idx] < price[prev_price_low_idx] and oscillator[price_low_idx] > oscillator[prev_price_low_idx]:
                bullish.iloc[idx] = True
        price_high_idx = window.idxmax()
        prev_price_high_idx = window[:price_high_idx].idxmax() if window[:price_high_idx].size else None
        if prev_price_high_idx is not None:
            if price[price_high_idx] > price[prev_price_high_idx] and oscillator[price_high_idx] < oscillator[prev_price_high_idx]:
                bearish.iloc[idx] = True
    return {"bullish": bullish, "bearish": bearish}


def compute_momentum_suite(df: pd.DataFrame) -> MomentumSuite:
    rsi = relative_strength_index(df["close"])
    macd_df = macd(df["close"])
    stoch = stochastic_oscillator(df["high"], df["low"], df["close"])
    divergences = detect_divergences(df["close"], macd_df["macd"].fillna(0))
    return MomentumSuite(rsi=rsi, macd=macd_df, stochastic=stoch, divergences=divergences)
