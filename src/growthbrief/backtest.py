import pandas as pd
import numpy as np
import vectorbt as vbt

# Suppress vectorbt warnings for cleaner output
vbt.settings.set_theme("dark")


vbt.settings.returns["year_freq"] = "365 days"

def run_backtest(grs_df: pd.DataFrame, prices: pd.DataFrame, top_n: int = 5) -> dict:
    """
    Runs a vectorized backtest based on monthly top-N GRS scores.

    Args:
        grs_df: DataFrame with GRS scores for each ticker, indexed by date.
        prices: DataFrame with historical adjusted close prices for all tickers.
        top_n: Number of top GRS tickers to select each month.

    Returns:
        A dictionary containing backtest metrics.
    """
    if grs_df.empty or prices.empty:
        return {
            'cagr': np.nan,
            'stdev': np.nan,
            'max_drawdown': np.nan,
            'hit_rate': np.nan,
            'sharpe_ratio': np.nan,
            'total_return': np.nan,
        }

    # Align GRS and prices by date and tickers
    # Ensure prices are aligned with the dates in grs_df (monthly rebalance)
    # Resample prices to monthly end to align with GRS calculation frequency
    # For simplicity, we assume grs_df is already monthly or can be aligned.
    # We need daily prices for backtesting.

    # Ensure prices DataFrame has a DatetimeIndex and columns are tickers
    prices.index = pd.to_datetime(prices.index).drop_duplicates()
    prices = prices.sort_index()

    # Ensure GRS DataFrame has a DatetimeIndex and columns are tickers (or GRS column)
    # Assuming grs_df has 'GRS' column and 'ticker' as index
    # We need to pivot grs_df to have dates as index and tickers as columns for vbt
    # This is a simplification. In a real scenario, GRS would be calculated monthly.
    # For this backtest, we'll assume grs_df contains daily GRS or we use the latest GRS for the month.

    # For monthly rebalance, we need to determine positions at the start of each month
    # based on GRS scores from the end of the previous month.

    # Create a signal for top N GRS tickers
    # This requires a multi-index DataFrame where first level is date, second is ticker
    # and values are GRS scores.

    # Let's assume grs_df is already in the format: index=date, columns=ticker, values=GRS
    # If grs_df is from run_signals.py, it's ticker as index, GRS as column.
    # We need to transform it to be time-indexed for vectorbt.

    # For a simple backtest, let's assume `grs_df` is a daily DataFrame with GRS scores for each ticker.
    # If `grs_df` is from `run_signals.py`, it's a snapshot. We need historical GRS.
    # This step needs to be refined based on how GRS is generated historically.

    # For now, let's simulate a monthly GRS signal from the `grs_df` snapshot.
    # This is a placeholder and needs actual historical GRS data.
    # We'll create a dummy signal for demonstration.

    # Create a dummy signal: buy top N GRS tickers at the start of each month
    # This requires a DataFrame with same index as prices, and columns as tickers
    # with True/False for entry/exit.

    # Let's assume `prices` contains all tickers we are interested in.
    # And `grs_df` contains the GRS scores for these tickers (snapshot).

    # To make it work with vectorbt, we need a signal DataFrame with the same shape as prices.
    # For monthly rebalance, we'll create a signal at the start of each month.

    # Get monthly rebalance points
    rebalance_dates = prices.index.to_period('M').drop_duplicates().map(lambda x: x.start_time)

    # Create an empty signal DataFrame


    # This part needs actual historical GRS data to be meaningful.
    # For demonstration, we'll just pick random top N for each rebalance date.
    # In a real scenario, you'd use historical GRS scores to determine top N.

    # For now, let's use the provided grs_df (snapshot) and apply it monthly.
    # This is a strong simplification and not a true historical backtest.
    # It will use the same GRS scores for all rebalance periods.

    # Create a dummy GRS signal for all dates in prices, based on the provided grs_df
    # This assumes grs_df is a single snapshot of GRS scores.
    grs_scores_aligned = pd.DataFrame(index=prices.index, columns=grs_df.index)
    for ticker in grs_df.index:
        grs_scores_aligned[ticker] = grs_df.loc[ticker, 'GRS']

    # Generate entries based on top N GRS scores at rebalance dates
    entries_data = []
    for rebalance_date in rebalance_dates:
        top_n_tickers = grs_df['GRS'].nlargest(top_n).index.tolist()
        
        # Create a row for this rebalance date
        row = {col: False for col in prices.columns}
        for ticker in top_n_tickers:
            if ticker in row: # Ensure ticker is in prices.columns
                row[ticker] = True
        entries_data.append(row)
    
    entries = pd.DataFrame(entries_data, index=rebalance_dates, columns=prices.columns)

    # Define exits (e.g., hold for one month, then rebalance)
    exits = entries.shift(1, freq='M').fillna(False) # Exit at the start of next month

    # Ensure entries and exits have the same index as prices for vectorbt
    entries = entries.reindex(prices.index, fill_value=False)
    exits = exits.reindex(prices.index, fill_value=False)

    # Run backtest
    pf = vbt.Portfolio.from_signals(
        prices,
        entries,
        exits,
        init_cash=100000,
        freq='1D', # Daily frequency for prices
        direction='longonly',
        accumulate=False, # Rebalance fully
    )

    # Calculate metrics
    metrics = {
        'cagr': pf.annual_returns().iloc[-1] if not pf.annual_returns().empty else np.nan,
        'stdev': pf.annualized_volatility().iloc[-1] if not pf.annualized_volatility().empty else np.nan,
        'max_drawdown': pf.max_drawdown().iloc[-1] if not pf.max_drawdown().empty else np.nan,
        'hit_rate': pf.trades.win_rate() if not pf.trades.empty else np.nan,
        'sharpe_ratio': pf.sharpe_ratio().iloc[-1] if not pf.sharpe_ratio().empty else np.nan,
        'total_return': pf.total_return().iloc[-1] if not pf.total_return().empty else np.nan,
    }

    return metrics