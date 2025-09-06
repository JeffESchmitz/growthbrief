import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from growthbrief.features.industry import industry_snapshot, SECTOR_ETF_MAP

# Fixture for a mock yfinance.download with complete data
@pytest.fixture
def mock_yf_download_complete():
    def _mock_download(symbol, start, end, progress):
        dates = pd.date_range(end=end, periods=300, freq='D') # Enough data for 200-day SMA
        if symbol == 'SPY':
            data = pd.DataFrame({'Adj Close': np.linspace(100, 110, 300)}, index=dates)
        else: # Sector ETF
            data = pd.DataFrame({'Adj Close': np.linspace(105, 115, 300)}, index=dates)
        return data
    return _mock_download

# Fixture for a mock yfinance.download with insufficient data
@pytest.fixture
def mock_yf_download_insufficient():
    def _mock_download(symbol, start, end, progress):
        dates = pd.date_range(end=end, periods=10, freq='D') # Not enough for 6m momentum or SMAs
        data = pd.DataFrame({'Adj Close': np.linspace(100, 105, 10)}, index=dates)
        return data
    return _mock_download

# Fixture for a mock yfinance.download with empty data
@pytest.fixture
def mock_yf_download_empty():
    def _mock_download(symbol, start, end, progress):
        return pd.DataFrame()
    return _mock_download

@patch('yfinance.download')
def test_industry_snapshot_complete_data(mock_download, mock_yf_download_complete):
    mock_download.side_effect = mock_yf_download_complete
    
    # Test with a ticker that has a mapping
    ticker = "AAPL"
    result = industry_snapshot(ticker)

    assert isinstance(result, dict)
    assert 'sector_rs_6m' in result
    assert 'sector_rs_12m' in result
    assert 'sector_above_50dma' in result
    assert 'sector_above_200dma' in result

    # Basic checks that values are not NaN
    assert not np.isnan(result['sector_rs_6m'])
    assert not np.isnan(result['sector_rs_12m'])
    assert result['sector_above_50dma'] in [0.0, 1.0]
    assert result['sector_above_200dma'] in [0.0, 1.0]

@patch('yfinance.download')
def test_industry_snapshot_no_etf_mapping(mock_download):
    result = industry_snapshot("UNKNOWN")

    # All values should be NaN if no ETF mapping
    assert np.isnan(result['sector_rs_6m'])
    assert np.isnan(result['sector_rs_12m'])
    assert np.isnan(result['sector_above_50dma'])
    assert np.isnan(result['sector_above_200dma'])

@patch('yfinance.download')
def test_industry_snapshot_insufficient_data(mock_download, mock_yf_download_insufficient):
    mock_download.side_effect = mock_yf_download_insufficient
    result = industry_snapshot("AAPL")

    # Values requiring sufficient historical data should be NaN
    assert np.isnan(result['sector_rs_6m'])
    assert np.isnan(result['sector_rs_12m'])
    assert np.isnan(result['sector_above_50dma'])
    assert np.isnan(result['sector_above_200dma'])

@patch('yfinance.download')
def test_industry_snapshot_empty_data(mock_download, mock_yf_download_empty):
    mock_download.side_effect = mock_yf_download_empty
    result = industry_snapshot("AAPL")

    # All values should be NaN if dataframes are empty
    assert np.isnan(result['sector_rs_6m'])
    assert np.isnan(result['sector_rs_12m'])
    assert np.isnan(result['sector_above_50dma'])
    assert np.isnan(result['sector_above_200dma'])

@patch('yfinance.download')
def test_industry_snapshot_exception_handling(mock_download):
    mock_download.side_effect = Exception("Network error")
    result = industry_snapshot("AAPL")

    # All values should be NaN on exception
    assert np.isnan(result['sector_rs_6m'])
    assert np.isnan(result['sector_rs_12m'])
    assert np.isnan(result['sector_above_50dma'])
    assert np.isnan(result['sector_above_200dma'])
