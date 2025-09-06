import os
import time
import logging
from datetime import date as dt_date, timedelta as dt_timedelta, datetime as dt_datetime
from pathlib import Path

import pandas as pd
import yfinance as yf
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _fetch_prices_from_source(ticker: str, retries: int, backoff_factor: float) -> pd.DataFrame:
    """
    Helper function to fetch historical adjusted close prices for a single ticker from yfinance.
    """
    for i in range(retries):
        try:
            data = yf.download(ticker, period="5y", progress=False)
            # If columns are multi-indexed, flatten them
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1) # Drop the ticker level
            
            if data.empty:
                logging.warning(f"No data found for ticker {ticker} from source.")
                raise RequestException(f"No data found for ticker {ticker}")
            if len(data) < 252:  # Less than a year of trading days
                logging.warning(f"Ticker {ticker} has less than one year of data from source. Skipping.")
                return pd.DataFrame()
            return data["Close"].to_frame(name=ticker)
        except RequestException as e:
            if i < retries - 1:
                time.sleep(backoff_factor * (2 ** i))
            else:
                logging.error(f"Error fetching {ticker} from source after {retries} retries: {e}")
                return pd.DataFrame()
    return pd.DataFrame()

def get_prices(tickers: list[str], retries: int = 3, backoff_factor: float = 0.5) -> pd.DataFrame:
    """
    Fetches historical adjusted close prices for a list of tickers with caching.

    Args:
        tickers: A list of ticker symbols.
        retries: The number of times to retry a failed download from source.
        backoff_factor: The factor by which to increase the wait time between retries.

    Returns:
        A pandas DataFrame with the adjusted close prices, indexed by date.
    """
    all_prices = {}
    for ticker in tickers:
        cache_file = CACHE_DIR / f"{ticker}.csv"
        data_from_cache = pd.DataFrame()
        
        # Check cache freshness
        if cache_file.exists():
            file_mod_time = dt_datetime.fromtimestamp(cache_file.stat().st_mtime)
            if dt_datetime.now() - file_mod_time < dt_timedelta(days=1):
                try:
                    data_from_cache = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                    if not data_from_cache.empty and ticker in data_from_cache.columns:
                        logging.info(f"CACHE HIT: {ticker}")
                        all_prices[ticker] = data_from_cache[ticker]
                        continue # Move to next ticker
                    else:
                        logging.warning(f"CACHE CORRUPT: {ticker} - re-fetching.")
                except Exception as e:
                    logging.warning(f"CACHE CORRUPT: {ticker} - {e} - re-fetching.")
        
        # Cache miss or stale or corrupt - fetch from source
        logging.info(f"CACHE MISS/STALE: {ticker} - fetching from source.")
        fresh_data = _fetch_prices_from_source(ticker, retries, backoff_factor)
        
        if not fresh_data.empty:
            fresh_data.to_csv(cache_file)
            logging.info(f"CACHE REFRESH: {ticker}")
            all_prices[ticker] = fresh_data[ticker]
        else:
            logging.warning(f"Failed to get data for {ticker} from any source.")

    if not all_prices:
        return pd.DataFrame()

    # Concatenate all ticker data into a single DataFrame
    final_df = pd.concat(all_prices.values(), axis=1)
    final_df.columns = all_prices.keys()
    return final_df
