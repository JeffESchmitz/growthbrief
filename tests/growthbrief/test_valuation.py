import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from growthbrief.features.valuation import valuation_snapshot, _calculate_zscore

# Fixture for a mock yfinance Ticker object with complete data for valuation
@pytest.fixture
def mock_ticker_complete_valuation():
    mock_info = {
        'trailingPE': 25.0,
        'enterpriseValue': 1000000000,
    }
    mock_income_stmt = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Total Revenue': 100000000, 'EBIT': 50000000},
        pd.to_datetime('2023-12-31'): {'Total Revenue': 90000000, 'EBIT': 45000000},
        pd.to_datetime('2022-12-31'): {'Total Revenue': 80000000, 'EBIT': 40000000},
        pd.to_datetime('2021-12-31'): {'Total Revenue': 70000000, 'EBIT': 35000000},
    })

    mock_stock = Mock()
    mock_stock.info = mock_info
    mock_stock.financials = mock_income_stmt
    return mock_stock

# Fixture for a mock yfinance Ticker object with missing data for valuation
@pytest.fixture
def mock_ticker_missing_valuation_data():
    mock_info = {
        'trailingPE': None,
        'enterpriseValue': None,
    }
    mock_income_stmt = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Total Revenue': 100000000},
    })

    mock_stock = Mock()
    mock_stock.info = mock_info
    mock_stock.financials = mock_income_stmt
    return mock_stock

# Fixture for a mock yfinance Ticker object with empty dataframes
@pytest.fixture
def mock_ticker_empty_valuation_data():
    mock_stock = Mock()
    mock_stock.info = {}
    mock_stock.financials = pd.DataFrame()
    return mock_stock

@patch('yfinance.Ticker')
def test_valuation_snapshot_complete_data(mock_yf_ticker, mock_ticker_complete_valuation):
    mock_yf_ticker.return_value = mock_ticker_complete_valuation
    result = valuation_snapshot("AAPL")

    assert isinstance(result, dict)
    assert 'pe' in result
    assert 'ev_sales' in result
    assert 'ev_sales_zscore' in result
    assert 'peg_proxy' in result

    assert np.isclose(result['pe'], 25.0)
    assert np.isclose(result['ev_sales'], 1000000000 / 100000000)

    # Test PEG proxy
    # Revenue growth rate = (100M - 90M) / 90M = 0.111...
    # PEG = PE / (growth rate * 100) = 25 / (0.111... * 100) = 2.25
    assert np.isclose(result['peg_proxy'], 25.0 / (((100000000 - 90000000) / 90000000) * 100))

    # Test EV/Sales Z-score
    # The _calculate_zscore function is tested separately, here we just check it's not NaN
    assert not np.isnan(result['ev_sales_zscore'])

@patch('yfinance.Ticker')
def test_valuation_snapshot_missing_data(mock_yf_ticker, mock_ticker_missing_valuation_data):
    mock_yf_ticker.return_value = mock_ticker_missing_valuation_data
    result = valuation_snapshot("MSFT")

    assert np.isnan(result['pe'])
    assert np.isnan(result['ev_sales'])
    assert np.isnan(result['ev_sales_zscore'])
    assert np.isnan(result['peg_proxy'])

@patch('yfinance.Ticker')
def test_valuation_snapshot_empty_data(mock_yf_ticker, mock_ticker_empty_valuation_data):
    mock_yf_ticker.return_value = mock_ticker_empty_valuation_data
    result = valuation_snapshot("GOOG")

    assert np.isnan(result['pe'])
    assert np.isnan(result['ev_sales'])
    assert np.isnan(result['ev_sales_zscore'])
    assert np.isnan(result['peg_proxy'])

@patch('yfinance.Ticker')
def test_valuation_snapshot_exception_handling(mock_yf_ticker):
    mock_yf_ticker.side_effect = Exception("Network error")
    result = valuation_snapshot("AMZN")

    assert np.isnan(result['pe'])
    assert np.isnan(result['ev_sales'])
    assert np.isnan(result['ev_sales_zscore'])
    assert np.isnan(result['peg_proxy'])

def test_calculate_zscore_synthetic_series():
    # Test with a simple series where z-score can be easily calculated
    series = pd.Series([10, 20, 30, 40, 50]) # Current value is 50
    # Historical data for 3 years: [20, 30, 40]
    # Mean = 30, Std = 8.16
    # Z-score = (50 - 30) / 8.16 = 2.449
    assert np.isclose(_calculate_zscore(series, years=3), (50 - np.mean([20,30,40])) / np.std([20,30,40], ddof=0))

    # Test with insufficient data
    series_short = pd.Series([10, 20])
    assert np.isnan(_calculate_zscore(series_short, years=3))

    # Test with constant series (std dev = 0)
    series_constant = pd.Series([10, 10, 10, 10, 10])
    assert np.isnan(_calculate_zscore(series_constant, years=3))

    # Test with NaN values in series
    series_nan = pd.Series([10, 20, np.nan, 40, 50])
    assert np.isclose(_calculate_zscore(series_nan, years=3), (50 - np.mean([20,40,50])) / np.std([20,40,50], ddof=0))