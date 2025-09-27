"""Historical candles endpoint."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from oryon.api.dependencies import AppResources, get_resources
from oryon.api.dto.candle_dto import CandleDTO

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=List[CandleDTO])
async def history_endpoint(
    symbol: str = Query(..., min_length=1, max_length=20),
    timeframe: str = Query(..., min_length=1, max_length=10),
    limit: int = Query(500, ge=10, le=5000),
    resources: AppResources = Depends(get_resources),
) -> List[CandleDTO]:
    candles = resources.sql_store.fetch_candles(symbol, timeframe, limit=limit)
    if not candles:
        raise HTTPException(status_code=404, detail="No candles available")
    dto = [
        CandleDTO(
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=candle.volume,
        )
        for candle in candles
    ]
    return dto


__all__ = ["router"]
