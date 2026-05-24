"""Pydantic schema for run-log JSONs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StageRunLog(BaseModel):
    stage: str
    started_at: datetime
    finished_at: datetime
    pre_rows: int = 0
    post_rows: int = 0
    drops: dict[str, int] = Field(default_factory=dict)
    drop_samples: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    schema_failures: dict[str, int] | None = None
    custom: dict[str, Any] = Field(default_factory=dict)
    config_hash: str
    config_snapshot_ref: str
    error: dict[str, Any] | None = None


class RunBundle(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: datetime
    stages: dict[str, StageRunLog]
    pipeline_config: dict[str, Any]
    cli_args: list[str]
    git_sha: str | None
    python_version: str
    package_version: str
