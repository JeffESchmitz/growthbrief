import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from growthbrief.features.technical import technical_snapshot, _calculate_max_drawdown

# Fixture for a mock yfinance Ticker object with complete historical data
@pytest.fixture
def mock_ticker_complete_technical():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=300, freq='D') # Enough data for 200-day SMA
    data = pd.DataFrame({'Close': np.linspace(100, 150, 300)}, index=dates)
    mock_stock = Mock()
    mock_stock.history.return_value = data
    return mock_stock

# Fixture for a mock yfinance Ticker object with insufficient historical data
@pytest.fixture
def mock_ticker_insufficient_technical_data():
    dates = pd.date_range(end=pd.Timestamp.now(), periods=10, freq='D') # Not enough for SMAs or momentum
    data = pd.DataFrame({'Close': np.linspace(100, 105, 10)}, index=dates)
    mock_stock = Mock()
    mock_stock.history.return_value = data
    return mock_stock

# Fixture for a mock yfinance Ticker object with empty historical data
@pytest.fixture
def mock_ticker_empty_technical_data():
    mock_stock = Mock()
    mock_stock.history.return_value = pd.DataFrame()
    return mock_stock

@patch('yfinance.Ticker')
def test_technical_snapshot_complete_data(mock_yf_ticker, mock_ticker_complete_technical):
    mock_yf_ticker.return_value = mock_ticker_complete_technical
    result = technical_snapshot("AAPL")

    assert isinstance(result, dict)
    assert 'above_50dma' in result
    assert 'above_100dma' in result
    assert 'above_200dma' in result
    assert '6m_momentum' in result
    assert 'max_drawdown_1y' in result

    # Basic checks that values are not NaN
    assert result['above_50dma'] in [0.0, 1.0]
    assert result['above_100dma'] in [0.0, 1.0]
    assert result['above_200dma'] in [0.0, 1.0]
    assert not np.isnan(result['6m_momentum'])
    assert not np.isnan(result['max_drawdown_1y'])

@patch('yfinance.Ticker')
def test_technical_snapshot_insufficient_data(mock_yf_ticker, mock_ticker_insufficient_technical_data):
    mock_yf_ticker.return_value = mock_ticker_insufficient_technical_data
    result = technical_snapshot("MSFT")

    # Values requiring sufficient historical data should be NaN
    assert np.isnan(result['above_50dma'])
    assert np.isnan(result['above_100dma'])
    assert np.isnan(result['above_200dma'])
    assert np.isnan(result['6m_momentum'])
    assert np.isnan(result['max_drawdown_1y'])

@patch('yfinance.Ticker')
def test_technical_snapshot_empty_data(mock_yf_ticker, mock_ticker_empty_technical_data):
    mock_yf_ticker.return_value = mock_ticker_empty_technical_data
    result = technical_snapshot("GOOG")

    # All values should be NaN if dataframes are empty
    assert np.isnan(result['above_50dma'])
    assert np.isnan(result['above_100dma'])
    assert np.isnan(result['above_200dma'])
    assert np.isnan(result['6m_momentum'])
    assert np.isnan(result['max_drawdown_1y'])

@patch('yfinance.Ticker')
def test_technical_snapshot_exception_handling(mock_yf_ticker):
    mock_yf_ticker.side_effect = Exception("Network error")
    result = technical_snapshot("AMZN")

    # All values should be NaN on exception
    assert np.isnan(result['above_50dma'])
    assert np.isnan(result['above_100dma'])
    assert np.isnan(result['above_200dma'])
    assert np.isnan(result['6m_momentum'])
    assert np.isnan(result['max_drawdown_1y'])

def test_calculate_max_drawdown_synthetic_series():
    series = pd.Series([100, 90, 110, 80, 120])
    # Drawdowns: (90-100)/100 = -0.1, (110-100)/100 = 0.1, (80-110)/110 = -0.27, (120-120)/120 = 0
    # Max drawdown should be from 110 to 80, which is (80-110)/110 = -0.2727
    assert np.isclose(_calculate_max_drawdown(series), (80-110)/110)

    series_no_drawdown = pd.Series([100, 110, 120, 130])
    assert np.isclose(_calculate_max_drawdown(series_no_drawdown), 0.0)

    series_empty = pd.Series([])
    assert np.isnan(_calculate_max_drawdown(series_empty))
