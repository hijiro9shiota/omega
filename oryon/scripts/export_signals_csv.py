"""Export generated signals from the SQL store into a CSV file."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from oryon.data.storage.sql_store import SQLStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Oryon signals to CSV")
    parser.add_argument("--sqlite", type=Path, default=Path("data_store/oryon.sqlite"))
    parser.add_argument("--output", type=Path, default=Path("signals_export.csv"))
    args = parser.parse_args()

    sql_store = SQLStore(args.sqlite)
    with sql_store.cursor() as cur:
        cur.execute("SELECT * FROM signals ORDER BY created_at DESC")
        rows = cur.fetchall()
    if not rows:
        print("No signals to export")
        return
    headers = rows[0].keys()
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))
    print(f"Exported {len(rows)} signals to {args.output}")


if __name__ == "__main__":
    main()
