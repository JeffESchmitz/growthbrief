import importlib

def test_import_llm():
    m = importlib.import_module("growthbrief.llm")
    assert m is not None
