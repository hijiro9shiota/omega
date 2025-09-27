"""Combine timeframe analyses into actionable contexts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from ..market_structure.bos_choch import StructureEvent
from ..market_structure.order_blocks import OrderBlock
from ..market_structure.swings_zigzag import SwingPoint
from ..signals.signal_builder import SignalContext


@dataclass
class EnsembleDecision:
    context: SignalContext
    confidence: float


class EnsembleRouter:
    def __init__(self, higher_timeframes: List[str], execution_timeframe: str):
        self.higher_timeframes = higher_timeframes
        self.execution_timeframe = execution_timeframe

    def build_context(
        self,
        symbol: str,
        analyses: Dict[str, object],
        regime: Dict[str, object],
    ) -> EnsembleDecision | None:
        exec_analysis = analyses.get(self.execution_timeframe)
        if exec_analysis is None:
            return None
        bias = self._derive_bias(analyses)
        if bias is None:
            return None
        features = {
            "bias": bias,
            "atr": exec_analysis.indicators["volatility"].atr,
            "order_block": exec_analysis.order_blocks[-1] if exec_analysis.order_blocks else None,
            "liquidity": exec_analysis.liquidity[-3:],
            "bos": any(event.type == "BOS" for event in exec_analysis.structure_events[-3:]),
            "fvg": exec_analysis.fair_value_gaps[-1] if exec_analysis.fair_value_gaps else None,
            "turtle": exec_analysis.turtle_soup[-1] if exec_analysis.turtle_soup else None,
            "divergence": bool(exec_analysis.indicators["momentum"].divergences["bullish"].iloc[-1])
            or bool(exec_analysis.indicators["momentum"].divergences["bearish"].iloc[-1]),
        }
        context = SignalContext(
            symbol=symbol,
            timeframe=self.execution_timeframe,
            candles=exec_analysis.candles,
            features=features,
            regime={
                "label": regime.label,
                "volatility_percentile": regime.volatility_percentile,
            },
        )
        confidence = 0.6 if regime.label == "trending" else 0.5
        if features["bias"] == "long" and regime.label == "trending":
            confidence += 0.1
        return EnsembleDecision(context=context, confidence=confidence)

    def _derive_bias(self, analyses: Dict[str, object]) -> str | None:
        bullish_votes = 0
        bearish_votes = 0
        for tf, analysis in analyses.items():
            if tf == self.execution_timeframe:
                continue
            structures: List[StructureEvent] = analysis.structure_events[-3:]
            if not structures:
                closes = analysis.candles["close"]
                if closes.iloc[-1] > closes.iloc[0]:
                    bullish_votes += 1
                elif closes.iloc[-1] < closes.iloc[0]:
                    bearish_votes += 1
                continue
            for event in structures:
                if event.direction == "bullish":
                    bullish_votes += 1
                elif event.direction == "bearish":
                    bearish_votes += 1
        if bullish_votes == bearish_votes:
            return "long" if analyses[self.execution_timeframe].candles["close"].iloc[-1] >= analyses[self.execution_timeframe].candles["close"].iloc[0] else "short"
        return "long" if bullish_votes > bearish_votes else "short"
