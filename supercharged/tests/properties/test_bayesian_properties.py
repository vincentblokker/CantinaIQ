from hypothesis import given, settings
from hypothesis import strategies as st

from cantinaiq.scoring.math import bayesian_weighted_rating


@given(
    rating=st.floats(min_value=0, max_value=5, allow_nan=False, allow_infinity=False),
    rating_count=st.integers(min_value=1, max_value=100_000),
    m=st.integers(min_value=1, max_value=10_000),
    global_mean=st.floats(min_value=3.0, max_value=4.5, allow_nan=False),
)
def test_weighted_rating_is_convex_combination(
    rating: float, rating_count: int, m: int, global_mean: float
) -> None:
    wr = bayesian_weighted_rating(rating, rating_count, m, global_mean)
    lo, hi = min(rating, global_mean), max(rating, global_mean)
    assert lo - 1e-9 <= wr <= hi + 1e-9


@given(
    rating=st.floats(min_value=0, max_value=5, allow_nan=False),
    m=st.integers(min_value=1, max_value=10_000),
    global_mean=st.floats(min_value=3.0, max_value=4.5, allow_nan=False),
)
@settings(max_examples=200)
def test_high_volume_approaches_rating(rating: float, m: int, global_mean: float) -> None:
    wr_low = bayesian_weighted_rating(rating, rating_count=1, m=m, global_mean=global_mean)
    wr_high = bayesian_weighted_rating(
        rating, rating_count=10_000_000, m=m, global_mean=global_mean
    )
    assert abs(wr_high - rating) <= abs(wr_low - rating) + 1e-9


@given(
    rating=st.floats(min_value=0, max_value=5, allow_nan=False),
    rating_count=st.integers(min_value=1, max_value=100_000),
    global_mean=st.floats(min_value=3.0, max_value=4.5, allow_nan=False),
)
@settings(max_examples=200)
def test_high_m_approaches_global_mean(
    rating: float, rating_count: int, global_mean: float
) -> None:
    wr_low_m = bayesian_weighted_rating(rating, rating_count, m=1, global_mean=global_mean)
    wr_high_m = bayesian_weighted_rating(
        rating, rating_count, m=10_000_000, global_mean=global_mean
    )
    assert abs(wr_high_m - global_mean) <= abs(wr_low_m - global_mean) + 1e-9
