import pytest
from growthbrief.features.leadership import leadership_confidence_from_text

def test_leadership_confidence_from_text_positive():
    text = "The company showed strong growth and is expected to exceed expectations."
    assert leadership_confidence_from_text(text) == 8.0

def test_leadership_confidence_from_text_negative():
    text = "The company is facing a challenging environment with significant headwinds."
    assert leadership_confidence_from_text(text) == 3.0

def test_leadership_confidence_from_text_neutral():
    text = "The company provided an update on its operations."
    assert leadership_confidence_from_text(text) == 5.0

def test_leadership_confidence_from_text_case_insensitivity():
    text = "STRONG GROWTH and EXCEED EXPECTATIONS."
    assert leadership_confidence_from_text(text) == 8.0

def test_leadership_confidence_from_text_determinism():
    text1 = "This is a test with strong growth."
    text2 = "This is a test with strong growth."
    assert leadership_confidence_from_text(text1) == leadership_confidence_from_text(text2)
