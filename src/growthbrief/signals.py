import pandas as pd
import numpy as np

def compute(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Computes various technical signals for a given DataFrame of prices.

    Args:
        prices: A pandas DataFrame with ticker symbols as columns and dates as index.

    Returns:
        A pandas DataFrame with the original prices and computed signals.
    """
    signals = prices.copy()

    # Simple Moving Averages
    signals['SMA50'] = prices.rolling(window=50).mean()
    signals['SMA100'] = prices.rolling(window=100).mean()
    signals['SMA200'] = prices.rolling(window=200).mean()

    # Six-month momentum (assuming 20 trading days per month, 120 trading days for 6 months)
    signals['six_month_momentum_pct'] = (prices / prices.shift(120) - 1) * 100

    # 20-day volatility (annualized)
    daily_returns = prices.pct_change()
    signals['20d_volatility'] = daily_returns.rolling(window=20).std() * np.sqrt(252)

    # Is Uptrend (price > 100DMA)
    signals['is_uptrend'] = (prices['AAPL'] > signals['SMA100']).astype(int)

    return signals