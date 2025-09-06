import importlib

def test_import_data():
    m = importlib.import_module("growthbrief.data")
    assert m is not None
