"""Render Jinja2 markdown templates against a RunBundle."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from cantinaiq.reporting.context import build_context
from cantinaiq.runlog.schema import RunBundle


def _env(templates_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["thousands"] = lambda v: f"{int(v):,}"
    env.filters["pct"] = lambda v, prec=1: f"{v:.{prec}f}%"
    return env


def render_report(
    template_name: str,
    bundle: RunBundle,
    templates_dir: Path,
    out_path: Path,
    figures_dir: Path | None = None,
) -> Path:
    env = _env(templates_dir)
    template = env.get_template(template_name)
    ctx = build_context(bundle)
    ctx["figures_dir"] = str(figures_dir) if figures_dir else ""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template.render(**ctx))
    return out_path
