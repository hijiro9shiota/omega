"""Signal dataclasses used across the analysis pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class SignalReason:
    label: str
    detail: str | None = None


@dataclass
class OverlayPrimitive:
    kind: str
    payload: Dict[str, Any]


@dataclass
class TradingSignal:
    id: str
    symbol: str
    timeframe: str
    direction: str
    entry: float
    stop_loss: float
    take_profits: List[float]
    rr: float
    score: float
    reasons: List[SignalReason] = field(default_factory=list)
    overlays: List[OverlayPrimitive] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "direction": self.direction,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profits": self.take_profits,
            "rr": self.rr,
            "score": self.score,
            "reasons": [reason.__dict__ for reason in self.reasons],
            "overlays": [overlay.__dict__ for overlay in self.overlays],
            "created_at": self.created_at.isoformat(),
        }
