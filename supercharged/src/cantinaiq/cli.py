"""CantinaIQ Typer CLI entrypoint."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
from hydra import compose, initialize_config_dir
from rich.console import Console

# Side-effect: importing stage subpackages registers their callables with STAGES.
# These are empty placeholders today; each fills in as its Phase lands.
from cantinaiq import (  # noqa: F401, E402  (intentional side-effect imports)
    __version__,
    cleaning,
    enrichment,
    export,
    ingestion,
    scoring,
    validation,
)
from cantinaiq.config.loader import config_from_omegaconf
from cantinaiq.config.models import PipelineConfig
from cantinaiq.crawler.cli import crawler_app
from cantinaiq.pipeline import STAGES, resolve_stage_subset
from cantinaiq.reporting import report_app

app = typer.Typer(no_args_is_help=True, help="CantinaIQ pipeline CLI.")
run_app = typer.Typer(no_args_is_help=True, help="Run pipeline stages.")
app.add_typer(run_app, name="run")
app.add_typer(report_app, name="report")
app.add_typer(crawler_app, name="crawler")
console = Console()

CONFIG_DIR = str((Path(__file__).resolve().parents[2] / "config").resolve())


@app.callback()
def main() -> None:
    """CantinaIQ — Slurpini Partner Intelligence Engine."""


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


def _load_cfg(overrides: list[str]) -> PipelineConfig:
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        oc = compose(config_name="pipeline", overrides=overrides)
    return config_from_omegaconf(oc)


def _new_run_id(config_hash: str) -> str:
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M")
    return f"{ts}__{config_hash}"


def _execute(stages: list[str], overrides: list[str]) -> None:
    cfg = _load_cfg(overrides)
    run_id = _new_run_id(cfg.hash)
    console.print(f"[bold]CantinaIQ run[/bold] {run_id}  config={cfg.hash}")
    for name in stages:
        fn = STAGES.get(name)
        if fn is None:
            console.print(f"  [red]✗ stage '{name}' not implemented yet[/red]")
            raise typer.Exit(code=2)
        console.print(f"  → [cyan]{name}[/cyan]")
        fn(cfg, run_id)


@run_app.command("ingestion")
def run_ingestion(
    overrides: Annotated[list[str] | None, typer.Argument()] = None,
) -> None:
    """Run the ingestion stage."""
    _execute(["ingestion"], overrides or [])


@run_app.command("cleaning")
def run_cleaning(
    overrides: Annotated[list[str] | None, typer.Argument()] = None,
) -> None:
    """Run the cleaning stage."""
    _execute(["cleaning"], overrides or [])


@run_app.command("validation")
def run_validation(
    overrides: Annotated[list[str] | None, typer.Argument()] = None,
) -> None:
    """Run the validation stage."""
    _execute(["validation"], overrides or [])


@run_app.command("enrichment")
def run_enrichment(
    overrides: Annotated[list[str] | None, typer.Argument()] = None,
) -> None:
    """Run the enrichment stage."""
    _execute(["enrichment"], overrides or [])


@run_app.command("scoring")
def run_scoring(
    overrides: Annotated[list[str] | None, typer.Argument()] = None,
) -> None:
    """Run the scoring stage."""
    _execute(["scoring"], overrides or [])


@run_app.command("export")
def run_export(
    overrides: Annotated[list[str] | None, typer.Argument()] = None,
) -> None:
    """Run the export stage."""
    _execute(["export"], overrides or [])


@run_app.command("all")
def run_all(
    from_stage: Annotated[str | None, typer.Option("--from")] = None,
    overrides: Annotated[list[str] | None, typer.Argument()] = None,
) -> None:
    """Run the full pipeline (optionally resuming from a stage)."""
    stages = resolve_stage_subset(start=from_stage)
    _execute(stages, overrides or [])


@app.command()
def audit(config_hash: str) -> None:
    """Show the config snapshot and matching runs for a config hash."""
    snap = Path("config/snapshots") / f"{config_hash}.yaml"
    if not snap.exists():
        console.print(f"[red]No snapshot found for hash {config_hash}[/red]")
        raise typer.Exit(code=1)
    console.print(f"[bold]Snapshot:[/bold] {snap}")
    runs_dir = Path("data/runs")
    if runs_dir.exists():
        matching = [
            p.name
            for p in runs_dir.iterdir()
            if p.is_dir() and p.name.endswith(f"__{config_hash}")
        ]
        console.print(f"[bold]Matching runs:[/bold] {len(matching)}")
        for r in sorted(matching):
            console.print(f"  - {r}")


@app.command()
def status() -> None:
    """Print the most recent run summary."""
    from cantinaiq.runlog import load_latest_run_id, load_run_bundle

    runs_dir = Path("data/runs")
    try:
        run_id = load_latest_run_id(runs_dir)
    except FileNotFoundError:
        console.print("[yellow]No runs found.[/yellow]")
        return
    bundle = load_run_bundle(run_id, runs_dir=runs_dir)
    console.print(f"[bold]Latest run:[/bold] {bundle.run_id}")
    for name, s in bundle.stages.items():
        console.print(
            f"  {name:12}  pre={s.pre_rows:>8}  post={s.post_rows:>8}  "
            f"dropped={sum(s.drops.values()):>6}  err={'yes' if s.error else 'no'}"
        )


if __name__ == "__main__":  # pragma: no cover
    app()
