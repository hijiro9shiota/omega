import pytest

pd = pytest.importorskip("pandas")

from oryon.core.market_structure.bos_choch import StructureEvent
from oryon.core.market_structure.order_blocks import find_order_blocks


def test_find_bullish_order_block_identifies_last_bearish_candle():
    idx = pd.date_range("2024-01-01", periods=6, freq="H")
    df = pd.DataFrame(
        {
            "open": [100, 99, 98, 99, 101, 103],
            "high": [101, 100, 99, 102, 104, 105],
            "low": [99, 98, 97, 98, 100, 102],
            "close": [99, 98, 97, 101, 103, 104],
            "volume": [1_000_000] * 6,
        },
        index=idx,
    )
    events = [StructureEvent(timestamp=idx[4], type="BOS", direction="bullish", swing_index=4)]
    blocks = find_order_blocks(df, events, lookback=5)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.direction == "bullish"
    assert block.timestamp == idx[3]
    assert not block.mitigated


def test_find_bearish_order_block():
    idx = pd.date_range("2024-01-01", periods=6, freq="H")
    df = pd.DataFrame(
        {
            "open": [105, 106, 107, 106, 104, 102],
            "high": [106, 107, 108, 107, 105, 103],
            "low": [104, 105, 106, 104, 102, 100],
            "close": [106, 107, 108, 105, 103, 101],
            "volume": [1_000_000] * 6,
        },
        index=idx,
    )
    events = [StructureEvent(timestamp=idx[4], type="BOS", direction="bearish", swing_index=4)]
    blocks = find_order_blocks(df, events, lookback=5)
    assert len(blocks) == 1
    assert blocks[0].direction == "bearish"
