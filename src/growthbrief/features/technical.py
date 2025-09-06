import yfinance as yf
import pandas as pd
import numpy as np

def _calculate_momentum(series: pd.Series, months: int) -> float:
    """
    Calculates the momentum (percentage change) over a given number of months.
    """
    if len(series) < months * 21: # Approx 21 trading days per month
        return np.nan
    
    start_price = series.iloc[-(months * 21)]
    end_price = series.iloc[-1]
    return (end_price - start_price) / start_price

def _calculate_sma(series: pd.Series, window: int) -> float:
    """
    Calculates the Simple Moving Average (SMA).
    """
    if len(series) < window:
        return np.nan
    return series.iloc[-window:].mean()

def _calculate_max_drawdown(series: pd.Series) -> float:
    """
    Calculates the maximum drawdown of a price series.
    """
    if series.empty:
        return np.nan
    
    # Calculate the running maximum
    running_max = series.cummax()
    # Calculate the drawdown
    drawdown = (series - running_max) / running_max
    # Return the maximum drawdown (most negative value)
    return drawdown.min()

def technical_snapshot(ticker: str) -> dict:
    """
    Fetches key technical indicators for a given ticker.

    Args:
        ticker: The stock ticker symbol (e.g., "AAPL").

    Returns:
        A dictionary containing technical metrics, or NaN for missing data.
    """
    try:
        stock = yf.Ticker(ticker)

        # Fetch enough data for 200-day SMA (approx 252 trading days/year) + 6 months momentum
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.DateOffset(years=1, months=3) # 15 months to be safe

        hist = stock.history(start=start_date, end=end_date)

        if hist.empty:
            return {
                'above_50dma': np.nan,
                'above_100dma': np.nan,
                'above_200dma': np.nan,
                '6m_momentum': np.nan,
                'max_drawdown_1y': np.nan,
            }

        close_prices = hist['Close']

        # --- Above 50/100/200-DMA ---
        current_price = close_prices.iloc[-1]

        sma_50 = _calculate_sma(close_prices, 50)
        above_50dma = 1.0 if current_price > sma_50 else 0.0 if not np.isnan(sma_50) else np.nan

        sma_100 = _calculate_sma(close_prices, 100)
        above_100dma = 1.0 if current_price > sma_100 else 0.0 if not np.isnan(sma_100) else np.nan

        sma_200 = _calculate_sma(close_prices, 200)
        above_200dma = 1.0 if current_price > sma_200 else 0.0 if not np.isnan(sma_200) else np.nan

        # --- 6m momentum ---
        six_m_momentum = _calculate_momentum(close_prices, 6)

        # --- Drawdown filter (e.g., max drawdown over last year) ---
        # Fetch data for 1 year for drawdown calculation
        drawdown_start_date = end_date - pd.DateOffset(years=1)
        drawdown_hist = stock.history(start=drawdown_start_date, end=end_date)
        max_drawdown_1y = _calculate_max_drawdown(drawdown_hist['Close'])

        return {
            'above_50dma': above_50dma,
            'above_100dma': above_100dma,
            'above_200dma': above_200dma,
            '6m_momentum': six_m_momentum,
            'max_drawdown_1y': max_drawdown_1y,
        }

    except Exception as e:
        print(f"Error fetching technical metrics for {ticker}: {e}")
        return {
            'above_50dma': np.nan,
            'above_100dma': np.nan,
            'above_200dma': np.nan,
            '6m_momentum': np.nan,
            'max_drawdown_1y': np.nan,
        }
