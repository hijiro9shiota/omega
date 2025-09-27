"""SQL storage using SQLite or DuckDB for analytical workloads."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from ..connectors.base import Candle
from ..ingestion.symbol_universe import SymbolRecord


class SQLStore:
    """Provide a lightweight abstraction over SQLite for Oryon."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self._path)
        self._connection.row_factory = sqlite3.Row

    def initialize(self, schema_path: Path) -> None:
        with open(schema_path, "r", encoding="utf-8") as fh:
            schema_sql = fh.read()
        with self._connection:
            self._connection.executescript(schema_sql)

    @contextmanager
    def cursor(self):
        cur = self._connection.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def upsert_symbols(self, records: Sequence[SymbolRecord]) -> None:
        with self._connection:
            self._connection.executemany(
                """
                INSERT INTO symbols(symbol, exchange, type, base, quote, aliases, updated_at)
                VALUES (:symbol, :exchange, :asset_type, :base, :quote, json(:aliases), :updated_at)
                ON CONFLICT(symbol) DO UPDATE SET
                    exchange=excluded.exchange,
                    type=excluded.type,
                    base=excluded.base,
                    quote=excluded.quote,
                    aliases=excluded.aliases,
                    updated_at=excluded.updated_at
                """,
                [
                    {
                        "symbol": rec.symbol,
                        "exchange": rec.exchange,
                        "asset_type": rec.asset_type,
                        "base": rec.base,
                        "quote": rec.quote,
                        "aliases": json_dumps(rec.aliases or []),
                        "updated_at": rec.updated_at,
                    }
                    for rec in records
                ],
            )

    def insert_candles(self, candles: Iterable[Candle]) -> int:
        rows = [
            (
                candle.symbol,
                candle.timeframe,
                int(candle.timestamp.timestamp()),
                candle.open,
                candle.high,
                candle.low,
                candle.close,
                candle.volume,
            )
            for candle in candles
        ]
        if not rows:
            return 0
        with self._connection:
            self._connection.executemany(
                """
                INSERT OR REPLACE INTO candles(symbol, tf, ts, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def fetch_candles(self, symbol: str, timeframe: str, limit: Optional[int] = None) -> List[Candle]:
        query = "SELECT * FROM candles WHERE symbol=? AND tf=? ORDER BY ts"
        params = [symbol, timeframe]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        return [
            Candle(
                symbol=row["symbol"],
                timeframe=row["tf"],
                timestamp=datetime.fromtimestamp(row["ts"]),
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
                source="sql",
            )
            for row in rows
        ]


def json_dumps(value) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


from datetime import datetime  # noqa: E402  # imported late for sqlite timestamp conversion
