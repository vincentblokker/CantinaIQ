"""`cantinaiq report …` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from cantinaiq.reporting.renderer import render_report
from cantinaiq.runlog import load_latest_run_id, load_run_bundle

report_app = typer.Typer(no_args_is_help=True, help="Render markdown reports from a run.")

TEMPLATES_BY_NAME: dict[str, str] = {
    "data-quality": "data-quality.md.j2",
}


@report_app.command("build")
def build(
    run: Annotated[str | None, typer.Option("--run")] = None,
    only: Annotated[str | None, typer.Option("--only")] = None,
    templates_dir: Annotated[Path, typer.Option("--templates-dir")] = Path("reports/templates"),
    out_dir: Annotated[Path, typer.Option("--out-dir")] = Path("reports/generated"),
    runs_dir: Annotated[Path, typer.Option("--runs-dir")] = Path("data/runs"),
) -> None:
    """Render one or all known templates against a run-bundle (latest by default)."""
    run_id = run or load_latest_run_id(runs_dir)
    bundle = load_run_bundle(run_id, runs_dir=runs_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = out_dir / "figures"
    targets: dict[str, str] = {only: TEMPLATES_BY_NAME[only]} if only else TEMPLATES_BY_NAME
    for name, tpl in targets.items():
        out_path = out_dir / f"{name}.md"
        render_report(
            template_name=tpl,
            bundle=bundle,
            templates_dir=templates_dir,
            out_path=out_path,
            figures_dir=figures_dir,
        )
        typer.echo(str(out_path))
