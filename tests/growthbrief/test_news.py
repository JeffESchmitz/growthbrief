import importlib

def test_import_news():
    m = importlib.import_module("growthbrief.news")
    assert m is not None
