"""Connector using Binance public REST endpoints without authentication."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator, Optional

import requests

from .base import Candle, DataConnector


class BinanceRestPublic(DataConnector):
    """Fetch OHLCV data via Binance public REST API."""

    name = "binance_public"

    def __init__(self, base_url: str = "https://api.binance.com", session: Optional[requests.Session] = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()

    def fetch(self, symbol: str, timeframe: str, start: Optional[datetime] = None,
              end: Optional[datetime] = None, limit: Optional[int] = None) -> Iterable[Candle]:
        params = {
            "symbol": symbol.upper(),
            "interval": timeframe,
        }
        if limit is not None:
            params["limit"] = min(limit, 1000)
        if start is not None:
            params["startTime"] = int(start.timestamp() * 1000)
        if end is not None:
            params["endTime"] = int(end.timestamp() * 1000)
        url = f"{self._base_url}/api/v3/klines"
        resp = self._session.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return self._yield(symbol, timeframe, resp.json())

    def _yield(self, symbol: str, timeframe: str, rows) -> Iterator[Candle]:
        for row in rows:
            open_time = int(row[0])
            open_, high, low, close, volume = map(float, row[1:6])
            yield Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.utcfromtimestamp(open_time / 1000),
                open=open_,
                high=high,
                low=low,
                close=close,
                volume=float(volume),
                source=self.name,
            )
