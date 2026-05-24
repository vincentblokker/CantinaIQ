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
