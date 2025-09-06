import time
import pandas as pd
import yfinance as yf
from requests.exceptions import RequestException

def get_prices(tickers: list[str], retries: int = 3, backoff_factor: float = 0.5) -> pd.DataFrame:
    """
    Fetches historical adjusted close prices for a list of tickers.

    Args:
        tickers: A list of ticker symbols.
        retries: The number of times to retry a failed download.
        backoff_factor: The factor by which to increase the wait time between retries.

    Returns:
        A pandas DataFrame with the adjusted close prices, indexed by date.
    """
    all_prices = {}
    for ticker in tickers:
        for i in range(retries):
            try:
                data = yf.download(ticker, period="5y", progress=False)
                if len(data) < 252:  # Less than a year of trading days
                    print(f"Warning: Ticker {ticker} has less than one year of data. Skipping.")
                    continue
                all_prices[ticker] = data["Adj Close"]
                break  # Success
            except RequestException as e:
                if i < retries - 1:
                    time.sleep(backoff_factor * (2 ** i))
                else:
                    print(f"Error fetching {ticker}: {e}")
    
    if not all_prices:
        return pd.DataFrame()

    return pd.DataFrame(all_prices)