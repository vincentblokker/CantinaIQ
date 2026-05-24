"""Deterministic producer extraction (alias whitelist + honorifics + first-token fallback)."""

from __future__ import annotations

import csv
from pathlib import Path

from cantinaiq.enrichment.producer.models import ProducerCandidate

HONORIFICS: tuple[str, ...] = (
    "Marchese",
    "Marchesi",
    "Tenuta",
    "Fattoria",
    "Castello",
    "Azienda Agricola",
    "Cantina",
    "Podere",
    "Villa",
    "Conte",
    "Barone",
    "Antica",
    "Antichi",
    "Vigneti",
    "Cascina",
    "Casa",
)

WINE_STYLE_BLACKLIST: frozenset[str] = frozenset(
    {
        "Brunello",
        "Chianti",
        "Barolo",
        "Barbaresco",
        "Amarone",
        "Prosecco",
        "Rosso",
        "Bianco",
        "Bolgheri",
        "Etna",
        "Soave",
        "Valpolicella",
        "Taurasi",
        "Sangiovese",
        "Nebbiolo",
        "Verdicchio",
        "Montepulciano",
        "Pinot",
        "Sauvignon",
        "Cabernet",
        "Merlot",
        "Vintage",
        "Riserva",
    }
)


class Pass1Extractor:
    def __init__(self, aliases_path: Path):
        self._aliases: list[tuple[str, str, str]] = []  # (pattern, canonical, match_type)
        with Path(aliases_path).open() as f:
            for row in csv.DictReader(f):
                self._aliases.append((row["pattern"], row["canonical_name"], row["match_type"]))
        # Longest patterns first: multi-word aliases win over single-word substrings.
        self._aliases.sort(key=lambda t: -len(t[0]))

    def extract(self, wine_name: str, region: str | None = None) -> ProducerCandidate:  # noqa: ARG002
        if not wine_name:
            return ProducerCandidate(name=None, confidence="None", method="empty-input")
        lower = wine_name.lower()
        for pattern, canonical, match_type in self._aliases:
            if match_type == "prefix" and lower.startswith(pattern.lower()):
                return ProducerCandidate(
                    name=canonical, confidence="High", method=f"alias:{canonical}"
                )
            if match_type == "contains" and pattern.lower() in lower:
                return ProducerCandidate(
                    name=canonical, confidence="High", method=f"alias-contains:{canonical}"
                )
        for hon in HONORIFICS:
            if wine_name.startswith(hon + " "):
                tokens = wine_name.split()
                # Spec §5.1.2 says "first 2-3 tokens" — use 2 for compact producer names
                # like "Podere Sapaio" (Volpolo is the wine, not part of the producer).
                producer = " ".join(tokens[:2])
                return ProducerCandidate(
                    name=producer, confidence="Medium", method="honorific-prefix"
                )
        first = wine_name.split()[0] if wine_name.strip() else ""
        if first and first not in WINE_STYLE_BLACKLIST:
            return ProducerCandidate(name=first, confidence="Low", method="first-token")
        return ProducerCandidate(name=None, confidence="None", method="no-match")
