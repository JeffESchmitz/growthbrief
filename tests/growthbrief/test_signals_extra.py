import pytest

@pytest.mark.skip(reason="implement signals.compute before enabling")
def test_compute_signals_shape(sample_prices):
    from growthbrief import signals
    result = signals.compute(sample_prices)
    assert isinstance(result, dict)
