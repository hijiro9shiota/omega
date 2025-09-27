"""Connector for reading OHLCV candles from local CSV files."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, Optional

import pandas as pd

from .base import Candle, DataConnector


class FileCSVClient(DataConnector):
    """Load candles from local CSV files compatible with the demo mode."""

    name = "file_csv"

    def __init__(self, root_dir: Path) -> None:
        self._root_dir = Path(root_dir)

    def fetch(self, symbol: str, timeframe: str, start: Optional[pd.Timestamp] = None,
              end: Optional[pd.Timestamp] = None, limit: Optional[int] = None) -> Iterable[Candle]:
        path = self._resolve_path(symbol, timeframe)
        df = self._load_csv(path)
        if start is not None:
            df = df[df["timestamp"] >= pd.Timestamp(start)]
        if end is not None:
            df = df[df["timestamp"] <= pd.Timestamp(end)]
        if limit is not None:
            df = df.tail(limit)
        return self._yield(symbol, timeframe, df)

    def _resolve_path(self, symbol: str, timeframe: str) -> Path:
        filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"
        path = self._root_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"CSV not found for {symbol} {timeframe}: {path}")
        return path

    @staticmethod
    def _load_csv(path: Path) -> pd.DataFrame:
        df = pd.read_csv(path)
        if "timestamp" not in df.columns:
            raise ValueError(f"CSV {path} missing 'timestamp' column")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        for col in ("open", "high", "low", "close", "volume"):
            if col not in df.columns:
                raise ValueError(f"CSV {path} missing '{col}' column")
        return df

    def _yield(self, symbol: str, timeframe: str, df: pd.DataFrame) -> Iterator[Candle]:
        for row in df.itertuples():
            yield Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=pd.Timestamp(row.timestamp).to_pydatetime(),
                open=float(row.open),
                high=float(row.high),
                low=float(row.low),
                close=float(row.close),
                volume=float(row.volume),
                source=self.name,
            )
