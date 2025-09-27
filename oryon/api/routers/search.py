"""Symbol search endpoint."""
from __future__ import annotations

import difflib
from typing import List

from fastapi import APIRouter, Depends, Query

from oryon.api.dependencies import AppResources, get_resources
from oryon.api.dto.symbol_dto import SymbolDTO
from oryon.data.ingestion.symbol_universe import SymbolRecord

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=List[SymbolDTO])
async def search_symbols(
    q: str = Query(..., min_length=1, max_length=20),
    limit: int = Query(10, ge=1, le=50),
    resources: AppResources = Depends(get_resources),
) -> List[SymbolDTO]:
    results = resources.sql_store.search_symbols(q, limit)
    if not results:
        universe_matches = fuzzy_universe_search(resources.universe, q, limit)
        results = [record_to_dict(record) for record in universe_matches]
    return [SymbolDTO(**result) for result in results]


def fuzzy_universe_search(universe, query: str, limit: int) -> List[SymbolRecord]:
    records = universe.all_records()
    symbols = [record.symbol for record in records]
    matches = difflib.get_close_matches(query.upper(), symbols, n=limit, cutoff=0.3)
    ranked = [universe.get(symbol) for symbol in matches]
    return [r for r in ranked if r is not None]


def record_to_dict(record: SymbolRecord) -> dict:
    return {
        "symbol": record.symbol,
        "exchange": record.exchange,
        "asset_type": record.asset_type,
        "base": record.base,
        "quote": record.quote,
    }


__all__ = ["router"]
