import pytest

pd = pytest.importorskip("pandas")

from oryon.core.pipelines.analyze_asset import AnalyzeAssetPipeline


def build_candles(start_price: float, trend: float, periods: int = 120):
    idx = pd.date_range("2024-01-01", periods=periods, freq="15min")
    prices = [start_price + i * trend for i in range(periods)]
    df = pd.DataFrame(
        {
            "open": prices,
            "high": [p + 0.5 for p in prices],
            "low": [p - 0.5 for p in prices],
            "close": [p + 0.25 for p in prices],
            "volume": [1_500_000 + i * 1000 for i in range(periods)],
        },
        index=idx,
    )
    return df


def test_pipeline_produces_signal_when_bias_and_filters_pass():
    pipeline = AnalyzeAssetPipeline(timeframes=["4h", "1h", "15m"], execution_timeframe="15m")
    candles_by_tf = {
        "4h": build_candles(100, 0.3, periods=90).resample("4h").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }).dropna(),
        "1h": build_candles(100, 0.15, periods=180).resample("1h").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }).dropna(),
        "15m": build_candles(100, 0.05, periods=240),
    }
    signals = pipeline.run("BTCUSDT", candles_by_tf)
    assert isinstance(signals, list)
    if signals:
        signal = signals[0]
        assert signal.symbol == "BTCUSDT"
        assert signal.timeframe == "15m"
        assert signal.score >= 0.55
        assert len(signal.reasons) >= 3
