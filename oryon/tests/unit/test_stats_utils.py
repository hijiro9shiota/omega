import pytest

np = pytest.importorskip("numpy")

from oryon.core.utils.stats_utils import zscore


def test_zscore_basic():
    arr = zscore([1, 2, 3])
    assert np.isclose(arr.mean(), 0.0)


def test_zscore_constant():
    arr = zscore([1, 1, 1])
    assert np.all(arr == 0)
