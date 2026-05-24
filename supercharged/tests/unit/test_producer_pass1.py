from pathlib import Path

from cantinaiq.enrichment.producer.pass1_rules import Pass1Extractor

ALIAS_CSV = Path("data/reference/producer_aliases.csv")


def test_alias_match() -> None:
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    r = ex.extract("Castello di Ama Chianti Classico 2020", region="Toscana")
    assert r.name == "Castello di Ama"
    assert r.confidence == "High"
    assert r.method.startswith("alias:")


def test_honorific_prefix() -> None:
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    r = ex.extract("Podere Sapaio Volpolo 2020", region="Toscana")
    assert r.name == "Podere Sapaio"
    assert r.confidence == "Medium"
    assert r.method == "honorific-prefix"


def test_first_token_blacklisted_returns_none() -> None:
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    r = ex.extract("Chianti Classico 2021", region="Toscana")
    assert r.confidence == "None"  # "Chianti" is blacklisted


def test_alias_beats_first_token() -> None:
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    r = ex.extract("Frescobaldi Nipozzano Riserva 2019", region="Toscana")
    # "Frescobaldi" is in the alias whitelist → High; not a first-token fallback.
    assert r.confidence == "High"
    assert r.name == "Marchesi de' Frescobaldi"


def test_longest_alias_wins() -> None:
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    # "Marchesi Antinori" (alias) must beat "Antinori" (also alias) for "Marchesi Antinori X".
    r = ex.extract("Marchesi Antinori Tignanello 2019", region="Toscana")
    assert r.name == "Marchesi Antinori"


def test_empty_input() -> None:
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    r = ex.extract("", region="Toscana")
    assert r.confidence == "None"
