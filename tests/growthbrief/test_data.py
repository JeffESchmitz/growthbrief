import importlib
import pandas as pd
import pytest
import vcr
from growthbrief import data

def test_import_data():
    m = importlib.import_module("growthbrief.data")
    assert m is not None

@vcr.use_cassette('tests/fixtures/vcr_cassettes/test_get_prices.yaml')
def test_get_prices():
    tickers = ["AAPL", "MSFT"]
    prices = data.get_prices(tickers)
    assert isinstance(prices, pd.DataFrame)
    assert list(prices.columns) == tickers
    assert len(prices) > 252 * 4 # Should have at least 4 years of data