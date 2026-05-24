from pathlib import Path

from cantinaiq.reporting.charts import (
    confidence_donut,
    coverage_bars,
    drop_cascade_waterfall,
    rating_distribution_histogram,
)


def test_drop_cascade_waterfall_writes_svg(tmp_path: Path) -> None:
    cascade = [
        {"stage": "ingestion", "post_rows": 47291},
        {"stage": "cleaning", "post_rows": 9847},
        {"stage": "validation", "post_rows": 9841},
        {"stage": "scoring", "post_rows": 9693},
    ]
    path = drop_cascade_waterfall(cascade, config_hash="abc12345", out_dir=tmp_path)
    assert path.exists()
    assert path.suffix == ".svg"
    content = path.read_text()
    assert "47,291" in content  # data label baked into SVG text


def test_rating_distribution_writes_svg(tmp_path: Path) -> None:
    pre = [4.5, 4.4, 4.2, 4.0, 3.9]
    post = [4.3, 4.3, 4.2, 4.1, 4.0]
    out = rating_distribution_histogram(pre, post, config_hash="abc12345", out_dir=tmp_path)
    assert out.exists()


def test_confidence_donut_writes_svg(tmp_path: Path) -> None:
    counts = {"High": 4000, "Medium": 3000, "Low": 1500, "None": 500}
    out = confidence_donut(counts, config_hash="abc12345", out_dir=tmp_path)
    assert out.exists()


def test_coverage_bars_writes_svg(tmp_path: Path) -> None:
    rows = [
        {"macro_region": "Toscana", "coverage": 0.92},
        {"macro_region": "Piemonte", "coverage": 0.88},
        {"macro_region": "Sicilia", "coverage": 0.70},
    ]
    out = coverage_bars(rows, config_hash="abc12345", out_dir=tmp_path)
    assert out.exists()
