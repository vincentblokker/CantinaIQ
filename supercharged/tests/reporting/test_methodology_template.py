from datetime import UTC, datetime
from pathlib import Path

from cantinaiq.reporting.renderer import render_report
from cantinaiq.runlog.schema import RunBundle, StageRunLog

TEMPLATES = Path("reports/templates")


def test_methodology_template_renders(tmp_path: Path) -> None:
    bundle = RunBundle(
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
                custom={"sheets_read": ["Italy"]},
            ),
            "cleaning": StageRunLog(
                stage="cleaning",
                started_at=datetime(2026, 5, 16, 0, 1, tzinfo=UTC),
                finished_at=datetime(2026, 5, 16, 0, 2, tzinfo=UTC),
                pre_rows=47291,
                post_rows=9847,
                drops={"non_italian": 35248},
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
            ),
            "scoring": StageRunLog(
                stage="scoring",
                started_at=datetime(2026, 5, 16, 0, 3, tzinfo=UTC),
                finished_at=datetime(2026, 5, 16, 0, 4, tzinfo=UTC),
                pre_rows=9847,
                post_rows=9693,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
                custom={"m_used": 100, "m_strategy": "manual", "global_mean_rating": 4.05},
            ),
        },
        pipeline_config={},
        cli_args=[],
        git_sha=None,
        python_version="3.13.0",
        package_version="0.1.0",
    )
    out = render_report(
        template_name="methodology.md.j2",
        bundle=bundle,
        templates_dir=TEMPLATES,
        out_path=tmp_path / "methodology.md",
    )
    text = out.read_text()
    assert "47,291" in text
    assert "9,847" in text
    assert "100" in text  # m_used
    assert "4.05" in text  # global_mean_rating
