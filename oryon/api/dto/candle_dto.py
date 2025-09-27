"""DTO for candle history responses."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CandleDTO(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


__all__ = ["CandleDTO"]
