import importlib

def test_import_brief():
    m = importlib.import_module("growthbrief.brief")
    assert m is not None
