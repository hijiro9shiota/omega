"""Price action candlestick pattern detection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass
class CandlePatterns:
    engulfing: pd.Series
    pin_bar: pd.Series
    inside_bar: pd.Series


def detect_engulfing(df: pd.DataFrame) -> pd.Series:
    body = (df["close"] - df["open"]).abs()
    prev_body = body.shift(1)
    prev_direction = (df["close"] - df["open"]).shift(1)
    direction = df["close"] - df["open"]
    engulf = (body > prev_body) & (direction * prev_direction < 0)
    engulf &= df["high"] >= df["high"].shift(1)
    engulf &= df["low"] <= df["low"].shift(1)
    return engulf.fillna(False)


def detect_pin_bar(df: pd.DataFrame, threshold: float = 0.66) -> pd.Series:
    high = df["high"]
    low = df["low"]
    open_ = df["open"]
    close = df["close"]
    body = (close - open_).abs()
    upper_wick = high - close.clip(lower=open_)
    lower_wick = open_.clip(lower=close) - low
    range_ = high - low
    bullish_pin = (lower_wick / range_ > threshold) & (body / range_ < 0.3)
    bearish_pin = (upper_wick / range_ > threshold) & (body / range_ < 0.3)
    return (bullish_pin | bearish_pin).fillna(False)


def detect_inside_bar(df: pd.DataFrame) -> pd.Series:
    return ((df["high"] <= df["high"].shift(1)) & (df["low"] >= df["low"].shift(1))).fillna(False)


def compute_candle_patterns(df: pd.DataFrame) -> CandlePatterns:
    engulf = detect_engulfing(df)
    pin = detect_pin_bar(df)
    inside = detect_inside_bar(df)
    return CandlePatterns(engulfing=engulf, pin_bar=pin, inside_bar=inside)


def summarize_patterns(patterns: CandlePatterns) -> Dict[str, int]:
    return {
        "engulfing": int(patterns.engulfing.sum()),
        "pin_bar": int(patterns.pin_bar.sum()),
        "inside_bar": int(patterns.inside_bar.sum()),
    }
