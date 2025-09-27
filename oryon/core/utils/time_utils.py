"""Time utilities used across the data pipelines."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def min_max_timestamps(candles: Iterable) -> tuple[datetime | None, datetime | None]:
    first = None
    last = None
    for candle in candles:
        ts = getattr(candle, "timestamp", None)
        if ts is None:
            continue
        if first is None or ts < first:
            first = ts
        if last is None or ts > last:
            last = ts
    return first, last
