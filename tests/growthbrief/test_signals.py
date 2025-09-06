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
    prices = pd.DataFrame({'AAPL': np.arange(100, 350)}, index=dates)

    # Compute signals
    computed_signals = signals.compute(prices)

    # Assert that the returned DataFrame has the correct columns
    expected_columns = ['AAPL', 'SMA50', 'SMA100', 'SMA200', 'six_month_momentum_pct', '20d_volatility', 'is_uptrend']
    assert all(col in computed_signals.columns for col in expected_columns)

    # Test SMA values for a specific row (e.g., the last row)
    # SMA50 for the last day (index 249) should be mean of prices[200:250]
    assert computed_signals['SMA50'].iloc[-1] == prices['AAPL'].iloc[200:250].mean()
    assert computed_signals['SMA100'].iloc[-1] == prices['AAPL'].iloc[150:250].mean()
    assert computed_signals['SMA200'].iloc[-1] == prices['AAPL'].iloc[50:250].mean()

    # Test six_month_momentum_pct (assuming 120 trading days for 6 months)
    # For the last day (index 249), it should be (price[249] / price[129] - 1) * 100
    assert computed_signals['six_month_momentum_pct'].iloc[-1] == pytest.approx(
               (prices['AAPL'].iloc[-1] / prices['AAPL'].iloc[prices.shape[0] - 1 - 120] - 1) * 100)

    # Test 20d_volatility (annualized)
    # For the last day, it should be std of daily_returns[230:250] * sqrt(252)
    daily_returns = prices['AAPL'].pct_change()
    assert computed_signals['20d_volatility'].iloc[-1] == pytest.approx(
           daily_returns.iloc[-20:].std() * np.sqrt(252))

    # Test is_uptrend (price > 100DMA)
    # For the last day, it should be 1 if prices[-1] > SMA100[-1], else 0
    expected_is_uptrend = 1 if prices['AAPL'].iloc[-1] > computed_signals['SMA100'].iloc[-1] else 0
    assert computed_signals['is_uptrend'].iloc[-1] == expected_is_uptrend