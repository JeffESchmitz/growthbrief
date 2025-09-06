import importlib
import pandas as pd
import numpy as np
import pytest
from growthbrief import signals

def test_import_signals():
    m = importlib.import_module("growthbrief.signals")
    assert m is not None

def test_compute_signals():
    # Create a sample DataFrame with enough data for all calculations
    # Let's create 250 rows to cover SMA200
    dates = pd.bdate_range(start='2023-01-01', periods=250, freq='B')
    prices = pd.DataFrame({'AAPL': np.arange(100, 350), 'MSFT': np.arange(200, 450)}, index=dates)

    # Compute signals
    computed_signals = signals.compute(prices)

    # Assert that the returned DataFrame has multi-indexed columns
    assert isinstance(computed_signals.columns, pd.MultiIndex)
    assert computed_signals.columns.names == [None, None] # Default names

    # Check the first level of the MultiIndex (tickers)
    assert list(computed_signals.columns.levels[0]) == ['AAPL', 'MSFT']

    # Check the second level of the MultiIndex (signal names)
    expected_signal_names = ['SMA50', 'SMA100', 'SMA200', 'six_month_momentum_pct', '20d_volatility', 'is_uptrend', 'Price']
    assert all(s in computed_signals.columns.levels[1] for s in expected_signal_names)

    # Test SMA values for a specific row (e.g., the last row) for AAPL
    ticker = 'AAPL'
    assert computed_signals[(ticker, 'SMA50')].iloc[-1] == prices[ticker].iloc[200:250].mean()
    assert computed_signals[(ticker, 'SMA100')].iloc[-1] == prices[ticker].iloc[150:250].mean()
    assert computed_signals[(ticker, 'SMA200')].iloc[-1] == prices[ticker].iloc[50:250].mean()

    # Test six_month_momentum_pct for AAPL
    assert computed_signals[(ticker, 'six_month_momentum_pct')].iloc[-1] == pytest.approx(
               (prices[ticker].iloc[-1] / prices[ticker].iloc[prices.shape[0] - 1 - 120] - 1) * 100)

    # Test 20d_volatility for AAPL
    daily_returns = prices[ticker].pct_change()
    assert computed_signals[(ticker, '20d_volatility')].iloc[-1] == pytest.approx(
           daily_returns.iloc[-20:].std() * np.sqrt(252))

    # Test is_uptrend for AAPL
    expected_is_uptrend = 1 if prices[ticker].iloc[-1] > computed_signals[(ticker, 'SMA100')].iloc[-1] else 0
    assert computed_signals[(ticker, 'is_uptrend')].iloc[-1] == expected_is_uptrend

    # Test for MSFT as well (just a quick check)
    ticker = 'MSFT'
    assert computed_signals[(ticker, 'Price')].iloc[-1] == prices[ticker].iloc[-1]
    assert computed_signals[(ticker, 'SMA50')].iloc[-1] == prices[ticker].iloc[200:250].mean()
