"""Vivino-vs-Italian-Trade bias quantification.

Goal: surface how the Vivino dataset's regional distribution differs from
real Italian wine imports to the Netherlands. The point isn't to "correct"
the data — Vivino IS the signal we have — but to be honest about which
regions are over-represented (likely: Toscana via wine-influencer culture)
and under-represented (likely: niche regions like Friuli, Liguria).

Baseline source: `data/reference/italian_trade_imports_nl.csv`, derived
from ICE Amsterdam annual Italian wine import reports.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl


# Roll-up alias map: NL translations + sub-appellations → canonical macro-region.
# Keeps the bias table compact and comparable to the Italian Trade baseline.
MACRO_REGION_ALIASES: dict[str, str] = {
    # NL translations
    "Toscane": "Toscana",
    "Umbrië": "Umbria",
    "Lombardije": "Lombardia",
    "Sicilië": "Sicilia",
    "Sardinië": "Sardegna",
    "Calabrië": "Calabria",
    "Apulië": "Puglia",
    "Trentino-Zuid-Tirol": "Trentino-Alto Adige",
    "Südtirol - Alto Adige": "Trentino-Alto Adige",
    # Sub-appellations within Toscana
    "Bolgheri Sassicaia": "Toscana",
    "Bolgheri Superiore": "Toscana",
    "Bolgheri": "Toscana",
    "Brunello di Montalcino": "Toscana",
    "Rosso di Montalcino": "Toscana",
    "Vino Nobile di Montepulciano": "Toscana",
    "Rosso di Montepulciano": "Toscana",
    "Chianti": "Toscana",
    "Chianti Classico": "Toscana",
    "Chianti Rùfina": "Toscana",
    "Chianti Colli Senesi": "Toscana",
    "Carmignano": "Toscana",
    "Morellino di Scansano": "Toscana",
    "Colli della Toscana Centrale": "Toscana",
    "Costa Toscana": "Toscana",
    "Sant'Antimo": "Toscana",
    "Pomino": "Toscana",
    "Montecucco": "Toscana",
    "Colline Lucchesi": "Toscana",
    "Vernaccia di San Gimignano": "Toscana",
    "Alta Valle della Greve": "Toscana",
    "Vin Santo del Chianti Classico": "Toscana",
    "Cortona": "Toscana",
    # Sub-appellations within Veneto
    "Amarone della Valpolicella": "Veneto",
    "Amarone della Valpolicella Classico": "Veneto",
    "Amarone della Valpolicella Valpantena": "Veneto",
    "Valpolicella": "Veneto",
    "Valpolicella Ripasso": "Veneto",
    "Valpolicella Ripasso Classico": "Veneto",
    "Valpolicella Classico": "Veneto",
    "Soave Classico": "Veneto",
    "Soave": "Veneto",
    "Bardolino": "Veneto",
    "Bardolino Classico": "Veneto",
    "Conegliano-Valdobbiadene Prosecco": "Veneto",
    "Conegliano-Valdobbiadene Prosecco Superiore": "Veneto",
    "Prosecco di Treviso": "Veneto",
    "Asolo Prosecco": "Veneto",
    "Lugana": "Veneto",
    "Verona": "Veneto",
    "Venezia": "Veneto",
    "Rosso Veronese": "Veneto",
    "Garda": "Veneto",
    "Montello e Colli Asolani": "Veneto",
    "Colli Berici": "Veneto",
    "delle Venezie": "Veneto",
    "Vigneti delle Dolomiti": "Veneto",
    "Atesino delle Venezie": "Veneto",
    # Sub-appellations within Piemonte
    "Barolo": "Piemonte",
    "Barbaresco": "Piemonte",
    "Barbera d'Asti": "Piemonte",
    "Barbera d'Alba": "Piemonte",
    "Barbera d’Asti": "Piemonte",
    "Barbera d’Alba": "Piemonte",
    "Dolcetto d'Alba": "Piemonte",
    "Dolcetto d'Asti": "Piemonte",
    "Moscato d'Asti": "Piemonte",
    "Moscato d’Asti": "Piemonte",
    "Nebbiolo d'Alba": "Piemonte",
    "Nebbiolo d’Alba": "Piemonte",
    "Asti": "Piemonte",
    "Brachetto d'Acqui": "Piemonte",
    "Brachetto d’Acqui": "Piemonte",
    "Gattinara": "Piemonte",
    "Gavi": "Piemonte",
    "Dogliani": "Piemonte",
    "Nizza": "Piemonte",
    "Monferrato": "Piemonte",
    "Carema": "Piemonte",
    "Colline Novaresi": "Piemonte",
    "Lessona": "Piemonte",
    "Ruchè": "Piemonte",
    "Verduno": "Piemonte",
    "Provincia di Pavia": "Lombardia",  # actually Lombardia
    # Sub-appellations within Sicilia
    "Terre Siciliane": "Sicilia",
    "De Etna": "Sicilia",
    "Etna": "Sicilia",
    "Menfi": "Sicilia",
    "Marsala": "Sicilia",
    "Noto": "Sicilia",
    "Cerasuolo di Vittoria": "Sicilia",
    "Vittoria": "Sicilia",
    "Contea di Sclafani": "Sicilia",
    "Contessa Entellina": "Sicilia",
    "Passito di Pantelleria": "Sicilia",
    # Sub-appellations within Puglia
    "Salento": "Puglia",
    "Primitivo di Manduria": "Puglia",
    "Castel del Monte": "Puglia",
    "Gioia del Colle": "Puglia",
    "Tarantino": "Puglia",
    "Valle d'Itria": "Puglia",
    "Brindisi": "Puglia",
    "Nardò": "Puglia",
    # Sub-appellations within Abruzzo
    "Montepulciano d'Abruzzo": "Abruzzo",
    "Montepulciano d’Abruzzo": "Abruzzo",
    "Trebbiano d'Abruzzo": "Abruzzo",
    "Terre di Chieti": "Abruzzo",
    # Sub-appellations within Sardegna
    "Isola dei Nuraghi": "Sardegna",
    "Carignano del Sulcis": "Sardegna",
    "Cannonau di Sardegna": "Sardegna",
    "Vermentino di Sardegna": "Sardegna",
    "Monica di Sardegna": "Sardegna",
    "Nuragus di Cagliari": "Sardegna",
    "Alghero": "Sardegna",
    # Sub-appellations within Friuli-Venezia Giulia
    "Colli Orientali del Friuli": "Friuli-Venezia Giulia",
    "Friuli Isonzo": "Friuli-Venezia Giulia",
    "Venezia Giulia": "Friuli-Venezia Giulia",
    # Sub-appellations within Umbria
    "Sagrantino di Montefalco": "Umbria",
    "Montefalco": "Umbria",
    "Montefalco Sagrantino": "Umbria",
    "Orvieto": "Umbria",
    "Orvieto Classico": "Umbria",
    "Torgiano": "Umbria",
    "Torgiano Rosso Riserva": "Umbria",
    "Colli Martani": "Umbria",
    # Sub-appellations within Trentino-Alto Adige
    "Trento": "Trentino-Alto Adige",
    "Teroldego Rotaliano": "Trentino-Alto Adige",
    "Valdadige": "Trentino-Alto Adige",
    # Sub-appellations within Marche
    "Verdicchio dei Castelli di Jesi": "Marche",
    "Verdicchio di Matelica": "Marche",
    "Verdicchio di Matelica Riserva": "Marche",
    "Rosso Piceno": "Marche",
    "Rosso Conero": "Marche",
    "Rosso Conero Riserva": "Marche",
    "Lacrima di Morro d'Alba": "Marche",
    "Lacrima di Morro d’Alba": "Marche",
    "Bianchello del Metauro": "Marche",
    "Falerio": "Marche",
    "Offida": "Marche",
    "Colli Pesaresi": "Marche",
    # Sub-appellations within Campania
    "Falanghina del Sannio": "Campania",
    "Falanghina del Beneventano": "Campania",
    "Fiano de Avellino": "Campania",
    "Aglianico del Vulture": "Basilicata",
    "Irpinia": "Campania",
    "Irpinia Campi Taurasini": "Campania",
    "Sannio": "Campania",
    "Costa d'Amalfi": "Campania",
    "Roccamonfina": "Campania",
    "Ischia": "Campania",
    # Sub-appellations within Lazio
    "Roma": "Lazio",
    "Est! Est!! Est!!! di Montefiascone": "Lazio",
    # Sub-appellations within Lombardia
    "Sforzato della Valtellina": "Lombardia",
    "Valtellina": "Lombardia",
    "Valtellina Superiore": "Lombardia",
    "Curtefranca": "Lombardia",
    "Benaco Bresciano": "Lombardia",
    # Sub-appellations within Emilia-Romagna
    "Emilia": "Emilia-Romagna",
    "Reggiano": "Emilia-Romagna",
    "Romagna": "Emilia-Romagna",
    "Rubicone": "Emilia-Romagna",
    "Modena": "Emilia-Romagna",
    "Sangiovese di Romagna": "Emilia-Romagna",
    "Lambrusco Grasparossa di Castelvetro": "Emilia-Romagna",
    "Lambrusco di Sorbara": "Emilia-Romagna",
    # Sub-appellations within Calabria
    "Cirò": "Calabria",
    "Val di Neto": "Calabria",
    # Sub-appellations within Molise
    "Biferno": "Molise",
    # Generic catch-all
    "Vino d'Italia": "Other",
}


def normalise_macro_region(raw: str | None) -> str:
    if raw is None:
        return "Other"
    return MACRO_REGION_ALIASES.get(raw, raw)


@dataclass(frozen=True)
class BiasReport:
    total_wines: int
    rows: list[dict[str, Any]]


def _read_baseline(baseline_csv: Path) -> dict[str, float]:
    out: dict[str, float] = {}
    with Path(baseline_csv).open() as f:
        for row in csv.DictReader(f):
            out[row["macro_region"].strip()] = float(row["share_nl_imports_pct"])
    return out


def compute_bias_report(wines_parquet: Path, baseline_csv: Path) -> BiasReport:
    df = pl.read_parquet(wines_parquet)
    total = df.height
    df = df.with_columns(
        pl.col("macro_region")
        .map_elements(normalise_macro_region, return_dtype=pl.Utf8)
        .alias("macro_region_normalised")
    )
    region_counts = (
        df.group_by("macro_region_normalised")
        .agg(pl.len().alias("n"))
        .sort("n", descending=True)
        .rename({"macro_region_normalised": "macro_region"})
    )
    baseline = _read_baseline(baseline_csv)

    rows: list[dict[str, Any]] = []
    for r in region_counts.to_dicts():
        region = r["macro_region"]
        n = r["n"]
        vivino_share = (n / total) * 100 if total else 0.0
        baseline_share = baseline.get(region, baseline.get("Other", 0.0))
        over_under = (vivino_share / baseline_share) if baseline_share > 0 else float("inf")
        rows.append(
            {
                "macro_region": region,
                "vivino_wines": n,
                "vivino_share_pct": round(vivino_share, 2),
                "baseline_share_pct": round(baseline_share, 2),
                "over_under": round(over_under, 2),
            }
        )
    return BiasReport(total_wines=total, rows=rows)
