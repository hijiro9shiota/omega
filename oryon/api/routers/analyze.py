"""Analyze endpoint for FastAPI server."""
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from oryon.api.dependencies import AppResources, get_resources
from oryon.api.dto.analyze_request import AnalyzeRequest
from oryon.api.dto.analyze_response import AnalyzeResponse, SignalModel
from oryon.data.storage.sql_store import store_signals

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_endpoint(
    request: AnalyzeRequest,
    resources: AppResources = Depends(get_resources),
) -> AnalyzeResponse:
    timeframes = request.timeframes or resources.pipeline.engine.timeframes
    if not timeframes:
        raise HTTPException(status_code=400, detail="No timeframes configured")
    lookback = request.lookback
    bundle = resources.data_loader.load_bundle(request.symbol, timeframes, limit=lookback)
    signals = resources.pipeline.run(request.symbol, bundle.candles)
    if signals:
        exec_df = bundle.candles[timeframes[-1]]
        ts_entry = exec_df.index[-1]
        store_signals(resources.sql_store, signals, timeframes[-1], ts_entry)
    payload: List[SignalModel] = [SignalModel(**signal.to_dict()) for signal in signals]
    return AnalyzeResponse(signals=payload, generated_at=datetime.utcnow())


__all__ = ["router"]
