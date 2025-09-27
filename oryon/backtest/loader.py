"""Data loading utilities for backtests."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import pandas as pd

from oryon.data.connectors.base import Candle
from oryon.data.storage.json_store import JsonStore
from oryon.data.storage.sql_store import SQLStore


@dataclass
class BacktestDataBundle:
    """Candlestick data for a symbol across multiple timeframes."""

    symbol: str
    candles: Dict[str, pd.DataFrame]

    def window(self, end: pd.Timestamp, lookback: Optional[int] = None) -> Dict[str, pd.DataFrame]:
        """Return data sliced up to ``end`` for each timeframe."""

        windowed: Dict[str, pd.DataFrame] = {}
        for tf, df in self.candles.items():
            sliced = df.loc[:end]
            if lookback is not None and lookback > 0:
                sliced = sliced.tail(lookback)
            if sliced.empty:
                raise ValueError(f"No data available for {self.symbol} {tf} up to {end}")
            windowed[tf] = sliced
        return windowed


class BacktestDataLoader:
    """Load candles for backtests from JSON and/or SQL stores."""

    def __init__(
        self,
        json_store: Optional[JsonStore] = None,
        sql_store: Optional[SQLStore] = None,
    ) -> None:
        if json_store is None and sql_store is None:
            raise ValueError("At least one storage backend must be provided")
        self.json_store = json_store
        self.sql_store = sql_store

    def load_bundle(
        self,
        symbol: str,
        timeframes: Sequence[str],
        limit: Optional[int] = None,
    ) -> BacktestDataBundle:
        candles_by_tf: Dict[str, pd.DataFrame] = {}
        for timeframe in timeframes:
            candles = self._fetch_candles(symbol, timeframe, limit)
            if not candles:
                raise FileNotFoundError(f"No candles for {symbol} {timeframe}")
            candles_by_tf[timeframe] = candles_to_dataframe(candles)
        return BacktestDataBundle(symbol=symbol, candles=candles_by_tf)

    def _fetch_candles(
        self, symbol: str, timeframe: str, limit: Optional[int]
    ) -> List[Candle]:
        rows: List[Candle] = []
        if self.sql_store is not None:
            rows.extend(self.sql_store.fetch_candles(symbol, timeframe, limit=limit))
        if (not rows or (limit and len(rows) < limit)) and self.json_store is not None:
            json_rows = list(self.json_store.read(symbol, timeframe))
            if limit is not None:
                json_rows = json_rows[-limit:]
            rows.extend(json_rows)
        rows.sort(key=lambda candle: candle.timestamp)
        if limit is not None:
            rows = rows[-limit:]
        return rows


def candles_to_dataframe(candles: Iterable[Candle]) -> pd.DataFrame:
    """Convert an iterable of :class:`Candle` into a OHLCV DataFrame."""

    records = [
        {
            "timestamp": candle.timestamp,
            "open": candle.open,
            "high": candle.high,
            "low": candle.low,
            "close": candle.close,
            "volume": candle.volume,
        }
        for candle in candles
    ]
    if not records:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"]).set_index(
            pd.DatetimeIndex([], name="timestamp")
        )
    df = pd.DataFrame.from_records(records).set_index("timestamp")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def infer_timeframe_from_index(index: pd.DatetimeIndex) -> Optional[pd.Timedelta]:
    """Best-effort inference of timeframe duration for reporting."""

    if len(index) < 2:
        return None
    diffs = index.to_series().diff().dropna()
    if diffs.empty:
        return None
    return pd.to_timedelta(diffs.mode().iloc[0])


def ensure_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


__all__ = [
    "BacktestDataBundle",
    "BacktestDataLoader",
    "candles_to_dataframe",
    "infer_timeframe_from_index",
    "ensure_directory",
]
