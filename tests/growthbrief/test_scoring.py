import pytest
import pandas as pd
import numpy as np
from growthbrief.scoring import score_grs, pct_rank, winsorize_series

# Fixture for a synthetic DataFrame with various feature values
@pytest.fixture
def synthetic_features_df():
    data = {
        'ticker': ['TKR1', 'TKR2', 'TKR3', 'TKR4', 'TKR5'],
        # FM features (higher is better)
        'rev_yoy': [0.1, 0.2, 0.3, 0.4, 0.5],
        'gm_delta': [0.01, 0.02, 0.03, 0.04, 0.05],
        'om_delta': [0.01, 0.02, 0.03, 0.04, 0.05],
        'fcf_delta': [0.01, 0.02, 0.03, 0.04, 0.05],
        # Q features (higher is better, except accruals_proxy)
        'roa_proxy': [0.05, 0.06, 0.07, 0.08, 0.09],
        'cash_conversion': [0.8, 0.9, 1.0, 1.1, 1.2],
        'accruals_proxy': [0.05, 0.04, 0.03, 0.02, 0.01], # Lower is better
        # VG features (lower is better)
        'pe': [30, 25, 20, 15, 10],
        'ev_sales': [5, 4, 3, 2, 1],
        'ev_sales_zscore': [2.0, 1.0, 0.0, -1.0, -2.0],
        'peg_proxy': [3.0, 2.5, 2.0, 1.5, 1.0],
        # IT features (higher is better)
        'sector_rs_6m': [0.01, 0.02, 0.03, 0.04, 0.05],
        'sector_rs_12m': [0.02, 0.03, 0.04, 0.05, 0.06],
        'sector_above_50dma': [0, 0, 1, 1, 1], # Binary
        'sector_above_200dma': [0, 0, 0, 1, 1], # Binary
        # TC features (higher is better, max_drawdown_1y closer to 0 is better)
        'above_50dma': [0, 0, 1, 1, 1],
        'above_100dma': [0, 0, 0, 1, 1],
        'above_200dma': [0, 0, 0, 0, 1],
        '6m_momentum': [0.05, 0.10, 0.15, 0.20, 0.25],
        'max_drawdown_1y': [-0.20, -0.15, -0.10, -0.05, -0.01], # Closer to 0 is better
    }
    df = pd.DataFrame(data).set_index('ticker')
    return df

def test_pct_rank():
    series = pd.Series([10, 20, 10, 30, np.nan])
    ranked = pct_rank(series)
    # Expected ranks for [10, 20, 10, 30] are [1.5, 3, 1.5, 4]
    # Percentile ranks: [1.5/4*100, 3/4*100, 1.5/4*100, 4/4*100] = [37.5, 75.0, 37.5, 100.0]
    expected = pd.Series([37.5, 75.0, 37.5, 100.0, np.nan], index=[0,1,2,3,4])
    pd.testing.assert_series_equal(ranked, expected, check_dtype=False)

def test_winsorize_series():
    series = pd.Series(np.arange(1, 101))
    winsorized = winsorize_series(series, lower_bound=5, upper_bound=95)
    assert np.isclose(winsorized.min(), 5.95)
    assert np.isclose(winsorized.max(), 95.05)
    assert winsorized.iloc[0] == 5
    assert winsorized.iloc[-1] == 95
    assert winsorized.iloc[50] == 51

    series_with_nan = pd.Series([1, 2, 100, np.nan, 500])
    winsorized_nan = winsorize_series(series_with_nan, lower_bound=25, upper_bound=75)
    # For [1, 2, 100, 500], 25th percentile is 1.75, 75th percentile is 300
    # Expected: [1.75, 2, 100, NaN, 300]
    expected_nan = pd.Series([1.75, 2.0, 100.0, np.nan, 300.0], index=[0,1,2,3,4])
    pd.testing.assert_series_equal(winsorized_nan, expected_nan, check_dtype=False)

def test_score_grs_monotonicity(synthetic_features_df):
    # The synthetic_features_df is constructed such that TKR1 should have the lowest GRS
    # and TKR5 should have the highest GRS, assuming all features contribute positively
    # after handling direction (e.g., lower PE gets higher score).

    result_df = score_grs(synthetic_features_df.copy())

    assert 'GRS' in result_df.columns
    assert result_df['GRS'].is_monotonic_increasing # Check if GRS increases from TKR1 to TKR5

    # Check GRS range (0-100)
    assert result_df['GRS'].min() >= 0
    assert result_df['GRS'].max() <= 100

    # Check for 1 decimal place
    assert all(result_df['GRS'].apply(lambda x: len(str(x).split('.')[-1]) <= 1 if '.' in str(x) else True))

def test_score_grs_stable_results(synthetic_features_df):
    # Run multiple times to check for stability (determinism)
    results = []
    for _ in range(3):
        results.append(score_grs(synthetic_features_df.copy())['GRS'])
    
    # All results should be identical
    for i in range(1, len(results)):
        pd.testing.assert_series_equal(results[0], results[i])

def test_score_grs_with_nan_features():
    data = {
        'ticker': ['TKR1', 'TKR2'],
        'rev_yoy': [0.1, np.nan],
        'gm_delta': [0.01, 0.02],
        'roa_proxy': [0.05, np.nan],
        'pe': [30, 10],
        'sector_rs_6m': [0.01, 0.02],
        'above_50dma': [1, np.nan],
    }
    df = pd.DataFrame(data).set_index('ticker')
    result_df = score_grs(df)

    assert 'GRS' in result_df.columns
    # GRS for TKR2 should be lower or NaN due to missing features
    assert result_df.loc['TKR1', 'GRS'] > 0 # Should be calculable
    # Depending on how NaNs are handled in scoring, TKR2 might be NaN or a lower score
    # For now, just check it's not raising an error and produces a result
    assert not result_df.loc['TKR2', 'GRS'] == result_df.loc['TKR1', 'GRS']
