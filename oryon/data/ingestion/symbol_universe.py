"""Utilities to manage the unified symbol universe."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class SymbolRecord:
    symbol: str
    exchange: str
    asset_type: str
    base: Optional[str] = None
    quote: Optional[str] = None
    aliases: Optional[List[str]] = None
    mic: Optional[str] = None
    updated_at: Optional[str] = None


class SymbolUniverse:
    """Load and persist the global symbol universe in JSONL format."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._records: Dict[str, SymbolRecord] = {}
        if self._path.exists():
            self._load()

    def _load(self) -> None:
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                data = json.loads(line)
                record = SymbolRecord(**data)
                self._records[record.symbol] = record

    def add_or_update(self, record: SymbolRecord) -> None:
        self._records[record.symbol] = record

    def bulk_update(self, records: Iterable[SymbolRecord]) -> None:
        for record in records:
            self.add_or_update(record)

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as fh:
            for record in self._records.values():
                fh.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    def get(self, symbol: str) -> Optional[SymbolRecord]:
        return self._records.get(symbol)

    def search_prefix(self, query: str, limit: int = 20) -> List[SymbolRecord]:
        query_lower = query.lower()
        matches = [r for r in self._records.values() if r.symbol.lower().startswith(query_lower)]
        matches.sort(key=lambda r: r.symbol)
        return matches[:limit]

    def all_records(self) -> List[SymbolRecord]:
        return list(self._records.values())
