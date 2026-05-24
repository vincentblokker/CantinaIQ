"""Hydra ↔ Pydantic config bridge + snapshot persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from omegaconf import DictConfig, OmegaConf

from cantinaiq.config.models import PipelineConfig


def config_from_dict(data: dict[str, Any]) -> PipelineConfig:
    return PipelineConfig(**data)


def config_from_omegaconf(cfg: DictConfig | dict[str, Any]) -> PipelineConfig:
    container: Any = (
        OmegaConf.to_container(cfg, resolve=True) if isinstance(cfg, DictConfig) else cfg
    )
    if not isinstance(container, dict):
        raise TypeError(f"Expected dict from OmegaConf, got {type(container).__name__}")
    return config_from_dict(container)


def snapshot_config(cfg: PipelineConfig, snapshots_dir: Path) -> Path:
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    target = snapshots_dir / f"{cfg.hash}.yaml"
    if target.exists():
        return target
    payload = cfg.model_dump(mode="json")
    target.write_text(yaml.safe_dump(payload, sort_keys=True))
    return target
