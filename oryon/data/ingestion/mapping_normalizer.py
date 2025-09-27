"""Helpers to normalize symbols across different data sources."""
from __future__ import annotations

from typing import Dict


class MappingNormalizer:
    """Maintain alias mapping between various vendor symbol syntaxes."""

    def __init__(self, mapping: Dict[str, str] | None = None) -> None:
        self._mapping = {k.upper(): v for k, v in (mapping or {}).items()}

    def normalize(self, symbol: str) -> str:
        key = symbol.upper()
        return self._mapping.get(key, key)

    def register(self, alias: str, canonical: str) -> None:
        self._mapping[alias.upper()] = canonical.upper()

    def merge(self, other: "MappingNormalizer") -> None:
        self._mapping.update(other._mapping)
