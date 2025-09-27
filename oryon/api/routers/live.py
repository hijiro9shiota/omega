"""Live price endpoint (polling based)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from oryon.api.dependencies import AppResources, get_resources

router = APIRouter(prefix="/live", tags=["live"])


@router.get("")
async def live_endpoint(
    symbol: str = Query(..., min_length=1, max_length=20),
    timeframe: str = Query("1m", min_length=1, max_length=10),
    resources: AppResources = Depends(get_resources),
) -> dict:
    candles = resources.sql_store.fetch_candles(symbol, timeframe, limit=1)
    if not candles:
        raise HTTPException(status_code=404, detail="No recent candle available")
    candle = candles[-1]
    return {
        "symbol": candle.symbol,
        "timeframe": candle.timeframe,
        "timestamp": candle.timestamp.isoformat(),
        "price": candle.close,
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "volume": candle.volume,
        "received_at": datetime.utcnow().isoformat(),
    }


__all__ = ["router"]
