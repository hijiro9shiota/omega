"""Request model for the analyze endpoint."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, validator


class AnalyzeRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    timeframes: Optional[List[str]] = Field(default=None)
    lookback: int = Field(default=600, ge=100, le=5000)
    layers: Optional[List[str]] = Field(default=None, description="Optional overlay layers requested by the UI")

    @validator("timeframes", always=True)
    def _validate_timeframes(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return value
        if not value:
            raise ValueError("timeframes cannot be empty")
        return value

    @validator("layers", always=True)
    def _validate_layers(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return value
        return [layer for layer in value if layer]


__all__ = ["AnalyzeRequest"]
