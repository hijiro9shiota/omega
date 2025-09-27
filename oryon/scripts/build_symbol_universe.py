"""Build or refresh the unified symbol universe file."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from oryon.core.utils.logging_setup import configure_logging
from oryon.data.ingestion.symbol_universe import SymbolRecord, SymbolUniverse


def load_static_symbols(path: Path) -> Iterable[SymbolRecord]:
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            yield SymbolRecord(
                symbol=row["symbol"],
                exchange=row.get("exchange", ""),
                asset_type=row.get("asset_type", ""),
                base=row.get("base"),
                quote=row.get("quote"),
                aliases=[alias for alias in row.get("aliases", "").split("|") if alias],
                mic=row.get("mic"),
                updated_at=datetime.utcnow().isoformat(),
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Oryon symbol universe")
    parser.add_argument("output", type=Path, help="Path to symbols.jsonl")
    parser.add_argument("--static-csv", type=Path, help="Optional CSV file with symbols")
    args = parser.parse_args()

    configure_logging()
    universe = SymbolUniverse(args.output)
    records: List[SymbolRecord] = []
    if args.static_csv:
        records.extend(load_static_symbols(args.static_csv))
    universe.bulk_update(records)
    universe.save()
    print(f"Saved {len(universe.all_records())} symbols to {args.output}")


if __name__ == "__main__":
    main()
