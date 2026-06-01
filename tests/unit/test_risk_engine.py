import numpy as np
import pandas as pd
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../app"))

from ml.risk_engine import RiskEngine


@pytest.fixture
def sample_prices():
    rng = np.random.default_rng(42)
    dates = pd.date_range("2023-01-01", periods=252, freq="D")
    return pd.DataFrame(
        {
            "AAPL": 100 * (1 + rng.normal(0.001, 0.02, 252)).cumprod(),
            "GOOGL": 90 * (1 + rng.normal(0.0008, 0.018, 252)).cumprod(),
        },
        index=dates,
    )


def test_sharpe_ratio_is_float(sample_prices):
    engine = RiskEngine()
    metrics = engine.compute(sample_prices, {"AAPL": 10000, "GOOGL": 5000})
    assert isinstance(metrics.sharpe_ratio, float)
    assert -10 < metrics.sharpe_ratio < 10


def test_var_ordering(sample_prices):
    engine = RiskEngine()
    metrics = engine.compute(sample_prices, {"AAPL": 10000, "GOOGL": 5000})
    assert metrics.var_99 <= metrics.var_95
    assert metrics.var_95 < 0


def test_max_drawdown_non_positive(sample_prices):
    engine = RiskEngine()
    metrics = engine.compute(sample_prices, {"AAPL": 10000, "GOOGL": 5000})
    assert metrics.max_drawdown <= 0


def test_annualized_vol_greater_than_daily(sample_prices):
    engine = RiskEngine()
    metrics = engine.compute(sample_prices, {"AAPL": 10000, "GOOGL": 5000})
    assert metrics.annualized_volatility > metrics.daily_volatility


def test_portfolio_value_matches_weights(sample_prices):
    engine = RiskEngine()
    weights = {"AAPL": 10000, "GOOGL": 5000}
    metrics = engine.compute(sample_prices, weights)
    assert metrics.portfolio_value == pytest.approx(15000.0)


def test_unknown_symbol_excluded(sample_prices):
    engine = RiskEngine()
    metrics = engine.compute(sample_prices, {"AAPL": 10000, "UNKNOWN": 5000})
    assert metrics.portfolio_value == pytest.approx(10000.0)
