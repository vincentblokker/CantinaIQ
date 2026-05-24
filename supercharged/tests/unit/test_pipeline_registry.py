import pytest

from cantinaiq.pipeline import get_stage_order, resolve_stage_subset


def test_stages_are_ordered() -> None:
    order = get_stage_order()
    assert order == [
        "ingestion",
        "cleaning",
        "validation",
        "enrichment",
        "scoring",
        "export",
    ]


def test_resolve_subset_from_stage() -> None:
    assert resolve_stage_subset(start="scoring") == ["scoring", "export"]


def test_resolve_subset_only_one() -> None:
    assert resolve_stage_subset(only="cleaning") == ["cleaning"]


def test_resolve_subset_invalid_raises() -> None:
    with pytest.raises(ValueError):
        resolve_stage_subset(start="not-a-stage")
