import pandas as pd
import numpy as np
import datetime as dt
import pytest

@pytest.fixture
def sample_prices():
    # 60 business days of synthetic adj close for AAPL/MSFT
    dates = pd.bdate_range(end=dt.date.today(), periods=60)
    data = {
        'AAPL': np.linspace(150, 175, len(dates)) + np.random.default_rng(0).normal(0, 1, len(dates)),
        'MSFT': np.linspace(300, 330, len(dates)) + np.random.default_rng(1).normal(0, 1, len(dates)),
    }
    return pd.DataFrame(data, index=dates)
