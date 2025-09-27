"""Simple rate limiting utilities for data ingestion."""
from __future__ import annotations

import threading
import time
from collections import deque
from typing import Deque, Dict, Optional


class RateLimiter:
    """Thread-safe fixed-window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self._max_requests = max_requests
        self._window = window_seconds
        self._lock = threading.Lock()
        self._hits: Dict[str, Deque[float]] = {}

    def acquire(self, key: str = "default", block: bool = True, timeout: Optional[float] = None) -> bool:
        """Acquire permission for ``key``.

        Returns ``True`` if the request is allowed. When ``block`` is True, the
        method will sleep until the rate limit allows a new request or until
        ``timeout`` expires.
        """

        end_time = None if timeout is None else time.monotonic() + timeout
        while True:
            with self._lock:
                now = time.monotonic()
                hits = self._hits.setdefault(key, deque())
                while hits and now - hits[0] > self._window:
                    hits.popleft()
                if len(hits) < self._max_requests:
                    hits.append(now)
                    return True
                remaining = self._window - (now - hits[0])
            if not block:
                return False
            if end_time is not None and remaining > end_time - time.monotonic():
                return False
            time.sleep(max(remaining, 0.01))

    def __call__(self, key: str = "default", block: bool = True, timeout: Optional[float] = None) -> bool:
        return self.acquire(key=key, block=block, timeout=timeout)
