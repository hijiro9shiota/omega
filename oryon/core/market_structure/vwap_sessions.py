"""Session-based VWAP calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd

from .liquidity_zones import session_labels


@dataclass
class SessionVWAP:
    session: str
    vwap: pd.Series


def compute_session_vwap(df: pd.DataFrame) -> Dict[str, SessionVWAP]:
    grouped = df.groupby(df.index.map(session_labels))
    out: Dict[str, SessionVWAP] = {}
    for session, session_df in grouped:
        if session_df.empty:
            continue
        volume = session_df["volume"].replace(0, np.nan).fillna(method="ffill").fillna(1)
        typical_price = (session_df["high"] + session_df["low"] + session_df["close"]) / 3
        cumulative_vp = (typical_price * volume).cumsum()
        cumulative_volume = volume.cumsum().replace(0, np.nan)
        vwap = cumulative_vp / cumulative_volume
        out[session] = SessionVWAP(session=session, vwap=vwap)
    return out
