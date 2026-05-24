from pathlib import Path

from cantinaiq.reporting.charts import drop_cascade_waterfall


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
