"""Build a Jinja2 context object from a RunBundle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cantinaiq.runlog.schema import RunBundle


@dataclass
class CascadeRow:
    stage: str
    pre_rows: int
    post_rows: int
    removed: int
    pct: float
    top_reason: str
    top_reason_count: int


def build_drop_cascade(bundle: RunBundle) -> list[CascadeRow]:
    rows: list[CascadeRow] = []
    prev = 0
    for name in ("ingestion", "cleaning", "validation", "enrichment", "scoring", "export"):
        s = bundle.stages.get(name)
        if s is None:
            continue
        pre = s.pre_rows if s.pre_rows else prev
        post = s.post_rows
        removed = max(pre - post, 0)
        pct = (removed / pre * 100) if pre else 0.0
        if s.drops:
            top_reason, top_reason_count = max(s.drops.items(), key=lambda kv: kv[1])
        else:
            top_reason, top_reason_count = "(none)", 0
        rows.append(
            CascadeRow(
                stage=name,
                pre_rows=pre,
                post_rows=post,
                removed=removed,
                pct=pct,
                top_reason=top_reason,
                top_reason_count=top_reason_count,
            )
        )
        prev = post
    return rows


def build_context(bundle: RunBundle) -> dict[str, Any]:
    config_hash = (
        bundle.stages[next(iter(bundle.stages))].config_hash if bundle.stages else "unknown"
    )
    return {
        "run": bundle,
        "drop_cascade": build_drop_cascade(bundle),
        "metadata_footer": (
            f"Config hash {config_hash} · run {bundle.run_id} · cantinaiq {bundle.package_version}"
        )
        if bundle.stages
        else "",
    }
