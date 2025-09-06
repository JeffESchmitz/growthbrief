import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from growthbrief.features.quality import quality_snapshot

# Fixture for a mock yfinance Ticker object with complete data
@pytest.fixture
def mock_ticker_complete_quality():
    mock_income_stmt = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Net Income': 100},
        pd.to_datetime('2023-12-31'): {'Net Income': 90},
    })
    mock_cash_flow = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Cash Flow From Operations': 120, 'Capital Expenditures': -20},
        pd.to_datetime('2023-12-31'): {'Cash Flow From Operations': 110, 'Capital Expenditures': -15},
    })
    mock_balance_sheet = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Total Assets': 500},
        pd.to_datetime('2023-12-31'): {'Total Assets': 450},
    })

    mock_stock = Mock()
    mock_stock.financials = mock_income_stmt
    mock_stock.cashflow = mock_cash_flow
    mock_stock.balance_sheet = mock_balance_sheet
    return mock_stock

# Fixture for a mock yfinance Ticker object with missing data
@pytest.fixture
def mock_ticker_missing_quality_data():
    mock_income_stmt = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Net Income': 100},
    })
    mock_cash_flow = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Cash Flow From Operations': 120},
    })
    mock_balance_sheet = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Total Assets': 500},
    })

    mock_stock = Mock()
    mock_stock.financials = mock_income_stmt
    mock_stock.cashflow = mock_cash_flow
    mock_stock.balance_sheet = mock_balance_sheet
    return mock_stock

# Fixture for a mock yfinance Ticker object with empty dataframes
@pytest.fixture
def mock_ticker_empty_quality_data():
    mock_stock = Mock()
    mock_stock.financials = pd.DataFrame()
    mock_stock.cashflow = pd.DataFrame()
    mock_stock.balance_sheet = pd.DataFrame()
    return mock_stock

@patch('yfinance.Ticker')
def test_quality_snapshot_complete_data(mock_yf_ticker, mock_ticker_complete_quality):
    mock_yf_ticker.return_value = mock_ticker_complete_quality
    result = quality_snapshot("AAPL")

    assert isinstance(result, dict)
    assert 'roa_proxy' in result
    assert 'cash_conversion' in result

    # ROA Proxy: Net Income / Total Assets
    assert np.isclose(result['roa_proxy'], 100 / 500)

    # Cash Conversion: FCF / Net Income (FCF = CFO + CapEx)
    fcf = 120 + (-20) # CapEx is negative in yfinance
    assert np.isclose(result['cash_conversion'], fcf / 100)

@patch('yfinance.Ticker')
def test_quality_snapshot_missing_data(mock_yf_ticker, mock_ticker_missing_quality_data):
    mock_yf_ticker.return_value = mock_ticker_missing_quality_data
    result = quality_snapshot("MSFT")

    # Test cases where data is insufficient for calculation
    assert np.isclose(result['roa_proxy'], 100 / 500) # ROA can still be calculated
    assert np.isnan(result['cash_conversion']) # FCF needs CapEx, which is missing for delta

@patch('yfinance.Ticker')
def test_quality_snapshot_empty_data(mock_yf_ticker, mock_ticker_empty_quality_data):
    mock_yf_ticker.return_value = mock_ticker_empty_quality_data
    result = quality_snapshot("GOOG")

    # All values should be NaN if dataframes are empty
    assert np.isnan(result['roa_proxy'])
    assert np.isnan(result['cash_conversion'])

@patch('yfinance.Ticker')
def test_quality_snapshot_exception_handling(mock_yf_ticker):
    mock_yf_ticker.side_effect = Exception("Network error")
    result = quality_snapshot("AMZN")

    # All values should be NaN on exception
    assert np.isnan(result['roa_proxy'])
    assert np.isnan(result['cash_conversion'])
