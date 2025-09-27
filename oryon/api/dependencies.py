"""Shared dependencies for API endpoints."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from fastapi import Request

from oryon.backtest.loader import BacktestDataLoader
from oryon.core.pipelines.analyze_asset import AnalyzeAssetPipeline
from oryon.data.ingestion.symbol_universe import SymbolUniverse
from oryon.data.storage.sql_store import SQLStore


@dataclass
class AppResources:
    config: Dict[str, Any]
    pipeline: AnalyzeAssetPipeline
    data_loader: BacktestDataLoader
    sql_store: SQLStore
    universe: SymbolUniverse


def get_resources(request: Request) -> AppResources:
    resources = getattr(request.app.state, "resources", None)
    if resources is None:
        raise RuntimeError("Application resources not configured")
    return resources


__all__ = ["AppResources", "get_resources"]
