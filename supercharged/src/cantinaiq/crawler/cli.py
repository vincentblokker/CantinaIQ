"""`cantinaiq crawler …` Typer subcommands."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import polars as pl
import typer

from cantinaiq.crawler.extend import add_derived_fields, enrich_with_firecrawl

crawler_app = typer.Typer(no_args_is_help=True, help="Crawler extension utilities.")


@crawler_app.command("extend")
def extend(
    raw_path: Annotated[Path, typer.Option("--raw")] = Path("data/interim/01_raw.parquet"),
    out_path: Annotated[Path, typer.Option("--out")] = Path("data/interim/01_raw_extended.parquet"),
    with_network: Annotated[bool, typer.Option("--with-network")] = False,
    sample: Annotated[
        int,
        typer.Option("--sample", help="Limit network calls to top-N rows by review count."),
    ] = 50,
) -> None:
    """Extend the ingested parquet with vintage + producer_hint, optionally enriched via Firecrawl."""
    df = pl.read_parquet(raw_path)
    df = add_derived_fields(df)
    typer.echo(f"Added derived fields → {df.height:,} rows, {len(df.columns)} columns.")

    if with_network:
        if not os.environ.get("FIRECRAWL_API_KEY"):
            typer.echo("FIRECRAWL_API_KEY not set; skipping network enrichment.")
        else:
            count_col = "rating_count" if "rating_count" in df.columns else None
            top = df.sort(count_col, descending=True).head(sample) if count_col else df.head(sample)
            enriched = 0
            for row in top.iter_rows(named=True):
                # The Vivino crawler export does not include canonical URLs.
                # We approximate via the search URL; production code should resolve a
                # stable wine ID via the search API first.
                wine_name = str(row.get("name") or row.get("wine_name") or "").strip()
                if not wine_name:
                    continue
                url = "https://www.vivino.com/search/wines?q=" + wine_name.replace(" ", "+")
                extras = enrich_with_firecrawl(wine_name=wine_name, url=url)
                if extras:
                    enriched += 1
            typer.echo(f"Enriched {enriched}/{top.height} top-reviewed wines via Firecrawl.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out_path)
    typer.echo(f"Wrote {out_path}.")
