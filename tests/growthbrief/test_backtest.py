import pytest
import pandas as pd
import numpy as np
from growthbrief.backtest import run_backtest

# Fixture for synthetic GRS DataFrame
@pytest.fixture
def synthetic_grs_df():
    data = {
        'GRS': [80, 70, 60, 50, 40, 30, 20, 10],
    }
    df = pd.DataFrame(data, index=['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX'])
    return df

    # Fixture for synthetic daily price DataFrame
@pytest.fixture
def synthetic_prices_df():
    dates = pd.date_range(start='2023-01-01', periods=365 * 2, freq='D') # 2 years of data
    tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX']
    data = {
        ticker: np.linspace(100, 200 + i*10, 365 * 2) for i, ticker in enumerate(tickers)
    }
    df = pd.DataFrame(data, index=dates)
    return df

def test_run_backtest_deterministic_results(synthetic_grs_df, synthetic_prices_df):
    # Run multiple times to check for stability (determinism)
    results = []
    for _ in range(3):
        metrics = run_backtest(synthetic_grs_df.copy(), synthetic_prices_df.copy(), top_n=3)
        results.append(metrics)
    
    # All results should be identical
    for i in range(1, len(results)):
        for key in results[0].keys():
            if isinstance(results[0][key], float) and isinstance(results[i][key], float):
                assert np.isclose(results[0][key], results[i][key])
            else:
                assert results[0][key] == results[i][key]

def test_run_backtest_metrics_calculation(synthetic_grs_df, synthetic_prices_df):
    metrics = run_backtest(synthetic_grs_df, synthetic_prices_df, top_n=3)

    assert isinstance(metrics, dict)
    assert 'cagr' in metrics
    assert 'stdev' in metrics
    assert 'max_drawdown' in metrics
    assert 'hit_rate' in metrics
    assert 'sharpe_ratio' in metrics
    assert 'total_return' in metrics

    # Basic check that metrics are not NaN (unless expected for specific scenarios)
    for key, value in metrics.items():
        assert not np.isnan(value)

def test_run_backtest_empty_data():
    empty_grs_df = pd.DataFrame()
    empty_prices_df = pd.DataFrame()
    metrics = run_backtest(empty_grs_df, empty_prices_df)

    # All metrics should be NaN for empty input
    for key, value in metrics.items():
        assert np.isnan(value)