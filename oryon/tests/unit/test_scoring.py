from oryon.core.pipelines.scoring_calibrator import ScoreBreakdown, calibrate_score


def test_calibrate_score_rewards_confluence():
    features = {
        "bos": True,
        "fvg": True,
        "turtle": False,
        "divergence": True,
        "order_block": True,
        "liquidity": [1, 2],
        "rr": 2.8,
        "volatility_percentile": 60,
    }
    breakdown = calibrate_score(features, regime_label="trending")
    assert isinstance(breakdown, ScoreBreakdown)
    assert 0.8 <= breakdown.total <= 1.0


def test_calibrate_score_penalizes_low_rr_and_vol():
    features = {
        "bos": False,
        "fvg": False,
        "turtle": False,
        "divergence": False,
        "order_block": False,
        "liquidity": [],
        "rr": 1.0,
        "volatility_percentile": 99,
    }
    breakdown = calibrate_score(features, regime_label="ranging")
    assert breakdown.total < 0.4
