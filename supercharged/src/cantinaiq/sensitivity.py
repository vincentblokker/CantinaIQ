"""Sensitivity sweep — vary a scoring parameter, measure top-N ranking stability."""

from __future__ import annotations

from typing import cast

import polars as pl
from scipy.stats import kendalltau  # type: ignore[import-untyped]


def parse_range_spec(spec: str) -> list[float]:
    """Parse 'start,end,step' into an inclusive list of floats.

    Example: '0.10,0.30,0.05' → [0.10, 0.15, 0.20, 0.25, 0.30]
    """
    start_s, end_s, step_s = spec.split(",")
    start, end, step = float(start_s), float(end_s), float(step_s)
    out: list[float] = []
    cur = start
    # Add small epsilon to include the endpoint despite float drift.
    while cur <= end + 1e-9:
        out.append(round(cur, 10))
        cur += step
    return out


def kendall_tau_topn(a: pl.DataFrame, b: pl.DataFrame, top_n: int = 20) -> float:
    """Kendall-tau between two ranked producer lists (top-N intersection).

    The score column must be present in both as `composite_score`. Producers
    not appearing in both top-N lists are ignored — this measures stability
    on the intersection, which is the meaningful quantity for shortlist work.
    """
    rank_a = (
        a.sort("composite_score", descending=True)
        .head(top_n)
        .with_row_index(name="rank", offset=1)
        .select(["producer_name", "rank"])
    )
    rank_b = (
        b.sort("composite_score", descending=True)
        .head(top_n)
        .with_row_index(name="rank", offset=1)
        .select(["producer_name", "rank"])
    )
    joined = rank_a.join(rank_b, on="producer_name", how="inner", suffix="_b")
    if joined.height < 2:
        return 0.0
    tau, _ = kendalltau(joined["rank"].to_list(), joined["rank_b"].to_list())
    return cast(float, float(tau))
