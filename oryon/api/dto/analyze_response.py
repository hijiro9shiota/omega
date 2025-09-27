"""Response models for analyze endpoint."""
from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class SignalReasonModel(BaseModel):
    label: str
    detail: str | None = None


class OverlayPrimitiveModel(BaseModel):
    kind: str
    payload: dict


class SignalModel(BaseModel):
    id: str
    symbol: str
    timeframe: str
    direction: str
    entry: float
    stop_loss: float
    take_profits: List[float]
    rr: float
    score: float
    reasons: List[SignalReasonModel]
    overlays: List[OverlayPrimitiveModel]
    created_at: datetime


class AnalyzeResponse(BaseModel):
    signals: List[SignalModel]
    generated_at: datetime


__all__ = [
    "AnalyzeResponse",
    "SignalModel",
    "OverlayPrimitiveModel",
    "SignalReasonModel",
]
