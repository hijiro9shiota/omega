import pytest

pd = pytest.importorskip("pandas")

from oryon.core.market_structure.liquidity_zones import (
    LiquidityZone,
    daily_levels,
    detect_equal_highs_lows,
    merge_zones,
)


def make_df():
    idx = pd.date_range("2024-01-01", periods=10, freq="H")
    data = {
        "open": [100, 101, 102, 103, 104, 105, 104, 103, 102, 101],
        "high": [101, 102, 103, 104, 105, 106, 105, 104, 103, 102],
        "low": [99, 100, 101, 102, 103, 104, 103, 102, 101, 100],
        "close": [100.5, 101.5, 102.5, 103.5, 104.5, 105.5, 104.5, 103.5, 102.5, 101.5],
        "volume": [1_000_000] * 10,
    }
    return pd.DataFrame(data, index=idx)


def test_detect_equal_highs_lows_identifies_clusters():
    df = make_df()
    df.loc[df.index[5], "high"] = 106
    df.loc[df.index[4], "high"] = 106
    zones = detect_equal_highs_lows(df, lookback=5, tolerance=0.001)
    assert any(zone.kind == "equal_high" for zone in zones)
    avg_level = [zone.level for zone in zones if zone.kind == "equal_high"][0]
    assert abs(avg_level - 106) < 0.01


def test_daily_levels_returns_high_low_pairs():
    df = make_df()
    zones = daily_levels(df)
    kinds = {zone.kind for zone in zones}
    assert {"daily_high", "daily_low"}.issubset(kinds)
    assert len(zones) == 2


def test_merge_zones_keeps_order():
    df = make_df()
    equal = detect_equal_highs_lows(df, lookback=3, tolerance=0.01)
    daily = daily_levels(df)
    merged = merge_zones(equal, daily)
    levels = [zone.level for zone in merged]
    assert levels == sorted(levels)
