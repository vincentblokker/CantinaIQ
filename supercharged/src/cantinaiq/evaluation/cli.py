"""`cantinaiq evaluate …` Typer subcommands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from cantinaiq.evaluation.gold_set import evaluate_producer_extraction

evaluate_app = typer.Typer(no_args_is_help=True, help="Pipeline output evaluation.")


@evaluate_app.command("producer-extraction")
def producer_extraction(
    producers_path: Annotated[
        Path, typer.Option("--producers")
    ] = Path("data/processed/producers_scored.parquet"),
    gold_path: Annotated[Path, typer.Option("--gold")] = Path(
        "data/reference/known_producers_top50.csv"
    ),
    out_path: Annotated[Path, typer.Option("--out")] = Path(
        "reports/generated/producer-extraction-eval.json"
    ),
) -> None:
    """Evaluate recall of producer extraction against the canonical top-50."""
    ev = evaluate_producer_extraction(producers_path, gold_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "gold_size": ev.gold_size,
                "producers_total": ev.producers_total,
                "recall_exact": ev.recall_exact,
                "recall_contains": ev.recall_contains,
                "matched_exact": ev.matched_exact,
                "matched_contains": ev.matched_contains,
                "missed": ev.missed,
            },
            indent=2,
        )
    )
    typer.echo(
        f"Gold size: {ev.gold_size}  "
        f"recall@exact: {ev.recall_exact:.2%}  "
        f"recall@contains: {ev.recall_contains:.2%}"
    )
    typer.echo(f"Wrote {out_path}")
