import pytest

pd = pytest.importorskip("pandas")

from oryon.core.market_structure.bos_choch import StructureEvent, detect_bos_choch
from oryon.core.market_structure.swings_zigzag import SwingPoint


def test_detect_bos_and_choch_sequences():
    idx = pd.date_range("2024-01-01", periods=6, freq="H")
    swings = [
        SwingPoint(index=0, timestamp=idx[0], price=100, type="low"),
        SwingPoint(index=1, timestamp=idx[1], price=110, type="high"),
        SwingPoint(index=2, timestamp=idx[2], price=102, type="low"),
        SwingPoint(index=3, timestamp=idx[3], price=115, type="high"),
        SwingPoint(index=4, timestamp=idx[4], price=108, type="low"),
        SwingPoint(index=5, timestamp=idx[5], price=118, type="high"),
    ]
    events = detect_bos_choch(swings, tolerance=0.01)
    assert any(event.type == "BOS" and event.direction == "bullish" for event in events)

    # Append lower low to trigger CHOCH
    swings.append(SwingPoint(index=6, timestamp=idx[-1] + pd.Timedelta(hours=1), price=95, type="low"))
    events = detect_bos_choch(swings, tolerance=0.01)
    assert any(event.type == "CHOCH" and event.direction == "bearish" for event in events)
