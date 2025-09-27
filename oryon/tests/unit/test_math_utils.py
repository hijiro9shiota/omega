import pytest

np = pytest.importorskip("numpy")

from oryon.core.utils.math_utils import ema, rolling_window


def test_rolling_window_valid():
    arr = [1, 2, 3, 4]
    windows = rolling_window(arr, 2)
    assert windows.shape == (3, 2)
    assert windows[0, 0] == 1
    assert windows[-1, -1] == 4


def test_rolling_window_invalid():
    with pytest.raises(ValueError):
        rolling_window([1], 2)


def test_ema_computation():
    values = [1, 2, 3]
    result = ema(values, 2)
    assert pytest.approx(result[-1], 0.01) == 2.5
