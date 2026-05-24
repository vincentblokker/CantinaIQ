from hypothesis import given
from hypothesis import strategies as st

from cantinaiq.scoring.math import value_score


@given(
    wr=st.floats(min_value=0.1, max_value=5, allow_nan=False),
    price_low=st.floats(min_value=1.0, max_value=50, allow_nan=False),
    price_high=st.floats(min_value=51, max_value=1000, allow_nan=False),
)
def test_value_decreases_in_price(wr: float, price_low: float, price_high: float) -> None:
    assert value_score(wr, price_low) > value_score(wr, price_high)


@given(
    price=st.floats(min_value=1, max_value=1000, allow_nan=False),
    wr_low=st.floats(min_value=0.1, max_value=2.5, allow_nan=False),
    wr_high=st.floats(min_value=2.6, max_value=5, allow_nan=False),
)
def test_value_increases_in_rating(price: float, wr_low: float, wr_high: float) -> None:
    assert value_score(wr_high, price) > value_score(wr_low, price)
