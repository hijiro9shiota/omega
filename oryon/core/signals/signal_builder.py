"""Assemble trading signals from the analysis context."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from ..risk.rr_engine import RiskResult, build_trade_levels
from ..risk import filters
from .signal_schema import OverlayPrimitive, SignalReason, TradingSignal


@dataclass
class SignalContext:
    symbol: str
    timeframe: str
    candles: pd.DataFrame
    features: Dict[str, object]
    regime: Dict[str, object]


class SignalBuilder:
    def __init__(self, min_score: float = 0.5, min_rr: float = 1.5, min_volume: float = 1_000_000):
        self.min_score = min_score
        self.min_rr = min_rr
        self.min_volume = min_volume

    def _hash(self, symbol: str, timeframe: str, timestamp: pd.Timestamp, direction: str) -> str:
        payload = f"{symbol}-{timeframe}-{timestamp.isoformat()}-{direction}".encode()
        return hashlib.sha1(payload).hexdigest()

    def build(self, context: SignalContext) -> List[TradingSignal]:
        reasons: List[SignalReason] = []
        overlays: List[OverlayPrimitive] = []
        direction = context.features.get("bias")
        if direction not in {"long", "short"}:
            return []
        atr = context.features.get("atr")
        if "risk_result" in context.features and isinstance(context.features["risk_result"], RiskResult):
            rr = context.features["risk_result"]
        else:
            rr = build_trade_levels(direction, context.candles, atr)
        if rr.rr < self.min_rr:
            return []
        regime_state = context.regime
        filter_results = {
            "volatility": filters.volatility_filter(regime_state["volatility_percentile"], threshold=95),
            "liquidity": filters.liquidity_filter(context.candles, self.min_volume),
        }
        if not filters.combine_filters(filter_results):
            return []
        reasons.extend(
            [
                SignalReason(label="Bias", detail=f"{direction} via multi-timeframe confluence"),
                SignalReason(label="Regime", detail=f"{regime_state['label']} regime"),
                SignalReason(label="RR", detail=f"{rr.rr:.2f} expected"),
            ]
        )
        order_block = context.features.get("order_block")
        if order_block:
            overlays.append(
                OverlayPrimitive(
                    kind="order_block",
                    payload={
                        "timestamp": order_block.timestamp.isoformat(),
                        "direction": order_block.direction,
                        "high": order_block.high,
                        "low": order_block.low,
                    },
                )
            )
            reasons.append(SignalReason(label="OrderBlock", detail=f"{order_block.direction.title()} OB respected"))
        liquidity = context.features.get("liquidity")
        if liquidity:
            overlays.extend(
                [
                    OverlayPrimitive(
                        kind="liquidity",
                        payload={"kind": zone.kind, "level": zone.level, "start": zone.start.isoformat()},
                    )
                    for zone in liquidity
                ]
            )
            reasons.append(SignalReason(label="Liquidity", detail=f"{len(liquidity)} zones"))
        score = context.features.get("score", 0.0)
        if score < self.min_score:
            return []
        signal = TradingSignal(
            id=self._hash(context.symbol, context.timeframe, context.candles.index[-1], direction),
            symbol=context.symbol,
            timeframe=context.timeframe,
            direction="long" if direction == "long" else "short",
            entry=rr.entry,
            stop_loss=rr.stop_loss,
            take_profits=list(rr.targets),
            rr=rr.rr,
            score=score,
            reasons=reasons,
            overlays=overlays,
        )
        return [signal]
