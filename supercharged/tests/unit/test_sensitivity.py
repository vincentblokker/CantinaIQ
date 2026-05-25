"""Sensitivity sweep — vary a scoring parameter, measure top-N stability."""
from __future__ import annotations

import polars as pl

from cantinaiq.sensitivity import kendall_tau_topn, parse_range_spec


def test_parse_range_spec() -> None:
    assert parse_range_spec("0.10,0.30,0.05") == [0.10, 0.15, 0.20, 0.25, 0.30]
    assert parse_range_spec("1,3,1") == [1.0, 2.0, 3.0]


def test_kendall_tau_identical_rankings_returns_one() -> None:
    a = pl.DataFrame(
        {"producer_name": ["A", "B", "C", "D"], "composite_score": [0.9, 0.8, 0.7, 0.6]}
    )
    b = a.clone()
    tau = kendall_tau_topn(a, b, top_n=4)
    assert tau == 1.0


def test_kendall_tau_reversed_rankings_returns_negative_one() -> None:
    a = pl.DataFrame(
        {"producer_name": ["A", "B", "C", "D"], "composite_score": [0.9, 0.8, 0.7, 0.6]}
    )
    b = pl.DataFrame(
        {"producer_name": ["A", "B", "C", "D"], "composite_score": [0.6, 0.7, 0.8, 0.9]}
    )
    tau = kendall_tau_topn(a, b, top_n=4)
    assert tau == -1.0


def test_kendall_tau_swapped_pair() -> None:
    a = pl.DataFrame(
        {"producer_name": ["A", "B", "C", "D"], "composite_score": [0.9, 0.8, 0.7, 0.6]}
    )
    b = pl.DataFrame(
        {"producer_name": ["A", "B", "C", "D"], "composite_score": [0.9, 0.7, 0.8, 0.6]}
    )
    tau = kendall_tau_topn(a, b, top_n=4)
    assert 0.0 < tau < 1.0
