"""ETL pipeline from JSON append-only store into SQL analytics store."""
from __future__ import annotations

import logging
from typing import Iterable, Tuple

from ..connectors.base import Candle
from .json_store import JsonStore
from .sql_store import SQLStore

logger = logging.getLogger(__name__)


def sync_symbol_timeframe(json_store: JsonStore, sql_store: SQLStore, symbol: str, timeframe: str) -> Tuple[int, int]:
    """Synchronize the JSON log with the SQL database for ``symbol`` and ``timeframe``.

    Returns a tuple ``(candles_read, candles_written)``.
    """

    candles = list(json_store.read(symbol, timeframe))
    if not candles:
        logger.info("No candles to sync for %s %s", symbol, timeframe)
        return 0, 0
    written = sql_store.insert_candles(candles)
    logger.info("Synced %s candles for %s %s", written, symbol, timeframe)
    return len(candles), written


def bulk_sync(json_store: JsonStore, sql_store: SQLStore, items: Iterable[Tuple[str, str]]) -> Tuple[int, int]:
    total_read = 0
    total_written = 0
    for symbol, timeframe in items:
        read, written = sync_symbol_timeframe(json_store, sql_store, symbol, timeframe)
        total_read += read
        total_written += written
    return total_read, total_written
