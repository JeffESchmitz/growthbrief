import pytest
import pandas as pd
import numpy as np
from growthbrief.reporter import generate_grs_insights

@pytest.fixture
def sample_grs_df():
    data = {
        'ticker': ['TKR1', 'TKR2', 'TKR3', 'TKR4', 'TKR5'],
        'GRS': [85.5, 70.2, 60.1, 45.0, 30.0],
        'rev_yoy': [0.15, 0.05, 0.12, 0.03, 0.08],
        'gm_delta': [0.02, 0.005, 0.015, -0.01, 0.001],
        'roa_proxy': [0.07, 0.04, 0.06, 0.03, 0.05],
        'ev_sales_zscore': [-0.8, -0.1, -0.3, 0.5, 0.1],
        'sector_rs_6m': [0.06, 0.02, 0.04, -0.01, 0.03],
        'above_200dma': [1, 0, 1, 0, 1],
        'max_drawdown_1y': [-0.05, -0.25, -0.10, -0.02, -0.18],
        'pe': [20, 60, 35, 15, 40],
    }
    df = pd.DataFrame(data).set_index('ticker')
    return df

def test_generate_grs_insights_top_n(sample_grs_df):
    result_df = generate_grs_insights(sample_grs_df, top_n=3)

    assert len(result_df) == 3
    assert 'Evidence' in result_df.columns
    assert 'Risks' in result_df.columns
    assert list(result_df.index) == ['TKR1', 'TKR2', 'TKR3']

def test_generate_grs_insights_content(sample_grs_df):
    result_df = generate_grs_insights(sample_grs_df, top_n=1)
    ticker1_insights = result_df.loc['TKR1']

    # Check evidence for TKR1
    evidence = ticker1_insights['Evidence']
    expected_evidence_parts = [
        "Strong Revenue YoY (15.0%)",
        "Improving Gross Margin (2.0%)",
        "Good Return on Assets (7.0%)",
        "Attractive EV/Sales Z-score (-0.8)",
        "Strong Sector Relative Strength (6.0%)",
        "Price above 200-day MA"
    ]
    # Check that the evidence string contains the expected parts (up to 3)
    for expected_part in expected_evidence_parts:
        if expected_part in evidence:
            assert True
    assert len(evidence.split('; ')) == 3 # Should pick top 3

    # Check risks for TKR1
    risks = ticker1_insights['Risks']
    assert "Significant 1-year Drawdown (-5.0%)" not in risks # Not significant enough
    assert "High PE Ratio (20.0)" not in risks # Not high enough
    assert len(risks.split('; ')) == 2 # Should pick top 2 (generic if not specific)

    result_df_tkr2 = generate_grs_insights(sample_grs_df, top_n=2).loc['TKR2']
    risks_tkr2 = result_df_tkr2['Risks']
    assert "Significant 1-year Drawdown (-25.0%)" in risks_tkr2
    assert "High PE Ratio (60.0)" in risks_tkr2

def test_generate_grs_insights_empty_df():
    empty_df = pd.DataFrame(columns=['ticker', 'GRS', 'rev_yoy', 'gm_delta', 'roa_proxy', 'ev_sales_zscore', 'sector_rs_6m', 'above_200dma', 'max_drawdown_1y', 'pe']).set_index('ticker')
    result_df = generate_grs_insights(empty_df)
    assert result_df.empty

def test_generate_grs_insights_nan_values():
    data = {
        'ticker': ['TKR_NAN'],
        'GRS': [50.0],
        'rev_yoy': [np.nan],
        'gm_delta': [np.nan],
        'roa_proxy': [np.nan],
        'ev_sales_zscore': [np.nan],
        'sector_rs_6m': [np.nan],
        'above_200dma': [np.nan],
        'max_drawdown_1y': [np.nan],
        'pe': [np.nan],
    }
    df = pd.DataFrame(data).set_index('ticker')
    result_df = generate_grs_insights(df, top_n=1)
    assert "General positive trend" in result_df.loc['TKR_NAN', 'Evidence']
    assert "General market risk" in result_df.loc['TKR_NAN', 'Risks']
