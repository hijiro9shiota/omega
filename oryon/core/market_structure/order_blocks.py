"""Order block detection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd

from .bos_choch import StructureEvent


@dataclass
class OrderBlock:
    timestamp: pd.Timestamp
    direction: str
    open: float
    high: float
    low: float
    close: float
    mitigated: bool


def find_order_blocks(df: pd.DataFrame, structure_events: List[StructureEvent], lookback: int = 20) -> List[OrderBlock]:
    blocks: List[OrderBlock] = []
    for event in structure_events:
        if event.type != "BOS":
            continue
        idx = df.index.get_loc(event.timestamp, method="pad")
        start_idx = max(0, idx - lookback)
        window = df.iloc[start_idx: idx + 1]
        if window.empty:
            continue
        if event.direction == "bullish":
            bearish = window[window["close"] < window["open"]]
            if bearish.empty:
                continue
            last_bearish = bearish.iloc[-1]
            block = OrderBlock(
                timestamp=last_bearish.name,
                direction="bullish",
                open=float(last_bearish["open"]),
                high=float(last_bearish["high"]),
                low=float(last_bearish["low"]),
                close=float(last_bearish["close"]),
                mitigated=bool(window["low"].iloc[-1] < last_bearish["low"]),
            )
            blocks.append(block)
        else:
            bullish = window[window["close"] > window["open"]]
            if bullish.empty:
                continue
            last_bullish = bullish.iloc[-1]
            block = OrderBlock(
                timestamp=last_bullish.name,
                direction="bearish",
                open=float(last_bullish["open"]),
                high=float(last_bullish["high"]),
                low=float(last_bullish["low"]),
                close=float(last_bullish["close"]),
                mitigated=bool(window["high"].iloc[-1] > last_bullish["high"]),
            )
            blocks.append(block)
    return blocks
