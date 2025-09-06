import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from growthbrief.features.fundamentals import fundamentals_snapshot

# Fixture for a mock yfinance Ticker object with complete data
@pytest.fixture
def mock_ticker_complete():
    mock_income_stmt = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Total Revenue': 1000, 'Gross Profit': 400, 'Operating Income': 200, 'Net Income': 150},
        pd.to_datetime('2023-12-31'): {'Total Revenue': 900, 'Gross Profit': 350, 'Operating Income': 180, 'Net Income': 130},
    })
    mock_cash_flow = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Cash Flow From Operations': 180, 'Capital Expenditures': -50},
        pd.to_datetime('2023-12-31'): {'Cash Flow From Operations': 160, 'Capital Expenditures': -40},
    })
    mock_balance_sheet = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Total Assets': 1000},
        pd.to_datetime('2023-12-31'): {'Total Assets': 900},
    })

    mock_stock = Mock()
    mock_stock.financials = mock_income_stmt
    mock_stock.cashflow = mock_cash_flow
    mock_stock.balance_sheet = mock_balance_sheet
    return mock_stock

# Fixture for a mock yfinance Ticker object with missing data
@pytest.fixture
def mock_ticker_missing_data():
    mock_income_stmt = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Total Revenue': 1000},
    })
    mock_cash_flow = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Cash Flow From Operations': 180},
    })
    mock_balance_sheet = pd.DataFrame({
        pd.to_datetime('2024-12-31'): {'Total Assets': 1000},
    })

    mock_stock = Mock()
    mock_stock.financials = mock_income_stmt
    mock_stock.cashflow = mock_cash_flow
    mock_stock.balance_sheet = mock_balance_sheet
    return mock_stock

# Fixture for a mock yfinance Ticker object with empty dataframes
@pytest.fixture
def mock_ticker_empty_data():
    mock_stock = Mock()
    mock_stock.financials = pd.DataFrame()
    mock_stock.cashflow = pd.DataFrame()
    mock_stock.balance_sheet = pd.DataFrame()
    return mock_stock

@patch('yfinance.Ticker')
def test_fundamentals_snapshot_complete_data(mock_yf_ticker, mock_ticker_complete):
    mock_yf_ticker.return_value = mock_ticker_complete
    result = fundamentals_snapshot("AAPL")

    assert isinstance(result, dict)
    assert 'rev_yoy' in result
    assert 'gm' in result
    assert 'gm_delta' in result
    assert 'om' in result
    assert 'om_delta' in result
    assert 'fcf_margin' in result
    assert 'fcf_delta' in result
    assert 'accruals_proxy' in result

    # Basic assertions for calculated values (approximate due to float precision)
    assert np.isclose(result['rev_yoy'], (1000-900)/900)
    assert np.isclose(result['gm'], 400/1000)
    assert np.isclose(result['gm_delta'], (400/1000) - (350/900))
    assert np.isclose(result['om'], 200/1000)
    assert np.isclose(result['om_delta'], (200/1000) - (180/900))
    
    # FCF = CFO - CapEx (CapEx is negative in yfinance, so CFO + CapEx)
    fcf_current = 180 + (-50)
    fcf_prev = 160 + (-40)
    assert np.isclose(result['fcf_margin'], fcf_current / 1000)
    assert np.isclose(result['fcf_delta'], (fcf_current / 1000) - (fcf_prev / 900))

    # Accruals proxy: (NetIncome − CFO)/AvgAssets
    net_income_current = 150
    cfo_current = 180
    avg_assets = (1000 + 900) / 2
    assert np.isclose(result['accruals_proxy'], (net_income_current - cfo_current) / avg_assets)

@patch('yfinance.Ticker')
def test_fundamentals_snapshot_missing_data(mock_yf_ticker, mock_ticker_missing_data):
    mock_yf_ticker.return_value = mock_ticker_missing_data
    result = fundamentals_snapshot("MSFT")

    # All values should be NaN if data is insufficient for calculation
    assert np.isnan(result['rev_yoy'])
    assert np.isnan(result['gm_delta'])
    assert np.isnan(result['om_delta'])
    assert np.isnan(result['fcf_delta'])
    assert np.isnan(result['accruals_proxy'])

@patch('yfinance.Ticker')
def test_fundamentals_snapshot_empty_data(mock_yf_ticker, mock_ticker_empty_data):
    mock_yf_ticker.return_value = mock_ticker_empty_data
    result = fundamentals_snapshot("GOOG")

    # All values should be NaN if dataframes are empty
    assert np.isnan(result['rev_yoy'])
    assert np.isnan(result['gm'])
    assert np.isnan(result['om'])
    assert np.isnan(result['fcf_margin'])
    assert np.isnan(result['accruals_proxy'])

@patch('yfinance.Ticker')
def test_fundamentals_snapshot_exception_handling(mock_yf_ticker):
    mock_yf_ticker.side_effect = Exception("Network error")
    result = fundamentals_snapshot("AMZN")

    # All values should be NaN on exception
    assert np.isnan(result['rev_yoy'])
    assert np.isnan(result['gm'])
    assert np.isnan(result['om'])
    assert np.isnan(result['fcf_margin'])
    assert np.isnan(result['accruals_proxy'])
