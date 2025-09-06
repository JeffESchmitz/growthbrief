import importlib

def test_import_signals():
    m = importlib.import_module("growthbrief.signals")
    assert m is not None
