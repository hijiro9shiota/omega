from datetime import datetime, timezone

import pytest

from oryon.data.connectors.base import Candle
from oryon.data.storage.integrity_checks import IntegrityError, check_monotonic, check_ohlc_bounds


def candle(ts: int, open_: float = 1.0, high: float = 2.0, low: float = 0.5, close: float = 1.5) -> Candle:
    return Candle(
        symbol="BTCUSDT",
        timeframe="1h",
        timestamp=datetime.fromtimestamp(ts, tz=timezone.utc),
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=1.0,
        source="test",
    )


def test_check_monotonic_ok():
    check_monotonic([candle(1), candle(2)])


def test_check_monotonic_raises():
    with pytest.raises(IntegrityError):
        check_monotonic([candle(2), candle(1)])


def test_check_ohlc_bounds_ok():
    check_ohlc_bounds([candle(1)])


def test_check_ohlc_bounds_raises():
    with pytest.raises(IntegrityError):
        check_ohlc_bounds([candle(1, open_=3.0)])
