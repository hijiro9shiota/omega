"""Statistical helper functions."""
from __future__ import annotations

from typing import Iterable

import numpy as np


def zscore(series: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(series), dtype=float)
    if arr.size == 0:
        return arr
    mean = arr.mean()
    std = arr.std(ddof=1) if arr.size > 1 else 0.0
    if std == 0:
        return np.zeros_like(arr)
    return (arr - mean) / std
