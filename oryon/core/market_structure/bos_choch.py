"""Break of structure (BOS) and change of character (CHOCH) detection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import pandas as pd

from .swings_zigzag import SwingPoint


@dataclass
class StructureEvent:
    timestamp: pd.Timestamp
    type: str  # "BOS" or "CHOCH"
    direction: str  # "bullish" or "bearish"
    swing_index: int


def detect_bos_choch(swings: Iterable[SwingPoint], tolerance: float = 1e-6) -> List[StructureEvent]:
    swings_list = list(swings)
    events: List[StructureEvent] = []
    if len(swings_list) < 3:
        return events
    prev_trend = None
    for idx in range(2, len(swings_list)):
        current = swings_list[idx]
        prev = swings_list[idx - 1]
        older = swings_list[idx - 2]
        if current.type == "high" and prev.type == "low" and older.type == "high":
            if current.price > older.price + tolerance:
                events.append(StructureEvent(timestamp=current.timestamp, type="BOS", direction="bullish", swing_index=idx))
                prev_trend = "bullish"
            elif current.price < older.price - tolerance and prev_trend == "bullish":
                events.append(StructureEvent(timestamp=current.timestamp, type="CHOCH", direction="bearish", swing_index=idx))
                prev_trend = "bearish"
        elif current.type == "low" and prev.type == "high" and older.type == "low":
            if current.price < older.price - tolerance:
                events.append(StructureEvent(timestamp=current.timestamp, type="BOS", direction="bearish", swing_index=idx))
                prev_trend = "bearish"
            elif current.price > older.price + tolerance and prev_trend == "bearish":
                events.append(StructureEvent(timestamp=current.timestamp, type="CHOCH", direction="bullish", swing_index=idx))
                prev_trend = "bullish"
    return events
