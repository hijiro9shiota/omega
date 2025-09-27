"""Multi-timeframe analysis orchestrator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from ..indicators.moving_averages import compute_moving_averages
from ..indicators.momentum import compute_momentum_suite
from ..indicators.pattern_candles import compute_candle_patterns
from ..indicators.volatility import compute_volatility_suite
from ..market_structure.bos_choch import StructureEvent, detect_bos_choch
from ..market_structure.fvg_imbalance import FairValueGap, find_fvg
from ..market_structure.liquidity_zones import LiquidityZone, daily_levels, detect_equal_highs_lows, merge_zones, session_high_low
from ..market_structure.microstructure import MicrostructureSnapshot, compute_microstructure
from ..market_structure.order_blocks import OrderBlock, find_order_blocks
from ..market_structure.regime_detection import RegimeState, detect_regime
from ..market_structure.swings_zigzag import SwingPoint, compute_swings
from ..market_structure.turtle_soup import TurtleSoupSignal, detect_turtle_soup
from ..market_structure.vwap_sessions import SessionVWAP, compute_session_vwap


@dataclass
class TimeframeAnalysis:
    candles: pd.DataFrame
    swings: List[SwingPoint]
    structure_events: List[StructureEvent]
    liquidity: List[LiquidityZone]
    fair_value_gaps: List[FairValueGap]
    order_blocks: List[OrderBlock]
    turtle_soup: List[TurtleSoupSignal]
    indicators: Dict[str, object]
    session_vwap: Dict[str, SessionVWAP]
    microstructure: MicrostructureSnapshot


@dataclass
class MultiTimeframeContext:
    per_timeframe: Dict[str, TimeframeAnalysis]
    top_regime: RegimeState


class MultiTimeframeEngine:
    def __init__(self, timeframes: List[str]):
        self.timeframes = timeframes

    def analyze(self, symbol: str, candles_by_tf: Dict[str, pd.DataFrame]) -> MultiTimeframeContext:
        analyses: Dict[str, TimeframeAnalysis] = {}
        higher_tf = self.timeframes[0]
        higher_df = candles_by_tf[higher_tf]
        regime = detect_regime(higher_df)
        for tf in self.timeframes:
            df = candles_by_tf[tf].copy()
            df.index = pd.to_datetime(df.index)
            swings = compute_swings(df)
            structure = detect_bos_choch(swings)
            liquidity = merge_zones(
                detect_equal_highs_lows(df),
                daily_levels(df),
                session_high_low(df),
            )
            fvgs = find_fvg(df)
            order_blocks = find_order_blocks(df, structure)
            turtle = detect_turtle_soup(df)
            ma_suite = compute_moving_averages(df["close"], (20, 50, 100))
            momentum = compute_momentum_suite(df)
            patterns = compute_candle_patterns(df)
            vol = compute_volatility_suite(df)
            indicators = {
                "moving_averages": ma_suite,
                "momentum": momentum,
                "patterns": patterns,
                "volatility": vol,
            }
            session_vwap = compute_session_vwap(df)
            micro = compute_microstructure(df)
            analyses[tf] = TimeframeAnalysis(
                candles=df,
                swings=swings,
                structure_events=structure,
                liquidity=liquidity,
                fair_value_gaps=fvgs,
                order_blocks=order_blocks,
                turtle_soup=turtle,
                indicators=indicators,
                session_vwap=session_vwap,
                microstructure=micro,
            )
        return MultiTimeframeContext(per_timeframe=analyses, top_regime=regime)
