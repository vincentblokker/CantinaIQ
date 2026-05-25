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
from cantinaiq.evaluation.cli import evaluate_app
from cantinaiq.sustainability.cli import sustainability_app
from cantinaiq.vivino_live.cli import enrich_app
from cantinaiq.pipeline import STAGES, resolve_stage_subset
from cantinaiq.reporting import report_app

app = typer.Typer(no_args_is_help=True, help="CantinaIQ pipeline CLI.")
run_app = typer.Typer(no_args_is_help=True, help="Run pipeline stages.")
app.add_typer(run_app, name="run")
app.add_typer(report_app, name="report")
app.add_typer(crawler_app, name="crawler")
app.add_typer(evaluate_app, name="evaluate")
app.add_typer(sustainability_app, name="sustainability")
app.add_typer(enrich_app, name="enrich-live")
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
def bias(
    wines_path: Annotated[Path, typer.Option("--wines")] = Path(
        "data/processed/italian_wines_enriched.parquet"
    ),
    baseline_path: Annotated[Path, typer.Option("--baseline")] = Path(
        "data/reference/italian_trade_imports_nl.csv"
    ),
    out_path: Annotated[Path, typer.Option("--out")] = Path(
        "reports/generated/bias-report.md"
    ),
) -> None:
    """Compare Vivino regional distribution to Italian Trade Agency NL imports."""
    from cantinaiq.bias import compute_bias_report

    report = compute_bias_report(wines_path, baseline_path)
    rows_sorted = sorted(report.rows, key=lambda r: r["over_under"], reverse=True)

    lines = [
        "# Vivino Regional Bias Report",
        "",
        f"Total Italian wines in Vivino dataset: **{report.total_wines:,}**.",
        "",
        "Baseline = `data/reference/italian_trade_imports_nl.csv` "
        "(derived from ICE Amsterdam Italian wine import statistics).",
        "",
        "| Macro region | Vivino n | Vivino % | Baseline % | Over/Under |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in rows_sorted:
        marker = (
            "▲" if r["over_under"] >= 1.3
            else ("▼" if r["over_under"] <= 0.7 else "·")
        )
        lines.append(
            f"| {marker} {r['macro_region']} | "
            f"{r['vivino_wines']:,} | "
            f"{r['vivino_share_pct']:.1f}% | "
            f"{r['baseline_share_pct']:.1f}% | "
            f"×{r['over_under']:.2f} |"
        )
    lines.extend(
        [
            "",
            "**Interpretation:** values above ×1.3 mean Vivino over-represents that region "
            "vs. real NL import volumes; values below ×0.7 mean Vivino under-represents it. "
            "Vivino bias does not invalidate the analysis but should be cited in any "
            "external-facing recommendation.",
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    console.print(f"[green]✓ {out_path}[/green]")


@app.command()
def cluster(
    n_clusters: Annotated[int, typer.Option("--k", help="Number of K-Means clusters.")] = 5,
    producers_path: Annotated[Path, typer.Option("--producers")] = Path(
        "data/processed/producers_scored.parquet"
    ),
    out_path: Annotated[Path, typer.Option("--out")] = Path(
        "data/processed/producers_scored_clustered.parquet"
    ),
) -> None:
    """Append a K-Means `cluster_id` column to producers_scored."""
    import polars as pl

    from cantinaiq.clustering import fit_kmeans_clusters

    df = pl.read_parquet(producers_path)
    out = fit_kmeans_clusters(df, n_clusters=n_clusters)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.write_parquet(out_path)

    summary = (
        out.group_by("cluster_id")
        .agg(
            pl.len().alias("n_producers"),
            pl.col("weighted_rating").mean().round(2).alias("mean_rating"),
            pl.col("avg_price").mean().round(0).alias("mean_price"),
            pl.col("total_reviews").mean().round(0).alias("mean_reviews"),
        )
        .sort("cluster_id")
    )
    console.print(f"[bold]K-Means clusters (k={n_clusters}):[/bold]")
    console.print(summary)
    console.print(f"[green]✓ {out_path}[/green]")


@app.command()
def bootstrap(
    n: Annotated[int, typer.Option("--n", help="Number of bootstrap resamples.")] = 1000,
    top: Annotated[int, typer.Option("--top", help="Top-N producers to track.")] = 20,
    seed: Annotated[int, typer.Option("--seed")] = 42,
    wines_path: Annotated[Path, typer.Option("--wines")] = Path(
        "data/processed/wines_scored.parquet"
    ),
    out_path: Annotated[Path, typer.Option("--out")] = Path(
        "reports/generated/bootstrap-ci.md"
    ),
) -> None:
    """Bootstrap producer-ranking confidence intervals."""
    import polars as pl

    from cantinaiq.bootstrap import bootstrap_producer_rank_ci

    wines = pl.read_parquet(wines_path).select(
        ["producer_name", "weighted_rating", "rating_count", "price"]
    )
    cis = bootstrap_producer_rank_ci(wines, n_bootstraps=n, top_n=top, seed=seed)

    lines = [
        f"# Bootstrap rank CIs (n={n}, top-{top}, seed={seed})",
        "",
        f"Based on `{wines_path}` ({wines.height:,} rows). "
        f"Producers that fall outside the top-{top} in a resample receive rank {top + 1}.",
        "",
        "| Producer | p05 | p50 | p95 | mean | appearances/n |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for c in cis:
        lines.append(
            f"| {c['producer_name']} | "
            f"{c['rank_p05']} | {c['rank_p50']} | {c['rank_p95']} | "
            f"{c['rank_mean']:.1f} | {c['appearances']}/{c['n_bootstraps']} |"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    console.print(f"[green]✓ {out_path}[/green]")


@app.command()
def anomaly(
    contamination: Annotated[
        float, typer.Option("--contamination", help="Expected fraction of anomalies.")
    ] = 0.05,
    seed: Annotated[int, typer.Option("--seed")] = 42,
    wines_path: Annotated[Path, typer.Option("--wines")] = Path(
        "data/processed/wines_scored.parquet"
    ),
    out_path: Annotated[Path, typer.Option("--out")] = Path(
        "reports/generated/anomalies.md"
    ),
) -> None:
    """Flag suspicious review patterns via Isolation Forest."""
    import polars as pl

    from cantinaiq.anomaly import flag_review_anomalies

    df = pl.read_parquet(wines_path)
    # Normalise wine-name column for downstream display.
    if "name" not in df.columns and "wine_name" in df.columns:
        df = df.rename({"wine_name": "name"})
    out = flag_review_anomalies(df, contamination=contamination, seed=seed)
    cols = ["name", "region", "rating", "rating_count", "price", "anomaly_score"]
    anomalies = (
        out.filter(pl.col("is_anomaly"))
        .sort("anomaly_score")
        .head(30)
        .select([c for c in cols if c in out.columns])
    )
    lines = [
        f"# Review anomalies (contamination={contamination}, seed={seed})",
        "",
        f"Flagged {out.filter(pl.col('is_anomaly')).height:,} of {out.height:,} wines.",
        "Lower anomaly_score = more anomalous.",
        "",
        "| Wine | Region | Rating | Reviews | Price (€) | Score |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in anomalies.iter_rows(named=True):
        name = str(row.get("name") or "")[:60]
        region = str(row.get("region") or "")[:30]
        lines.append(
            f"| {name} | {region} | "
            f"{row['rating']:.2f} | {row['rating_count']:,} | "
            f"{float(row.get('price') or 0):.2f} | {row['anomaly_score']:.3f} |"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    console.print(f"[green]✓ {out_path}[/green]")


@app.command()
def sensitivity(
    param: Annotated[
        str,
        typer.Option(
            "--param", help="Hydra override key, e.g. scoring.bayesian_m"
        ),
    ],
    range_spec: Annotated[
        str, typer.Option("--range", help="start,end,step e.g. 0.10,0.30,0.05")
    ],
    top_n: Annotated[int, typer.Option("--top-n")] = 20,
    out_path: Annotated[Path, typer.Option("--out")] = Path("reports/generated/sensitivity.md"),
) -> None:
    """Sweep a scoring parameter and report top-N ranking stability per value.

    Re-runs the scoring + export stages for each value, then computes
    Kendall-tau between the resulting top-N producer list and the baseline
    (first value in the sweep). Writes a markdown summary to `--out`.
    """
    import polars as pl

    from cantinaiq.sensitivity import kendall_tau_topn, parse_range_spec

    values = parse_range_spec(range_spec)
    console.print(f"[bold]Sensitivity sweep[/bold] {param} over {values}")

    processed = Path("data/processed/producers_scored.parquet")
    baseline_df: pl.DataFrame | None = None
    rows: list[dict[str, float | str]] = []

    for i, v in enumerate(values):
        override = f"{param}={v}"
        console.print(f"  → run {i + 1}/{len(values)} with {override}")
        _execute(["scoring", "export"], [override])
        df = pl.read_parquet(processed)
        if baseline_df is None:
            baseline_df = df
            tau = 1.0
        else:
            tau = kendall_tau_topn(baseline_df, df, top_n=top_n)
        rows.append({"value": v, "kendall_tau": tau})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Sensitivity sweep: `{param}`",
        "",
        f"Top-{top_n} Kendall-tau vs. baseline ({values[0]}).",
        "",
        "| Value | Kendall-τ |",
        "|---:|---:|",
    ]
    for r in rows:
        lines.append(f"| {r['value']} | {float(r['kendall_tau']):.3f} |")
    out_path.write_text("\n".join(lines) + "\n")
    console.print(f"[green]✓ {out_path}[/green]")


@app.command()
def compare(
    hash_a: Annotated[str, typer.Argument(help="Config hash of run A.")],
    hash_b: Annotated[str, typer.Argument(help="Config hash of run B.")],
    parquet_a: Annotated[Path | None, typer.Option("--parquet-a", help="Explicit path to producers_scored for run A.")] = None,
    parquet_b: Annotated[Path | None, typer.Option("--parquet-b", help="Explicit path to producers_scored for run B.")] = None,
    processed_dir: Annotated[Path, typer.Option("--processed-dir")] = Path("data/processed"),
    top: Annotated[int, typer.Option("--top", help="Show top-N largest rank shifts.")] = 10,
) -> None:
    """Compare two CantinaIQ runs by config hash."""
    from cantinaiq.compare import compare_runs

    path_a = parquet_a or (processed_dir / f"producers_scored__{hash_a}.parquet")
    path_b = parquet_b or (processed_dir / f"producers_scored__{hash_b}.parquet")
    if not path_a.exists():
        path_a = processed_dir / "producers_scored.parquet"
        console.print(
            f"[yellow]No hash-tagged parquet for {hash_a}; using default {path_a}[/yellow]"
        )
    if not path_b.exists():
        path_b = processed_dir / "producers_scored.parquet"
        console.print(
            f"[yellow]No hash-tagged parquet for {hash_b}; using default {path_b}[/yellow]"
        )

    comp = compare_runs(path_a, path_b, hash_a=hash_a, hash_b=hash_b)

    console.print(f"\n[bold]Comparing runs[/bold] {hash_a} ↔ {hash_b}")
    console.print(f"\n[bold]Top {top} rank shifts:[/bold]")
    shifts_sorted = sorted(
        (s for s in comp.ranking_shifts if s.get("shift") is not None),
        key=lambda s: abs(int(s["shift"])),
        reverse=True,
    )[:top]
    for s in shifts_sorted:
        arrow = "↑" if (s["shift"] or 0) > 0 else "↓"
        console.print(
            f"  {arrow} {s['producer_name']:30}  rank {s['rank_a']} → {s['rank_b']}  (Δ={s['shift']})"
        )

    console.print(f"\n[bold]Segment movements:[/bold] {len(comp.segment_movements)}")
    for m in comp.segment_movements[:top]:
        console.print(
            f"  {m['producer_name']:30}  {m['segment_a']} → {m['segment_b']}"
        )


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
