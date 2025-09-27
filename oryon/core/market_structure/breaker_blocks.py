"""Breaker block classification."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd

from .order_blocks import OrderBlock


@dataclass
class BreakerBlock:
    order_block: OrderBlock
    invalidation_ts: pd.Timestamp
    direction: str


def classify_breakers(blocks: List[OrderBlock], df: pd.DataFrame) -> List[BreakerBlock]:
    breakers: List[BreakerBlock] = []
    for block in blocks:
        if block.direction == "bullish":
            post_prices = df[df.index > block.timestamp]["close"]
            invalidated = post_prices.lt(block.low).idxmax() if (post_prices < block.low).any() else None
            if invalidated is not None:
                breakers.append(BreakerBlock(order_block=block, invalidation_ts=invalidated, direction="bearish"))
        else:
            post_prices = df[df.index > block.timestamp]["close"]
            invalidated = post_prices.gt(block.high).idxmax() if (post_prices > block.high).any() else None
            if invalidated is not None:
                breakers.append(BreakerBlock(order_block=block, invalidation_ts=invalidated, direction="bullish"))
    return breakers
