from pathlib import Path

import pytest
from typer.testing import CliRunner

from cantinaiq.cli import app

runner = CliRunner()


def test_version() -> None:
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert res.stdout.strip() == "0.1.0"


def test_run_help_lists_stages() -> None:
    res = runner.invoke(app, ["run", "--help"])
    assert res.exit_code == 0
    assert "ingestion" in res.stdout
    assert "cleaning" in res.stdout


def test_status_when_no_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "runs").mkdir(parents=True)
    res = runner.invoke(app, ["status"])
    assert res.exit_code == 0
    assert "No runs" in res.stdout


def test_top_level_help() -> None:
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "run" in res.stdout
    assert "status" in res.stdout
    assert "version" in res.stdout
