"""Connector using ccxt public endpoints for crypto exchanges."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator, Optional

from dateutil import tz

from .base import Candle, DataConnector

try:
    import ccxt
except Exception as exc:  # pragma: no cover - import guard
    raise RuntimeError("ccxt must be installed to use CCXTPublicClient") from exc


class CCXTPublicClient(DataConnector):
    """Fetch OHLCV data via ccxt public endpoints."""

    name = "ccxt"

    def __init__(self, exchange: str = "binance", enable_rate_limit: bool = True) -> None:
        if not hasattr(ccxt, exchange):  # pragma: no cover - defensive
            raise ValueError(f"Unknown ccxt exchange: {exchange}")
        exchange_cls = getattr(ccxt, exchange)
        self._client = exchange_cls({"enableRateLimit": enable_rate_limit})

    def fetch(self, symbol: str, timeframe: str, start: Optional[datetime] = None,
              end: Optional[datetime] = None, limit: Optional[int] = None) -> Iterable[Candle]:
        since = int(start.timestamp() * 1000) if start else None
        ohlcv = self._client.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
        return self._yield(symbol, timeframe, ohlcv)

    def _yield(self, symbol: str, timeframe: str, rows) -> Iterator[Candle]:
        tz_utc = tz.UTC
        for ts, open_, high, low, close, volume in rows:
            yield Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.fromtimestamp(ts / 1000, tz=tz_utc),
                open=float(open_),
                high=float(high),
                low=float(low),
                close=float(close),
                volume=float(volume or 0.0),
                source=self.name,
            )
