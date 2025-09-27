import time

from oryon.data.ingestion.rate_limit import RateLimiter


def test_rate_limiter_allows_within_window(monkeypatch):
    limiter = RateLimiter(2, 1)
    times = [0]

    def fake_monotonic():
        return times[0]

    monkeypatch.setattr(time, "monotonic", fake_monotonic)
    assert limiter.acquire()
    assert limiter.acquire()
    times[0] = 1.1
    assert limiter.acquire()


def test_rate_limiter_blocks_when_exceeded(monkeypatch):
    limiter = RateLimiter(1, 10)
    monkeypatch.setattr(time, "sleep", lambda duration: None)
    monkeypatch.setattr(time, "monotonic", lambda: 0)
    assert limiter.acquire(block=False) is True
    assert limiter.acquire(block=False) is False
