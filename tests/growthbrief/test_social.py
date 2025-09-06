import importlib

def test_import_social():
    m = importlib.import_module("growthbrief.social")
    assert m is not None
