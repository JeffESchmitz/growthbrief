import yfinance as yf
import pandas as pd
import numpy as np

def _calculate_zscore(series: pd.Series, years: int = 3) -> float:
    """
    Calculates the z-score for the latest value in a series against the past 'years' of data.
    Returns NaN if insufficient data.
    """
    series = series.dropna() # Ensure no NaNs in calculation
    if len(series) < years + 1: # Need current + 'years' of historical data
        return np.nan

    # Ensure the series is sorted from oldest to newest for consistent z-score calculation
    series_sorted = series.sort_values(ascending=True) # Use sort_values for Series

    # Take the last 'years' values (excluding the most recent one for historical context)
    historical_data = series_sorted.iloc[-(years + 1):-1] # Exclude current, take previous 'years' values
    current_value = series_sorted.iloc[-1]

    if historical_data.empty or historical_data.std(ddof=0) == 0: # Use ddof=0 for consistency with np.std
        return np.nan

    # Calculate z-score of the current value against the historical data
    return (current_value - historical_data.mean()) / historical_data.std(ddof=0)

def valuation_snapshot(ticker: str) -> dict:
    """
    Fetches key valuation metrics for a given ticker using yfinance.

    Args:
        ticker: The stock ticker symbol (e.g., "AAPL").

    Returns:
        A dictionary containing valuation metrics, or NaN for missing data.
    """
    try:
        stock = yf.Ticker(ticker)

        info = stock.info
        income_stmt = stock.financials

        if income_stmt.empty:
            return {
                'pe': np.nan,
                'ev_sales': np.nan,
                'ev_sales_zscore': np.nan,
                'peg_proxy': np.nan,
            }

        income_stmt = income_stmt.T.sort_index(ascending=False)

        # --- PE Ratio ---
        pe = info.get('trailingPE', np.nan)
        if pe is None:
            pe = np.nan

        # --- EV/Sales or EV/EBIT ---
        enterprise_value = info.get('enterpriseValue', np.nan)
        total_revenue = income_stmt.get('Total Revenue')
        ebit = income_stmt.get('EBIT')

        ev_sales = np.nan
        if enterprise_value is not None and total_revenue is not None and not total_revenue.empty and total_revenue.iloc[0] != 0:
            ev_sales = enterprise_value / total_revenue.iloc[0]
        elif enterprise_value is not None and ebit is not None and not ebit.empty and ebit.iloc[0] != 0: # Fallback to EV/EBIT
            ev_sales = enterprise_value / ebit.iloc[0] # Renaming to ev_ebit if this is the case

        # --- EV/Sales Z-score (3-year) ---
        ev_sales_zscore = np.nan
        if enterprise_value is not None and total_revenue is not None and len(total_revenue) >= 4: # Need at least 4 years for 3 historical + current
            # Create a series of EV/Sales for the past few years
            historical_ev_sales = []
            for i in range(min(len(total_revenue), 4)): # Look at up to 4 periods (current + 3 historical)
                if total_revenue.iloc[i] != 0:
                    # This is a simplification, as enterpriseValue is current, not historical
                    # For a true historical EV/Sales, we'd need historical enterprise values.
                    # As a proxy, we'll use current EV with historical sales.
                    historical_ev_sales.append(enterprise_value / total_revenue.iloc[i])
                else:
                    historical_ev_sales.append(np.nan)
            
            historical_ev_sales_series = pd.Series(historical_ev_sales).dropna()
            if len(historical_ev_sales_series) >= 4: # Ensure enough data for z-score
                ev_sales_zscore = _calculate_zscore(historical_ev_sales_series, years=3)

        # --- PEG Proxy: PE / (Revenue Growth Rate * 100) ---
        peg_proxy = np.nan
        if pe is not None and total_revenue is not None and len(total_revenue) > 1 and total_revenue.iloc[1] != 0:
            revenue_growth_rate = (total_revenue.iloc[0] - total_revenue.iloc[1]) / total_revenue.iloc[1]
            if revenue_growth_rate > 0:
                peg_proxy = pe / (revenue_growth_rate * 100)

        return {
            'pe': pe,
            'ev_sales': ev_sales,
            'ev_sales_zscore': ev_sales_zscore,
            'peg_proxy': peg_proxy,
        }

    except Exception as e:
        print(f"Error fetching valuation metrics for {ticker}: {e}")
        return {
            'pe': np.nan,
            'ev_sales': np.nan,
            'ev_sales_zscore': np.nan,
            'peg_proxy': np.nan,
        }
