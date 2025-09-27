"""DTO for symbol responses."""
from __future__ import annotations

from pydantic import BaseModel


class SymbolDTO(BaseModel):
    symbol: str
    exchange: str
    asset_type: str
    base: str | None = None
    quote: str | None = None


__all__ = ["SymbolDTO"]
