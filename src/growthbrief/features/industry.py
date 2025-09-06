import yfinance as yf
import pandas as pd
import numpy as np

# Simple mapping for common tickers to their sector ETFs
# In a real application, this would be more robust (e.g., external data, industry classification)
SECTOR_ETF_MAP = {
    'AAPL': 'XLK',  # Technology Select Sector SPDR Fund
    'MSFT': 'XLK',
    'NVDA': 'SMH',  # VanEck Semiconductor ETF
    'GOOG': 'XLK',
    'AMZN': 'XLY',  # Consumer Discretionary Select Sector SPDR Fund
    'META': 'XLC',  # Communication Services Select Sector SPDR Fund
    'TSLA': 'XLY',
    'JPM': 'XLF',  # Financial Select Sector SPDR Fund
    'XOM': 'XLE',  # Energy Select Sector SPDR Fund
    'JNJ': 'XLV',  # Health Care Select Sector SPDR Fund
    'PG': 'XLP',  # Consumer Staples Select Sector SPDR Fund
    'V': 'XLF',
    'MA': 'XLF',
    'UNH': 'XLV',
    'HD': 'XLY',
    'KO': 'XLP',
    'PEP': 'XLP',
    'DIS': 'XLC',
    'CMCSA': 'XLC',
    'VZ': 'XLC',
    'T': 'XLC',
    'PFE': 'XLV',
    'MRK': 'XLV',
    'ABBV': 'XLV',
    'LLY': 'XLV',
    'NKE': 'XLY',
    'SBUX': 'XLY',
    'MCD': 'XLY',
    'BA': 'XLI',  # Industrial Select Sector SPDR Fund
    'CAT': 'XLI',
    'GE': 'XLI',
    'HON': 'XLI',
    'MMM': 'XLI',
    'DOW': 'XLB',  # Materials Select Sector SPDR Fund
    'DUK': 'XLU',  # Utilities Select Sector SPDR Fund
    'NEE': 'XLU',
    'SO': 'XLU',
    'PLD': 'XLRE', # Real Estate Select Sector SPDR Fund
    'SPG': 'XLRE',
}

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

def industry_snapshot(ticker: str) -> dict:
    """
    Fetches industry tailwind metrics for a given ticker.

    Args:
        ticker: The stock ticker symbol (e.g., "AAPL").

    Returns:
        A dictionary containing industry metrics, or NaN for missing data.
    """
    sector_etf_symbol = SECTOR_ETF_MAP.get(ticker.upper())
    if not sector_etf_symbol:
        print(f"Warning: No sector ETF mapping found for {ticker}")
        return {
            'sector_rs_6m': np.nan,
            'sector_rs_12m': np.nan,
            'sector_above_50dma': np.nan,
            'sector_above_200dma': np.nan,
        }

    try:
        # Fetch historical data for sector ETF and SPY
        # Fetch enough data for 12 months + 200-day SMA (approx 252 trading days/year)
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.DateOffset(years=1, months=3) # 15 months to be safe

        sector_etf_data = yf.download(sector_etf_symbol, start=start_date, end=end_date, progress=False)
        spy_data = yf.download('SPY', start=start_date, end=end_date, progress=False)

        if sector_etf_data.empty or spy_data.empty:
            return {
                'sector_rs_6m': np.nan,
                'sector_rs_12m': np.nan,
                'sector_above_50dma': np.nan,
                'sector_above_200dma': np.nan,
            }

        sector_etf_close = sector_etf_data['Adj Close']
        spy_close = spy_data['Adj Close']

        # --- Relative Strength vs SPY ---
        sector_6m_mom = _calculate_momentum(sector_etf_close, 6)
        spy_6m_mom = _calculate_momentum(spy_close, 6)
        sector_rs_6m = sector_6m_mom - spy_6m_mom if not np.isnan(sector_6m_mom) and not np.isnan(spy_6m_mom) else np.nan

        sector_12m_mom = _calculate_momentum(sector_etf_close, 12)
        spy_12m_mom = _calculate_momentum(spy_close, 12)
        sector_rs_12m = sector_12m_mom - spy_12m_mom if not np.isnan(sector_12m_mom) and not np.isnan(spy_12m_mom) else np.nan

        # --- Industry Breadth (proxy with ETF price vs SMAs) ---
        sector_etf_50dma = _calculate_sma(sector_etf_close, 50)
        sector_etf_200dma = _calculate_sma(sector_etf_close, 200)

        sector_above_50dma = 1.0 if sector_etf_close.iloc[-1] > sector_etf_50dma else 0.0 if not np.isnan(sector_etf_50dma) else np.nan
        sector_above_200dma = 1.0 if sector_etf_close.iloc[-1] > sector_etf_200dma else 0.0 if not np.isnan(sector_etf_200dma) else np.nan

        return {
            'sector_rs_6m': sector_rs_6m,
            'sector_rs_12m': sector_rs_12m,
            'sector_above_50dma': sector_above_50dma,
            'sector_above_200dma': sector_above_200dma,
        }

    except Exception as e:
        print(f"Error fetching industry metrics for {ticker}: {e}")
        return {
            'sector_rs_6m': np.nan,
            'sector_rs_12m': np.nan,
            'sector_above_50dma': np.nan,
            'sector_above_200dma': np.nan,
        }
