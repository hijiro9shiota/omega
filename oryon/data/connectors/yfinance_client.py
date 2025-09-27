"""Connector for historical data from Yahoo Finance using yfinance."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator, Optional

import pandas as pd

from .base import Candle, DataConnector

try:
    import yfinance as yf
except Exception as exc:  # pragma: no cover - import guard
    raise RuntimeError("yfinance must be installed to use YFinanceClient") from exc


_INTERVAL_MAP = {
    "1m": "1m",
    "2m": "2m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "60m": "60m",
    "90m": "90m",
    "1h": "60m",
    "1d": "1d",
    "1wk": "1wk",
    "1mo": "1mo",
}


class YFinanceClient(DataConnector):
    """Fetch OHLCV data from Yahoo Finance with chunked downloads."""

    name = "yfinance"

    def __init__(self, max_chunk_days: int = 60, session=None) -> None:
        self._max_chunk_days = max_chunk_days
        self._session = session

    def fetch(self, symbol: str, timeframe: str, start: Optional[datetime] = None,
              end: Optional[datetime] = None, limit: Optional[int] = None) -> Iterable[Candle]:
        interval = self._normalize_timeframe(timeframe)
        history = self._download(symbol, interval, start=start, end=end, limit=limit)
        return self._yield_candles(symbol, timeframe, history)

    @staticmethod
    def _normalize_timeframe(timeframe: str) -> str:
        try:
            return _INTERVAL_MAP[timeframe]
        except KeyError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Unsupported timeframe for yfinance: {timeframe}") from exc

    def _download(self, symbol: str, interval: str, start: Optional[datetime],
                  end: Optional[datetime], limit: Optional[int]) -> pd.DataFrame:
        kwargs = {
            "interval": interval,
            "auto_adjust": False,
            "progress": False,
            "prepost": False,
            "actions": False,
            "threads": True,
        }
        if start is not None:
            kwargs["start"] = start
        if end is not None:
            kwargs["end"] = end
        data = yf.download(symbol, **kwargs)
        if data.empty:
            return data
        data = data.rename(columns=str.lower)
        if limit is not None and len(data) > limit:
            data = data.tail(limit)
        return data

    def _yield_candles(self, symbol: str, timeframe: str, df: pd.DataFrame) -> Iterator[Candle]:
        if df.empty:
            return iter([])
        df = df.reset_index()
        for row in df.itertuples():
            timestamp = row.Index if isinstance(row.Index, datetime) else pd.to_datetime(row.Index)
            yield Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=timestamp.to_pydatetime(),
                open=float(row.open),
                high=float(row.high),
                low=float(row.low),
                close=float(row.close),
                volume=float(getattr(row, "volume", 0.0) or 0.0),
                source=self.name,
            )
