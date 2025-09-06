import importlib

def test_import_risk():
    m = importlib.import_module("growthbrief.risk")
    assert m is not None
