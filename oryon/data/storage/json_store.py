"""Append-only JSON storage for raw candles."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, List

from ..connectors.base import Candle


class JsonStore:
    """Persist candles as JSON Lines with periodic snapshots."""

    def __init__(self, root_dir: Path, snapshot_interval: int = 1000, snapshot_retention: int = 5) -> None:
        self._root = Path(root_dir)
        self._snapshot_interval = snapshot_interval
        self._snapshot_retention = snapshot_retention
        self._root.mkdir(parents=True, exist_ok=True)

    def _file_path(self, symbol: str, timeframe: str) -> Path:
        safe_symbol = symbol.replace("/", "_")
        return self._root / symbol.upper() / f"{safe_symbol}_{timeframe}.jsonl"

    def append(self, symbol: str, timeframe: str, candles: Iterable[Candle]) -> None:
        path = self._file_path(symbol, timeframe)
        path.parent.mkdir(parents=True, exist_ok=True)
        existing_count = self._count_lines(path)
        with path.open("a", encoding="utf-8") as fh:
            for candle in candles:
                fh.write(json.dumps(self.candle_to_dict(candle), default=str) + "\n")
                existing_count += 1
                if existing_count % self._snapshot_interval == 0:
                    self._write_snapshot(symbol, timeframe)
        if existing_count % self._snapshot_interval != 0:
            self._trim_snapshots(symbol, timeframe)

    def read(self, symbol: str, timeframe: str) -> Iterator[Candle]:
        path = self._file_path(symbol, timeframe)
        if not path.exists():
            return iter([])
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                yield self.candle_from_dict(json.loads(line))

    def _write_snapshot(self, symbol: str, timeframe: str) -> None:
        snapshot_path = self._snapshot_path(symbol, timeframe, datetime.now(tz=timezone.utc))
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        candles = list(self.read(symbol, timeframe))
        with snapshot_path.open("w", encoding="utf-8") as fh:
            json.dump([self.candle_to_dict(c) for c in candles], fh)
        self._trim_snapshots(symbol, timeframe)

    def _trim_snapshots(self, symbol: str, timeframe: str) -> None:
        snap_dir = self._snapshot_dir(symbol, timeframe)
        if not snap_dir.exists():
            return
        snapshots = sorted(snap_dir.glob("*.json"))
        for path in snapshots[:-self._snapshot_retention]:
            path.unlink(missing_ok=True)

    def _snapshot_dir(self, symbol: str, timeframe: str) -> Path:
        return self._root / symbol.upper() / "snapshots" / timeframe

    def _snapshot_path(self, symbol: str, timeframe: str, ts: datetime) -> Path:
        safe_symbol = symbol.replace("/", "_")
        return self._snapshot_dir(symbol, timeframe) / f"{safe_symbol}_{timeframe}_{ts.strftime('%Y%m%d%H%M%S')}.json"

    @staticmethod
    def _count_lines(path: Path) -> int:
        if not path.exists():
            return 0
        with path.open("r", encoding="utf-8") as fh:
            return sum(1 for _ in fh)

    @staticmethod
    def candle_to_dict(candle: Candle) -> dict:
        payload = asdict(candle)
        payload["timestamp"] = candle.timestamp.isoformat()
        return payload

    @staticmethod
    def candle_from_dict(payload: dict) -> Candle:
        return Candle(
            symbol=payload["symbol"],
            timeframe=payload["timeframe"],
            timestamp=datetime.fromisoformat(payload["timestamp"]),
            open=float(payload["open"]),
            high=float(payload["high"]),
            low=float(payload["low"]),
            close=float(payload["close"]),
            volume=float(payload.get("volume", 0.0)),
            source=payload.get("source", "unknown"),
        )
