"""Connector for Stooq end-of-day data."""
from __future__ import annotations

from datetime import datetime
from io import StringIO
from typing import Iterable, Iterator, Optional

import pandas as pd
import requests

from .base import Candle, DataConnector


_TIMEFRAME_SUFFIX = {
    "1d": "d",
    "1w": "w",
    "1m": "m",
}


class StooqClient(DataConnector):
    """Fetch end-of-day data from Stooq without authentication."""

    name = "stooq"

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self._session = session or requests.Session()

    def fetch(self, symbol: str, timeframe: str, start: Optional[datetime] = None,
              end: Optional[datetime] = None, limit: Optional[int] = None) -> Iterable[Candle]:
        interval = self._resolve_interval(timeframe)
        csv_text = self._download(symbol, interval)
        df = self._parse(csv_text)
        if start is not None:
            df = df[df["date"] >= pd.Timestamp(start)]
        if end is not None:
            df = df[df["date"] <= pd.Timestamp(end)]
        if limit is not None:
            df = df.tail(limit)
        return self._yield(symbol, timeframe, df)

    def _download(self, symbol: str, interval: str) -> str:
        url = f"https://stooq.com/q/d/l/?s={symbol.lower()}&i={interval}"
        resp = self._session.get(url, timeout=20)
        resp.raise_for_status()
        return resp.text

    @staticmethod
    def _parse(csv_text: str) -> pd.DataFrame:
        df = pd.read_csv(StringIO(csv_text))
        if df.empty:
            return df
        df["date"] = pd.to_datetime(df["Date"]) if "Date" in df.columns else pd.to_datetime(df["date"])
        df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
        return df[["date", "open", "high", "low", "close", "volume"]]

    @staticmethod
    def _resolve_interval(timeframe: str) -> str:
        try:
            return _TIMEFRAME_SUFFIX[timeframe]
        except KeyError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Unsupported timeframe for Stooq: {timeframe}") from exc

    def _yield(self, symbol: str, timeframe: str, df: pd.DataFrame) -> Iterator[Candle]:
        for row in df.itertuples():
            yield Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=pd.Timestamp(row.date).to_pydatetime(),
                open=float(row.open),
                high=float(row.high),
                low=float(row.low),
                close=float(row.close),
                volume=float(getattr(row, "volume", 0.0) or 0.0),
                source=self.name,
            )
