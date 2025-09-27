from datetime import datetime, timedelta

import pytest

pd = pytest.importorskip("pandas")

from oryon.backtest.walk_forward import evaluate_signal
from oryon.core.signals.signal_schema import TradingSignal


def make_forward_df(direction: str) -> pd.DataFrame:
    base = datetime(2024, 1, 1)
    rows = []
    price = 100.0
    for i in range(10):
        if direction == "long":
            price += 1.5
        else:
            price -= 1.5
        rows.append(
            {
                "timestamp": base + timedelta(minutes=i + 1),
                "open": price - 0.5,
                "high": price + 0.8,
                "low": price - 0.8,
                "close": price,
                "volume": 1000 + i,
            }
        )
    df = pd.DataFrame(rows).set_index("timestamp")
    return df


def test_evaluate_signal_hits_target():
    signal = TradingSignal(
        id="a",
        symbol="BTCUSDT",
        timeframe="5m",
        direction="long",
        entry=100.0,
        stop_loss=95.0,
        take_profits=[105.0],
        rr=1.0,
        score=0.6,
    )
    forward_df = make_forward_df("long")
    trade = evaluate_signal(signal, forward_df)
    assert trade is not None
    assert trade.outcome == "target"
    assert trade.rr_realized > 0


def test_evaluate_signal_hits_stop():
    signal = TradingSignal(
        id="b",
        symbol="BTCUSDT",
        timeframe="5m",
        direction="short",
        entry=100.0,
        stop_loss=105.0,
        take_profits=[90.0],
        rr=1.0,
        score=0.6,
    )
    df = make_forward_df("long")
    trade = evaluate_signal(signal, df)
    assert trade is not None
    assert trade.outcome == "stop"
    assert trade.rr_realized == -1.0
