from datetime import datetime

import pytest

pd = pytest.importorskip("pandas")

from oryon.backtest.metrics import BacktestMetrics, summarize
from oryon.backtest.walk_forward import BacktestTrade
from oryon.core.signals.signal_schema import TradingSignal


def make_signal(direction: str = "long") -> TradingSignal:
    return TradingSignal(
        id="sig",
        symbol="BTCUSDT",
        timeframe="5m",
        direction=direction,
        entry=100.0,
        stop_loss=95.0 if direction == "long" else 105.0,
        take_profits=[110.0, 115.0] if direction == "long" else [90.0, 85.0],
        rr=2.0,
        score=0.7,
    )


def test_summarize_trades():
    trades = [
        BacktestTrade(
            signal=make_signal("long"),
            entry_time=pd.Timestamp(datetime.utcnow()),
            exit_time=pd.Timestamp(datetime.utcnow()),
            outcome="target",
            rr_realized=2.0,
            max_adverse=1.0,
            max_favorable=8.0,
        ),
        BacktestTrade(
            signal=make_signal("short"),
            entry_time=pd.Timestamp(datetime.utcnow()),
            exit_time=pd.Timestamp(datetime.utcnow()),
            outcome="stop",
            rr_realized=-1.0,
            max_adverse=3.0,
            max_favorable=0.5,
        ),
    ]
    metrics = summarize(trades)
    assert isinstance(metrics, BacktestMetrics)
    assert metrics.total_trades == 2
    assert metrics.win_rate == 0.5
    assert metrics.avg_rr != 0.0
    assert metrics.max_favorable >= 8.0
    assert metrics.max_adverse >= 3.0


def test_summarize_empty():
    metrics = summarize([])
    assert metrics == BacktestMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0)
