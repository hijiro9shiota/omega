"""High level entry point combining the pipeline components."""
from __future__ import annotations

from typing import Dict, List

import pandas as pd

from ..risk.rr_engine import build_trade_levels
from ..signals.post_filtering import deduplicate, enforce_quality
from ..signals.signal_builder import SignalBuilder
from ..signals.signal_schema import TradingSignal
from .ensemble_router import EnsembleRouter
from .multi_timeframe_engine import MultiTimeframeEngine
from .scoring_calibrator import ScoreBreakdown, calibrate_score


class AnalyzeAssetPipeline:
    def __init__(
        self,
        timeframes: List[str],
        execution_timeframe: str,
        min_score: float = 0.55,
        min_rr: float = 1.6,
    ) -> None:
        if execution_timeframe not in timeframes:
            raise ValueError("execution timeframe must be part of timeframes")
        self.engine = MultiTimeframeEngine(timeframes=timeframes)
        self.router = EnsembleRouter(higher_timeframes=[tf for tf in timeframes if tf != execution_timeframe], execution_timeframe=execution_timeframe)
        self.builder = SignalBuilder(min_score=min_score, min_rr=min_rr)
        self.min_score = min_score

    def run(self, symbol: str, candles_by_tf: Dict[str, pd.DataFrame]) -> List[TradingSignal]:
        context = self.engine.analyze(symbol, candles_by_tf)
        decision = self.router.build_context(symbol, context.per_timeframe, context.top_regime.__dict__)
        if decision is None:
            return []
        features = decision.context.features
        atr_series = features.get("atr")
        risk_result = build_trade_levels(features["bias"], decision.context.candles, atr_series)
        features["risk_result"] = risk_result
        volatility_pct = context.top_regime.volatility_percentile
        score_breakdown: ScoreBreakdown = calibrate_score(
            {
                "bos": features.get("bos"),
                "fvg": features.get("fvg"),
                "turtle": features.get("turtle"),
                "divergence": features.get("divergence"),
                "order_block": features.get("order_block"),
                "liquidity": features.get("liquidity"),
                "rr": risk_result.rr,
                "volatility_percentile": volatility_pct,
            },
            context.top_regime.label,
        )
        features["score"] = score_breakdown.total
        signals = self.builder.build(decision.context)
        signals = enforce_quality(deduplicate(signals, window=5), self.min_score)
        return signals
