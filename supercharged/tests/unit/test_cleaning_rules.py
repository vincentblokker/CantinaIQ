from cantinaiq.cleaning.rules import (
    extract_vintage,
    fix_encoding,
    normalise_wine_name,
    parse_tuple_string,
)


def test_parse_tuple_string() -> None:
    assert parse_tuple_string("('Italy',)") == "Italy"
    assert parse_tuple_string("Italy") == "Italy"
    assert parse_tuple_string("('Italy', 'IT')") == "Italy"
    assert parse_tuple_string("") == ""


def test_fix_encoding() -> None:
    assert fix_encoding("ItaliÃ«") == "Italië"  # UTF-8 "ë" (0xC3 0xAB) read as Latin-1
    assert fix_encoding("ToscÃ na") == "Toscàna"  # "Ã " (2 chars) → "à" (1 char)
    assert fix_encoding("Italy") == "Italy"


def test_normalise_wine_name() -> None:
    assert normalise_wine_name("  Castello di Ama  Chianti 2020 ") == "castello di ama chianti 2020"
    assert normalise_wine_name("Tignanello\t2019") == "tignanello 2019"


def test_extract_vintage() -> None:
    assert extract_vintage("Castello di Ama Chianti Classico 2020") == 2020
    assert extract_vintage("Tignanello") is None
    assert extract_vintage("Vintage 1899") is None  # out of range
    assert extract_vintage("Some Wine 2025 Reserve") == 2025
