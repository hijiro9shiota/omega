"""Base classes and shared models for market data connectors."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional


@dataclass(frozen=True)
class Candle:
    """Normalized OHLCV candle."""

    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str


class DataConnector:
    """Abstract interface for fetching candles from a remote or local source."""

    name: str = "connector"

    def fetch(self, symbol: str, timeframe: str, start: Optional[datetime] = None,
              end: Optional[datetime] = None, limit: Optional[int] = None) -> Iterable[Candle]:
        """Fetch normalized candles for ``symbol``.

        Implementations should yield ``Candle`` instances sorted by timestamp.
        """

        raise NotImplementedError
