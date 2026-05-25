"""`cantinaiq report …` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer
import yaml

from cantinaiq.reporting.findings import build_findings_context
from cantinaiq.reporting.renderer import render_report
from cantinaiq.runlog import load_latest_run_id, load_run_bundle

report_app = typer.Typer(no_args_is_help=True, help="Render markdown reports from a run.")

TEMPLATES_BY_NAME: dict[str, str] = {
    "data-quality": "data-quality.md.j2",
    "methodology": "methodology.md.j2",
    "findings-one-pager": "findings-one-pager.html.j2",
}


def _output_filename(name: str) -> str:
    """findings-one-pager → .html; everything else → .md."""
    return f"{name}.html" if name.endswith("one-pager") else f"{name}.md"


def _findings_extra_context(processed_dir: Path, copy_path: Path) -> dict[str, Any]:
    from cantinaiq.reporting.reasons import build_reason

    producers = pl.read_parquet(processed_dir / "producers_scored.parquet")
    wines = pl.read_parquet(processed_dir / "wines_scored.parquet")
    copy = yaml.safe_load(copy_path.read_text()) if copy_path.exists() else {}

    top5 = producers.sort("composite_score", descending=True).head(5).to_dicts()
    reasons = {
        p["producer_name"]: build_reason(
            producer_name=p["producer_name"],
            market_segment=p["market_segment"],
            weighted_rating=p["weighted_rating"],
            avg_price=p["avg_price"],
            total_reviews=p["total_reviews"],
            composite_score=p["composite_score"],
            value_score=p.get("value_score", 0.0),
        )
        for p in top5
    }

    return build_findings_context(
        producers_scored=producers,
        wines_scored=wines,
        price_split=float(producers["avg_price"].median() or 60.0),  # type: ignore[arg-type]
        rating_split=float(producers["weighted_rating"].median() or 4.0),  # type: ignore[arg-type]
        reasons=reasons,
        findings_copy={
            "problem": copy.get("problem", ""),
            "limitations": copy.get("limitations", []),
        },
    )


@report_app.command("build")
def build(
    run: Annotated[str | None, typer.Option("--run")] = None,
    only: Annotated[str | None, typer.Option("--only")] = None,
    templates_dir: Annotated[Path, typer.Option("--templates-dir")] = Path("reports/templates"),
    out_dir: Annotated[Path, typer.Option("--out-dir")] = Path("reports/generated"),
    runs_dir: Annotated[Path, typer.Option("--runs-dir")] = Path("data/runs"),
    processed_dir: Annotated[Path, typer.Option("--processed-dir")] = Path("data/processed"),
    findings_copy: Annotated[Path, typer.Option("--findings-copy")] = Path(
        "config/reporting/findings.yaml"
    ),
) -> None:
    """Render one or all known templates against a run-bundle (latest by default)."""
    run_id = run or load_latest_run_id(runs_dir)
    bundle = load_run_bundle(run_id, runs_dir=runs_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = out_dir / "figures"
    targets: dict[str, str] = {only: TEMPLATES_BY_NAME[only]} if only else TEMPLATES_BY_NAME
    for name, tpl in targets.items():
        out_path = out_dir / _output_filename(name)
        extra: dict[str, Any] | None = None
        if name == "findings-one-pager":
            extra = _findings_extra_context(processed_dir, findings_copy)
        render_report(
            template_name=tpl,
            bundle=bundle,
            templates_dir=templates_dir,
            out_path=out_path,
            figures_dir=figures_dir,
            extra_context=extra,
        )
        typer.echo(str(out_path))
