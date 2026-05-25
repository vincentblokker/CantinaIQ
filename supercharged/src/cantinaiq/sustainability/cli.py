"""`cantinaiq sustainability …` Typer subcommands."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Annotated

import polars as pl
import typer

from cantinaiq.sustainability.lookup import lookup_sustainability

sustainability_app = typer.Typer(
    no_args_is_help=True, help="Producer sustainability lookups."
)


@sustainability_app.command("check")
def check(
    producers_path: Annotated[
        Path, typer.Option("--producers")
    ] = Path("data/processed/producers_scored.parquet"),
    top_n: Annotated[
        int, typer.Option("--top", help="Check top-N producers by composite_score.")
    ] = 50,
    only: Annotated[
        str | None,
        typer.Option(
            "--only",
            help="Comma-separated explicit producer names (bypasses --top selection).",
        ),
    ] = None,
    cache_path: Annotated[
        Path, typer.Option("--cache")
    ] = Path("data/reference/sustainability_cache.csv"),
    out_json: Annotated[
        Path, typer.Option("--out-json")
    ] = Path("data/exports/sustainability_report.json"),
    out_md: Annotated[
        Path, typer.Option("--out-md")
    ] = Path("reports/generated/sustainability.md"),
    rate_limit_ms: Annotated[
        int, typer.Option("--rate-limit-ms", help="Sleep between Firecrawl calls.")
    ] = 500,
) -> None:
    """Check sustainability cert for top-N producers; cache results."""
    cache: dict[str, dict[str, str]] = {}
    if cache_path.exists():
        with cache_path.open() as f:
            for row in csv.DictReader(f):
                cache[row["producer"]] = row

    if only:
        producer_names = [p.strip() for p in only.split(",") if p.strip()]
    else:
        df = (
            pl.read_parquet(producers_path)
            .sort("composite_score", descending=True)
            .head(top_n)
        )
        producer_names = df["producer_name"].to_list()

    results: list[dict[str, str | None | bool]] = []
    fresh_calls = 0
    for producer in producer_names:
        if producer in cache:
            results.append(
                {
                    "producer": producer,
                    "certification": cache[producer].get("certification") or None,
                    "source": cache[producer].get("source"),
                    "from_cache": True,
                }
            )
            continue
        res = lookup_sustainability(producer)
        results.append(
            {
                "producer": producer,
                "certification": res.certification,
                "source": res.source,
                "from_cache": False,
            }
        )
        fresh_calls += 1
        if rate_limit_ms > 0:
            time.sleep(rate_limit_ms / 1000)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["producer", "certification", "source"])
        w.writeheader()
        for r in results:
            w.writerow(
                {
                    "producer": r["producer"],
                    "certification": r["certification"] or "",
                    "source": r["source"] or "",
                }
            )

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(results, indent=2))

    certified = [r for r in results if r["certification"]]
    sustainable_targets = certified[:5]
    lines = [
        "# Sustainability check (FederBio + Demeter)",
        "",
        f"Checked **{len(producer_names)}** producers"
        + (" (by --only list)" if only else f" (top **{top_n}** by composite_score)")
        + ". "
        f"Fresh API calls: **{fresh_calls}**. "
        f"Certified hits: **{len(certified)}**.",
        "",
        "## Sustainable Targets (top 5 certified producers)",
        "",
        "| Producer | Certification | Source |",
        "|---|---|---|",
    ]
    for r in sustainable_targets:
        lines.append(
            f"| {r['producer']} | {r['certification']} | "
            f"[link]({r['source']}) |"
        )
    lines.extend(
        ["", "## Full results", "", "| Producer | Certification |", "|---|---|"]
    )
    for r in results:
        cert = r["certification"] or "—"
        lines.append(f"| {r['producer']} | {cert} |")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n")
    typer.echo(f"Wrote {out_md}")
    typer.echo(f"Wrote {out_json}")
