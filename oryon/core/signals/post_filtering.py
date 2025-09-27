"""Signal post-processing utilities."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable, List

from .signal_schema import TradingSignal


def deduplicate(signals: Iterable[TradingSignal], window: int = 3) -> List[TradingSignal]:
    buckets = defaultdict(list)
    for signal in signals:
        buckets[(signal.symbol, signal.direction)].append(signal)
    filtered: List[TradingSignal] = []
    for key, bucket in buckets.items():
        bucket.sort(key=lambda s: s.created_at)
        last_ts = None
        for signal in bucket:
            if last_ts is None or (signal.created_at - last_ts).total_seconds() / 60 >= window:
                filtered.append(signal)
                last_ts = signal.created_at
    return filtered


def enforce_quality(signals: Iterable[TradingSignal], min_score: float) -> List[TradingSignal]:
    return [signal for signal in signals if signal.score >= min_score]
