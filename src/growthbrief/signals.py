import pandas as pd
import numpy as np

def compute(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Computes various technical signals for a given DataFrame of prices.

    Args:
        prices: A pandas DataFrame with ticker symbols as columns and dates as index.

    Returns:
        A pandas DataFrame with multi-indexed columns (ticker, signal_name).
    """
    all_signals = {}

    for ticker in prices.columns:
        ticker_prices = prices[ticker]
        signals = pd.DataFrame(index=ticker_prices.index)

        # Simple Moving Averages
        signals['SMA50'] = ticker_prices.rolling(window=50).mean()
        signals['SMA100'] = ticker_prices.rolling(window=100).mean()
        signals['SMA200'] = ticker_prices.rolling(window=200).mean()

        # Six-month momentum (assuming 20 trading days per month, 120 trading days for 6 months)
        signals['six_month_momentum_pct'] = (ticker_prices / ticker_prices.shift(120) - 1) * 100

        # 20-day volatility (annualized)
        daily_returns = ticker_prices.pct_change()
        signals['20d_volatility'] = daily_returns.rolling(window=20).std() * np.sqrt(252)

        # Is Uptrend (price > 100DMA)
        signals['is_uptrend'] = (ticker_prices > signals['SMA100']).astype(int)

        # Add original price to signals for this ticker
        signals['Price'] = ticker_prices

        # Store signals for this ticker with a multi-index
        all_signals[ticker] = signals

    # Concatenate all ticker signals into a single DataFrame with multi-indexed columns
    final_signals_df = pd.concat(all_signals, axis=1)
    return final_signals_df
