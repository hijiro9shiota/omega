"""Convert feature confluences into normalized scores."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ScoreBreakdown:
    base: float
    confluence_bonus: float
    penalty: float

    @property
    def total(self) -> float:
        return max(0.0, min(1.0, self.base + self.confluence_bonus - self.penalty))


def calibrate_score(features: Dict[str, object], regime_label: str) -> ScoreBreakdown:
    base = 0.4 if regime_label == "ranging" else 0.5
    confluence = 0.0
    penalty = 0.0
    if features.get("bos"):
        confluence += 0.15
    if features.get("fvg"):
        confluence += 0.1
    if features.get("turtle"):
        confluence += 0.1
    if features.get("divergence"):
        confluence += 0.1
    if features.get("order_block"):
        confluence += 0.15
    liquidity_zones = features.get("liquidity", [])
    if isinstance(liquidity_zones, list) and len(liquidity_zones) >= 2:
        confluence += 0.05
    rr = features.get("rr", 0)
    if rr < 1.5:
        penalty += 0.2
    elif rr > 2.5:
        confluence += 0.05
    volatility_pct = features.get("volatility_percentile", 50)
    if volatility_pct > 95:
        penalty += 0.2
    return ScoreBreakdown(base=base, confluence_bonus=confluence, penalty=penalty)
