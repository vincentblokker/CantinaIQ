from datetime import UTC, datetime
from pathlib import Path

from cantinaiq.reporting.renderer import render_report
from cantinaiq.runlog.schema import RunBundle, StageRunLog

TEMPLATES = Path("reports/templates")


def _bundle() -> RunBundle:
    return RunBundle(
        run_id="2026-05-16T00-00__abc12345",
        started_at=datetime(2026, 5, 16, 0, 0, tzinfo=UTC),
        finished_at=datetime(2026, 5, 16, 0, 5, tzinfo=UTC),
        stages={
            "ingestion": StageRunLog(
                stage="ingestion",
                started_at=datetime(2026, 5, 16, 0, 0, tzinfo=UTC),
                finished_at=datetime(2026, 5, 16, 0, 1, tzinfo=UTC),
                pre_rows=0,
                post_rows=47291,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
            ),
            "cleaning": StageRunLog(
                stage="cleaning",
                started_at=datetime(2026, 5, 16, 0, 1, tzinfo=UTC),
                finished_at=datetime(2026, 5, 16, 0, 2, tzinfo=UTC),
                pre_rows=47291,
                post_rows=9847,
                drops={"non_italian": 35248, "duplicate": 2196},
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
            ),
        },
        pipeline_config={},
        cli_args=[],
        git_sha=None,
        python_version="3.13.0",
        package_version="0.1.0",
    )


def test_data_quality_report_renders(tmp_path: Path) -> None:
    bundle = _bundle()
    out = render_report(
        template_name="data-quality.md.j2",
        bundle=bundle,
        templates_dir=TEMPLATES,
        out_path=tmp_path / "data-quality.md",
        figures_dir=tmp_path / "figures",
    )
    assert out.exists()
    text = out.read_text()
    assert "47,291" in text
    assert "9,847" in text
    assert "non_italian" in text
