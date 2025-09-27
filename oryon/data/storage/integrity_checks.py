"""Integrity checks for candle datasets."""
from __future__ import annotations

from typing import Iterable, List, Tuple

from ..connectors.base import Candle


class IntegrityError(Exception):
    """Raised when a dataset fails integrity validation."""


def check_monotonic(candles: Iterable[Candle]) -> None:
    last_ts = None
    for candle in candles:
        if last_ts and candle.timestamp <= last_ts:
            raise IntegrityError(f"Timestamps not strictly increasing: {candle.timestamp} <= {last_ts}")
        last_ts = candle.timestamp


def check_ohlc_bounds(candles: Iterable[Candle]) -> None:
    for candle in candles:
        if not (candle.low <= candle.open <= candle.high):
            raise IntegrityError(f"Open price out of bounds for {candle}")
        if not (candle.low <= candle.close <= candle.high):
            raise IntegrityError(f"Close price out of bounds for {candle}")
        if candle.low > candle.high:
            raise IntegrityError(f"Low greater than high for {candle}")


def run_all_checks(candles: Iterable[Candle]) -> List[str]:
    candles_list = list(candles)
    check_monotonic(candles_list)
    check_ohlc_bounds(candles_list)
    return ["monotonic", "ohlc_bounds"]


def summarize_gaps(candles: Iterable[Candle]) -> Tuple[int, List[Tuple[int, int]]]:
    candles_list = list(candles)
    if not candles_list:
        return 0, []
    candles_list.sort(key=lambda c: c.timestamp)
    expected = None
    gaps: List[Tuple[int, int]] = []
    for candle in candles_list:
        ts = int(candle.timestamp.timestamp())
        if expected is not None and ts != expected:
            gaps.append((expected, ts))
        expected = ts
    return len(gaps), gaps
