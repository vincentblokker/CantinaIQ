"""Stage registry and CLI helpers."""

from __future__ import annotations

from collections.abc import Callable

from cantinaiq.config.models import PipelineConfig

StageFn = Callable[[PipelineConfig, str], object]
STAGES: dict[str, StageFn] = {}


def register_stage(name: str) -> Callable[[StageFn], StageFn]:
    def decorator(fn: StageFn) -> StageFn:
        STAGES[name] = fn
        return fn

    return decorator


_ORDER = ["ingestion", "cleaning", "validation", "enrichment", "scoring", "export"]


def get_stage_order() -> list[str]:
    return list(_ORDER)


def resolve_stage_subset(*, start: str | None = None, only: str | None = None) -> list[str]:
    if only is not None:
        if only not in _ORDER:
            raise ValueError(f"Unknown stage: {only}")
        return [only]
    if start is not None:
        if start not in _ORDER:
            raise ValueError(f"Unknown stage: {start}")
        return _ORDER[_ORDER.index(start) :]
    return list(_ORDER)
