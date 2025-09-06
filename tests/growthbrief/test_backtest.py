import importlib

def test_import_backtest():
    m = importlib.import_module("growthbrief.backtest")
    assert m is not None
