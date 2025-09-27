"""Lightweight parallel execution helpers."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def run_in_threads(func: Callable[[T], R], items: Sequence[T], max_workers: int = 4) -> List[R]:
    if not items:
        return []
    results: List[R] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(func, item): item for item in items}
        for future in as_completed(futures):
            results.append(future.result())
    return results
