"""Task scheduler orchestrating data ingestion across connectors."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence

from ..connectors.base import Candle, DataConnector
from ..storage.json_store import JsonStore
from .cache_manager import CacheManager
from .rate_limit import RateLimiter

logger = logging.getLogger(__name__)


class FetchScheduler:
    """Coordinate data ingestion, caching and persistence."""

    def __init__(self, connectors: Sequence[DataConnector], json_store: JsonStore,
                 cache: CacheManager, rate_limiter: RateLimiter, cache_namespace: str = "candles") -> None:
        if not connectors:
            raise ValueError("At least one connector required")
        self._connectors = list(connectors)
        self._json_store = json_store
        self._cache = cache
        self._rate_limiter = rate_limiter
        self._namespace = cache_namespace

    def fetch_symbol(self, symbol: str, timeframes: Iterable[str], start: Optional[datetime] = None,
                     end: Optional[datetime] = None, force_refresh: bool = False) -> Dict[str, List[Candle]]:
        results: Dict[str, List[Candle]] = {}
        for timeframe in timeframes:
            candles = self._fetch_timeframe(symbol, timeframe, start=start, end=end, force_refresh=force_refresh)
            if candles:
                self._json_store.append(symbol, timeframe, candles)
                results[timeframe] = candles
        return results

    def _fetch_timeframe(self, symbol: str, timeframe: str, start: Optional[datetime], end: Optional[datetime],
                         force_refresh: bool) -> List[Candle]:
        cache_key = self._cache_key(symbol, timeframe, start, end)
        if not force_refresh:
            cached = self._cache.get(self._namespace, cache_key)
            if cached is not None:
                logger.debug("Cache hit for %s %s", symbol, timeframe)
                return [self._json_store.candle_from_dict(payload) for payload in cached["value"]]
        for connector in self._connectors:
            if not self._rate_limiter.acquire(connector.name, timeout=5):
                logger.warning("Rate limit exceeded for connector %s", connector.name)
                continue
            try:
                candles = list(connector.fetch(symbol, timeframe, start=start, end=end))
            except Exception as exc:  # pragma: no cover - network errors
                logger.exception("Connector %s failed for %s %s: %s", connector.name, symbol, timeframe, exc)
                continue
            if not candles:
                logger.info("Connector %s returned no data for %s %s", connector.name, symbol, timeframe)
                continue
            payload = [self._json_store.candle_to_dict(c) for c in candles]
            self._cache.set(self._namespace, cache_key, payload)
            return candles
        return []

    @staticmethod
    def _cache_key(symbol: str, timeframe: str, start: Optional[datetime], end: Optional[datetime]) -> str:
        return "|".join([
            symbol,
            timeframe,
            start.isoformat() if start else "",
            end.isoformat() if end else "",
        ])
