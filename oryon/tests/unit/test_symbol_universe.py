from pathlib import Path

from oryon.data.ingestion.symbol_universe import SymbolRecord, SymbolUniverse


def test_symbol_universe_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "symbols.jsonl"
    universe = SymbolUniverse(path)
    record = SymbolRecord(symbol="BTCUSDT", exchange="BINANCE", asset_type="crypto")
    universe.add_or_update(record)
    universe.save()

    universe_loaded = SymbolUniverse(path)
    assert universe_loaded.get("BTCUSDT") is not None
    matches = universe_loaded.search_prefix("BTC")
    assert matches[0].symbol == "BTCUSDT"
