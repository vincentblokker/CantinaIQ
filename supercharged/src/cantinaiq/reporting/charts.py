"""Static, deterministic chart generation for the data-quality + methodology reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # headless backend for CI / report rendering
import matplotlib.pyplot as plt


def drop_cascade_waterfall(
    cascade: list[dict[str, Any]],
    config_hash: str,
    out_dir: Path,
) -> Path:
    """Render a deterministic bar chart of post-stage row counts."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"drop-cascade-{config_hash}.svg"
    stages = [c["stage"] for c in cascade]
    rows = [c["post_rows"] for c in cascade]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(stages, rows, color="#8B7355", edgecolor="#1A1714")
    ax.set_ylabel("Rows remaining")
    ax.set_title("Cleaning cascade")
    for i, v in enumerate(rows):
        ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out


def rating_distribution_histogram(
    pre_shrinkage: list[float],
    post_shrinkage: list[float],
    config_hash: str,
    out_dir: Path,
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"rating-distribution-{config_hash}.svg"
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(
        pre_shrinkage,
        bins=20,
        alpha=0.45,
        label="raw rating",
        color="#9B3A2F",
        edgecolor="#1A1714",
    )
    ax.hist(
        post_shrinkage,
        bins=20,
        alpha=0.65,
        label="weighted rating",
        color="#6B8E4E",
        edgecolor="#1A1714",
    )
    ax.set_xlabel("Rating")
    ax.set_ylabel("Wines")
    ax.set_title("Rating distribution: raw vs Bayesian-shrunk")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out


def confidence_donut(counts: dict[str, int], config_hash: str, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"confidence-mix-{config_hash}.svg"
    labels = ["High", "Medium", "Low", "None"]
    values = [counts.get(lab, 0) for lab in labels]
    palette = ["#6B8E4E", "#1F3A5F", "#8B7355", "#9B3A2F"]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(values, labels=labels, colors=palette, wedgeprops={"width": 0.4}, autopct="%1.0f%%")
    ax.set_title("Producer-extraction confidence mix")
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out


def coverage_bars(
    rows: list[dict[str, Any]], config_hash: str, out_dir: Path
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"coverage-per-region-{config_hash}.svg"
    rows_sorted = sorted(rows, key=lambda r: -r["coverage"])
    regions = [r["macro_region"] for r in rows_sorted]
    cov = [r["coverage"] * 100 for r in rows_sorted]
    fig, ax = plt.subplots(figsize=(8, max(3, 0.35 * len(regions) + 1)))
    ax.barh(regions, cov, color="#1F3A5F", edgecolor="#1A1714")
    ax.set_xlabel("High+Medium confidence (%)")
    ax.set_title("Producer-extraction coverage per macro-region")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out
