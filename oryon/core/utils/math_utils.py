"""Mathematical helper functions."""
from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np


def rolling_window(arr: Sequence[float], window: int) -> np.ndarray:
    if window <= 0:
        raise ValueError("window must be positive")
    if len(arr) < window:
        raise ValueError("array shorter than window")
    array = np.asarray(arr, dtype=float)
    shape = array.shape[0] - window + 1, window
    strides = array.strides + (array.strides[-1],)
    return np.lib.stride_tricks.as_strided(array, shape=shape, strides=strides)


def ema(values: Iterable[float], period: int) -> np.ndarray:
    alpha = 2 / (period + 1)
    values = np.asarray(list(values), dtype=float)
    if values.size == 0:
        return values
    ema_values = np.empty_like(values)
    ema_values[0] = values[0]
    for i in range(1, values.size):
        ema_values[i] = alpha * values[i] + (1 - alpha) * ema_values[i - 1]
    return ema_values
