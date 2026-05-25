"""`cantinaiq enrich live` Typer subcommand."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import polars as pl
import typer

from cantinaiq.vivino_live.enrich import enrich_wines

enrich_app = typer.Typer(no_args_is_help=True, help="Live enrichment helpers.")


@enrich_app.command("live")
def live(
    wines_path: Annotated[
        Path, typer.Option("--wines")
    ] = Path("data/processed/wines_scored.parquet"),
    top_n: Annotated[int, typer.Option("--top")] = 50,
    out_path: Annotated[
        Path, typer.Option("--out")
    ] = Path("data/exports/wine_enrichments.json"),
    cache_dir: Annotated[
        Path, typer.Option("--cache-dir")
    ] = Path("data/reference/vivino_cache"),
    rate_limit_ms: Annotated[int, typer.Option("--rate-limit-ms")] = 500,
    with_network: Annotated[bool, typer.Option("--with-network")] = False,
) -> None:
    """Enrich top-N wines via Vivino (Firecrawl). Cached on disk."""
    if not with_network:
        typer.echo(
            "Stub mode: --with-network not set. Re-run with --with-network and "
            "FIRECRAWL_API_KEY for live data."
        )
        return

    df = pl.read_parquet(wines_path)
    if "name" not in df.columns and "wine_name" in df.columns:
        df = df.rename({"wine_name": "name"})
    df = df.sort("rating_count", descending=True).head(top_n)
    cols = ["name", "region", "rating", "rating_count", "price"]
    wines = df.select([c for c in cols if c in df.columns]).to_dicts()
    enriched = enrich_wines(wines, cache_dir=cache_dir, rate_limit_ms=rate_limit_ms)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(enriched, indent=2, default=str))
    typer.echo(f"Wrote {out_path} ({len(enriched)} entries)")
    enriched_with_extras = [w for w in enriched if "alcohol_percentage" in w or "grape_varieties" in w]
    typer.echo(f"Enriched with extras: {len(enriched_with_extras)}/{len(enriched)}")
