"""Microstructure approximations such as tick delta."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class MicrostructureSnapshot:
    delta_volume: pd.Series
    buy_pressure: pd.Series


def compute_microstructure(df: pd.DataFrame) -> MicrostructureSnapshot:
    returns = df["close"].diff().fillna(0)
    volume = df["volume"].fillna(0)
    sign = np.sign(returns)
    delta_volume = volume * sign
    rolling_vol = volume.rolling(10).sum().replace(0, np.nan)
    buy_pressure = (delta_volume.rolling(10).sum()) / rolling_vol
    return MicrostructureSnapshot(delta_volume=delta_volume, buy_pressure=buy_pressure.fillna(0))
