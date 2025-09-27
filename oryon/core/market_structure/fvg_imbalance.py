"""Fair value gap and imbalance detection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class FairValueGap:
    start: pd.Timestamp
    end: pd.Timestamp
    direction: str
    filled: bool


def find_fvg(df: pd.DataFrame, min_size: float = 0.0005) -> List[FairValueGap]:
    gaps: List[FairValueGap] = []
    for idx in range(2, len(df)):
        current = df.iloc[idx]
        prev = df.iloc[idx - 1]
        older = df.iloc[idx - 2]
        bullish_gap = older.high < current.low and (current.low - older.high) >= min_size * current.low
        bearish_gap = older.low > current.high and (older.low - current.high) >= min_size * current.high
        if bullish_gap:
            filled = df.iloc[idx - 1 : idx + 1]["low"].min() <= older.high
            gaps.append(FairValueGap(start=df.index[idx - 2], end=df.index[idx], direction="bullish", filled=bool(filled)))
        if bearish_gap:
            filled = df.iloc[idx - 1 : idx + 1]["high"].max() >= older.low
            gaps.append(FairValueGap(start=df.index[idx - 2], end=df.index[idx], direction="bearish", filled=bool(filled)))
    return gaps
