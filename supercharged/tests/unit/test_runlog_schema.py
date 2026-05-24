from datetime import UTC, datetime

from cantinaiq.runlog.schema import RunBundle, StageRunLog


def test_stage_runlog_roundtrip() -> None:
    log = StageRunLog(
        stage="cleaning",
        started_at=datetime(2026, 5, 15, 14, 22, tzinfo=UTC),
        finished_at=datetime(2026, 5, 15, 14, 23, tzinfo=UTC),
        pre_rows=47291,
        post_rows=9847,
        drops={"non_italian": 35248, "missing_price": 412},
        drop_samples={"non_italian": [{"wine_name": "Tempranillo Reserva"}]},
        schema_failures=None,
        custom={"it_filter_kept": 9847},
        config_hash="a3f8e1",
        config_snapshot_ref="config/snapshots/a3f8e1.yaml",
    )
    j = log.model_dump_json()
    restored = StageRunLog.model_validate_json(j)
    assert restored.post_rows == 9847
    assert restored.drops["non_italian"] == 35248


def test_run_bundle_minimum() -> None:
    bundle = RunBundle(
        run_id="2026-05-15T14-22__a3f8e1",
        started_at=datetime(2026, 5, 15, 14, 22, tzinfo=UTC),
        finished_at=datetime(2026, 5, 15, 14, 25, tzinfo=UTC),
        stages={},
        pipeline_config={},
        cli_args=["run", "all"],
        git_sha=None,
        python_version="3.13.0",
        package_version="0.1.0",
    )
    assert bundle.run_id.startswith("2026-05-15")
