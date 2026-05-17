# CantinaIQ Data Pipeline (Sub-Project A) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, reproducible data pipeline that turns `data/raw/Vivino-export.xlsx` into validated/enriched/scored Parquet datasets, JSON exports, and instrumented markdown reports — at HBO/academic quality.

**Architecture:** Linear stage pipeline (ingestion → cleaning → validation → enrichment → scoring → export → reporting), each stage a pure function of (input parquet, config) → (output parquet, run-log JSON). Config is Pydantic-validated YAML composed by Hydra; CLI is Typer; testing is Pytest + Hypothesis + Pandera dual-use.

**Tech Stack:** Python 3.13, Polars 1.x, DuckDB 1.x, Pandera 0.20+, Hydra 1.3+, Pydantic 2.x, Typer 0.12+, Jinja2, Matplotlib, uv, Ruff, mypy, Pytest, Hypothesis.

**Spec reference:** `docs/superpowers/specs/2026-05-15-cantinaiq-data-pipeline-design.md`

---

## Phase 0 — Project bootstrap

### Task 0.1: Initialise pyproject.toml + uv

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `uv.lock` (generated)

- [ ] **Step 1: Write `.python-version`**

```
3.13
```

- [ ] **Step 2: Write `pyproject.toml`**

```toml
[project]
name = "cantinaiq"
version = "0.1.0"
description = "Slurpini Partner Intelligence Engine — data pipeline"
requires-python = ">=3.13,<3.14"
readme = "README.md"
authors = [{ name = "Vincent Blokker" }]
dependencies = [
    "polars>=1.0,<2",
    "duckdb>=1.0,<2",
    "pandera[polars]>=0.20,<0.30",
    "hydra-core>=1.3,<2",
    "omegaconf>=2.3,<3",
    "pydantic>=2.7,<3",
    "typer>=0.12,<1",
    "jinja2>=3.1,<4",
    "matplotlib>=3.8,<4",
    "anthropic>=0.40,<1",
    "python-dotenv>=1.0,<2",
    "fastexcel>=0.10",
    "rich>=13",
]

[project.scripts]
cantinaiq = "cantinaiq.cli:app"

[dependency-groups]
dev = [
    "pytest>=8,<9",
    "pytest-cov>=5,<6",
    "hypothesis>=6.100,<7",
    "ruff>=0.6,<1",
    "mypy>=1.10,<2",
    "openpyxl>=3.1",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/cantinaiq"]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N", "SIM", "TID"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.13"
strict = true
warn_unused_configs = true
disallow_untyped_defs = true
no_implicit_optional = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = ["hydra.*", "omegaconf.*", "matplotlib.*", "fastexcel.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
markers = [
    "slow: long-running tests",
    "llm: tests that would call LLM (must be cache-hit only)",
]

[tool.coverage.run]
source = ["src/cantinaiq"]
branch = true

[tool.coverage.report]
exclude_lines = ["pragma: no cover", "raise NotImplementedError", "if TYPE_CHECKING:"]
```

- [ ] **Step 3: Run `uv sync` to generate lockfile**

```bash
uv sync
```

Expected: creates `.venv/`, installs all deps, writes `uv.lock`.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock .python-version
git commit -m "chore: scaffold pyproject.toml with uv-managed deps"
```

---

### Task 0.2: Create src-layout package skeleton

**Files:**
- Create: `src/cantinaiq/__init__.py`
- Create: `src/cantinaiq/cli.py` (placeholder)
- Create: `src/cantinaiq/config/__init__.py`
- Create: `src/cantinaiq/runlog/__init__.py`
- Create: `src/cantinaiq/ingestion/__init__.py`
- Create: `src/cantinaiq/cleaning/__init__.py`
- Create: `src/cantinaiq/validation/__init__.py`
- Create: `src/cantinaiq/enrichment/__init__.py`
- Create: `src/cantinaiq/scoring/__init__.py`
- Create: `src/cantinaiq/export/__init__.py`
- Create: `src/cantinaiq/reporting/__init__.py`

- [ ] **Step 1: Write `src/cantinaiq/__init__.py`**

```python
__version__ = "0.1.0"
```

- [ ] **Step 2: Write a placeholder `src/cantinaiq/cli.py`**

```python
import typer

app = typer.Typer(no_args_is_help=True, help="CantinaIQ pipeline CLI.")


@app.command()
def version() -> None:
    """Print the package version."""
    from cantinaiq import __version__
    typer.echo(__version__)
```

- [ ] **Step 3: Write empty `__init__.py` for every subpackage above**

Each contains: `"""Stage package."""`

- [ ] **Step 4: Verify the CLI is wired**

```bash
uv run cantinaiq version
```

Expected: prints `0.1.0`.

- [ ] **Step 5: Commit**

```bash
git add src/
git commit -m "chore: scaffold cantinaiq package with empty stage modules"
```

---

### Task 0.3: Configure linting/typing/test runner

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `.gitignore` (extend)

- [ ] **Step 1: Extend `.gitignore`**

Append:

```
.venv/
.coverage
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
data/runs/
data/interim/
data/processed/
data/exports/
!data/raw/.gitkeep
!data/reference/.gitkeep
.env
```

- [ ] **Step 2: Write `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy src/
      - run: uv run pytest --cov=src/cantinaiq --cov-report=term --cov-fail-under=85
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore .github/workflows/ci.yml
git commit -m "ci: add ruff/mypy/pytest workflow with coverage gate"
```

---

### Task 0.4: Reorganise data directory

**Files:**
- Move: `Upload/Vivino-export.xlsx` → `data/raw/Vivino-export.xlsx`
- Move: `Upload/Pyton-script.docx` → `data/raw/Pyton-script.docx`
- Create: `data/raw/.gitkeep`, `data/reference/.gitkeep`

- [ ] **Step 1: Create data subdirs**

```bash
mkdir -p data/raw data/reference data/interim data/processed data/exports data/runs
touch data/raw/.gitkeep data/reference/.gitkeep
```

- [ ] **Step 2: Move source files**

```bash
git mv Upload/Vivino-export.xlsx data/raw/Vivino-export.xlsx
git mv Upload/Pyton-script.docx data/raw/Pyton-script.docx
rmdir Upload
```

- [ ] **Step 3: Commit**

```bash
git add data/raw/.gitkeep data/reference/.gitkeep
git commit -m "chore: reorganise data/ tree, move raw sources from Upload/"
```

---

## Phase 1 — Config infrastructure

### Task 1.1: Pydantic config models (without hash yet)

**Files:**
- Create: `src/cantinaiq/config/models.py`
- Create: `tests/unit/test_config_models.py`

- [ ] **Step 1: Write failing test `tests/unit/test_config_models.py`**

```python
import pytest
from pydantic import ValidationError
from cantinaiq.config.models import (
    PipelineConfig,
    ScoringWeights,
    ScoringConfig,
    CleaningConfig,
    EnrichmentConfig,
    SegmentsConfig,
    PathsConfig,
    PriceSegments,
    ConfidenceSegments,
)


def _valid_weights() -> ScoringWeights:
    return ScoringWeights(
        weighted_rating=0.35,
        market_confidence=0.20,
        value_for_money=0.20,
        premium_fit=0.15,
        portfolio_opportunity=0.10,
    )


def test_scoring_weights_must_sum_to_one():
    with pytest.raises(ValidationError) as exc:
        ScoringWeights(
            weighted_rating=0.5,
            market_confidence=0.2,
            value_for_money=0.2,
            premium_fit=0.2,
            portfolio_opportunity=0.2,
        )
    assert "sum to 1.0" in str(exc.value)


def test_scoring_weights_valid_baseline():
    w = _valid_weights()
    assert w.weighted_rating == 0.35


def test_scoring_config_requires_positive_m():
    with pytest.raises(ValidationError):
        ScoringConfig(bayesian_m=0, weights=_valid_weights())


def test_price_segments_ordering():
    seg = PriceSegments(entry_max=15, accessible_premium_max=30, premium_max=75)
    assert seg.entry_max < seg.accessible_premium_max < seg.premium_max


def test_pipeline_config_constructs():
    cfg = PipelineConfig(
        cleaning=CleaningConfig(),
        enrichment=EnrichmentConfig(),
        scoring=ScoringConfig(bayesian_m=100, weights=_valid_weights()),
        segments=SegmentsConfig(),
        paths=PathsConfig(),
    )
    assert cfg.scoring.bayesian_m == 100
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_config_models.py -v
```

Expected: ImportError (module not found).

- [ ] **Step 3: Write `src/cantinaiq/config/models.py`**

```python
"""Pydantic config schema for the CantinaIQ pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ScoringWeights(BaseModel):
    weighted_rating: float = Field(ge=0, le=1)
    market_confidence: float = Field(ge=0, le=1)
    value_for_money: float = Field(ge=0, le=1)
    premium_fit: float = Field(ge=0, le=1)
    portfolio_opportunity: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _sum_to_one(self) -> ScoringWeights:
        s = (
            self.weighted_rating
            + self.market_confidence
            + self.value_for_money
            + self.premium_fit
            + self.portfolio_opportunity
        )
        if not 0.999 <= s <= 1.001:
            raise ValueError(f"Scoring weights must sum to 1.0, got {s:.4f}")
        return self


class ScoringConfig(BaseModel):
    bayesian_m: int | None = Field(default=None, gt=0, description="Shrinkage threshold; None = auto-median")
    min_reviews_floor: int = Field(default=0, ge=0)
    weights: ScoringWeights
    composite_formula_version: Literal["v1"] = "v1"


class PriceSegments(BaseModel):
    entry_max: float = 15.0
    accessible_premium_max: float = 30.0
    premium_max: float = 75.0


class ConfidenceSegments(BaseModel):
    low_max: int = 50
    emerging_max: int = 250
    reliable_max: int = 1000


class MarketSegmentRules(BaseModel):
    hidden_gem_min_rating: float = 4.2
    premium_icon_min_rating: float = 4.3
    premium_icon_min_price: float = 75.0
    overpriced_max_rating: float = 4.0
    overpriced_min_price: float = 75.0
    low_confidence_review_max: int = 50


class SegmentsConfig(BaseModel):
    prices: PriceSegments = Field(default_factory=PriceSegments)
    confidence: ConfidenceSegments = Field(default_factory=ConfidenceSegments)
    market: MarketSegmentRules = Field(default_factory=MarketSegmentRules)


class CleaningConfig(BaseModel):
    italian_country_token: str = "Italy"
    dedup_keys: list[str] = Field(default_factory=lambda: ["wine_name_normalised", "producer_hint", "vintage"])


class LLMConfig(BaseModel):
    model: str = "claude-haiku-4-5-20251001"
    temperature: float = 0.0
    batch_size: int = 50
    max_retries: int = 3
    cache_path: Path = Path("data/reference/llm_cache.parquet")


class EnrichmentConfig(BaseModel):
    aliases_path: Path = Path("data/reference/producer_aliases.csv")
    macro_regions_path: Path = Path("data/reference/macro_regions.csv")
    known_top50_path: Path = Path("data/reference/known_producers_top50.csv")
    llm: LLMConfig = Field(default_factory=LLMConfig)
    coverage_target_overall: float = 0.80
    coverage_target_per_region: float = 0.70


class PathsConfig(BaseModel):
    raw_dir: Path = Path("data/raw")
    interim_dir: Path = Path("data/interim")
    processed_dir: Path = Path("data/processed")
    exports_dir: Path = Path("data/exports")
    runs_dir: Path = Path("data/runs")
    reference_dir: Path = Path("data/reference")
    snapshots_dir: Path = Path("config/snapshots")
    source_excel: Path = Path("data/raw/Vivino-export.xlsx")


class PipelineConfig(BaseModel):
    cleaning: CleaningConfig
    enrichment: EnrichmentConfig
    scoring: ScoringConfig
    segments: SegmentsConfig
    paths: PathsConfig
```

- [ ] **Step 4: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_config_models.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/cantinaiq/config/models.py tests/unit/test_config_models.py
git commit -m "feat(config): add Pydantic config models with sum-to-one weight invariant"
```

---

### Task 1.2: Config hash + loader

**Files:**
- Modify: `src/cantinaiq/config/models.py` (add `hash`)
- Create: `src/cantinaiq/config/loader.py`
- Create: `tests/unit/test_config_loader.py`

- [ ] **Step 1: Write failing tests `tests/unit/test_config_loader.py`**

```python
from pathlib import Path

import pytest
from omegaconf import OmegaConf

from cantinaiq.config.loader import (
    config_from_dict,
    config_from_omegaconf,
    snapshot_config,
)
from cantinaiq.config.models import PipelineConfig


@pytest.fixture
def baseline_dict() -> dict:
    return {
        "cleaning": {},
        "enrichment": {},
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35,
                "market_confidence": 0.20,
                "value_for_money": 0.20,
                "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
        "segments": {},
        "paths": {},
    }


def test_config_from_dict_constructs(baseline_dict):
    cfg = config_from_dict(baseline_dict)
    assert isinstance(cfg, PipelineConfig)
    assert cfg.scoring.bayesian_m == 100


def test_config_from_omegaconf_resolves(baseline_dict):
    oc = OmegaConf.create(baseline_dict)
    cfg = config_from_omegaconf(oc)
    assert cfg.scoring.weights.weighted_rating == 0.35


def test_config_hash_is_stable(baseline_dict):
    cfg_a = config_from_dict(baseline_dict)
    cfg_b = config_from_dict(baseline_dict)
    assert cfg_a.hash == cfg_b.hash
    assert len(cfg_a.hash) == 8


def test_config_hash_changes_with_weight(baseline_dict):
    cfg_a = config_from_dict(baseline_dict)
    baseline_dict["scoring"]["weights"]["weighted_rating"] = 0.40
    baseline_dict["scoring"]["weights"]["portfolio_opportunity"] = 0.05
    cfg_b = config_from_dict(baseline_dict)
    assert cfg_a.hash != cfg_b.hash


def test_snapshot_writes_yaml(tmp_path: Path, baseline_dict):
    cfg = config_from_dict(baseline_dict)
    snapshot_dir = tmp_path / "snapshots"
    path = snapshot_config(cfg, snapshot_dir)
    assert path.exists()
    assert path.name == f"{cfg.hash}.yaml"
    # Second call must be idempotent (no overwrite, same path).
    path2 = snapshot_config(cfg, snapshot_dir)
    assert path == path2
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
uv run pytest tests/unit/test_config_loader.py -v
```

Expected: ImportError on `cantinaiq.config.loader`.

- [ ] **Step 3: Add `hash` to `PipelineConfig` in `src/cantinaiq/config/models.py`**

Insert before the closing of class `PipelineConfig`:

```python
    @property
    def hash(self) -> str:
        import hashlib
        import json
        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True, default=str).encode()
        return hashlib.sha256(payload).hexdigest()[:8]
```

- [ ] **Step 4: Write `src/cantinaiq/config/loader.py`**

```python
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
    container = OmegaConf.to_container(cfg, resolve=True) if isinstance(cfg, DictConfig) else cfg
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
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_config_loader.py -v
```

Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/config/ tests/unit/test_config_loader.py
git commit -m "feat(config): add deterministic hash, OmegaConf bridge, snapshot writer"
```

---

### Task 1.3: Hydra YAML configs

**Files:**
- Create: `config/pipeline.yaml`
- Create: `config/cleaning/default.yaml`
- Create: `config/enrichment/default.yaml`
- Create: `config/scoring/default.yaml`
- Create: `config/scoring/weights/baseline.yaml`
- Create: `config/scoring/weights/rating-heavy.yaml`
- Create: `config/scoring/weights/value-heavy.yaml`
- Create: `config/segments/default.yaml`
- Create: `config/paths/default.yaml`

- [ ] **Step 1: Write `config/pipeline.yaml`**

```yaml
defaults:
  - cleaning: default
  - enrichment: default
  - scoring: default
  - segments: default
  - paths: default
  - _self_
```

- [ ] **Step 2: Write `config/cleaning/default.yaml`**

```yaml
italian_country_token: Italy
dedup_keys:
  - wine_name_normalised
  - producer_hint
  - vintage
```

- [ ] **Step 3: Write `config/enrichment/default.yaml`**

```yaml
aliases_path: data/reference/producer_aliases.csv
macro_regions_path: data/reference/macro_regions.csv
known_top50_path: data/reference/known_producers_top50.csv
coverage_target_overall: 0.80
coverage_target_per_region: 0.70
llm:
  model: claude-haiku-4-5-20251001
  temperature: 0.0
  batch_size: 50
  max_retries: 3
  cache_path: data/reference/llm_cache.parquet
```

- [ ] **Step 4: Write `config/scoring/default.yaml`**

```yaml
defaults:
  - weights: baseline
  - _self_

bayesian_m: null          # null = auto-median strategy
min_reviews_floor: 0
composite_formula_version: v1
```

- [ ] **Step 5: Write `config/scoring/weights/baseline.yaml`**

```yaml
# @package scoring.weights
weighted_rating: 0.35
market_confidence: 0.20
value_for_money: 0.20
premium_fit: 0.15
portfolio_opportunity: 0.10
```

- [ ] **Step 6: Write `config/scoring/weights/rating-heavy.yaml`**

```yaml
# @package scoring.weights
weighted_rating: 0.50
market_confidence: 0.15
value_for_money: 0.15
premium_fit: 0.15
portfolio_opportunity: 0.05
```

- [ ] **Step 7: Write `config/scoring/weights/value-heavy.yaml`**

```yaml
# @package scoring.weights
weighted_rating: 0.25
market_confidence: 0.15
value_for_money: 0.35
premium_fit: 0.15
portfolio_opportunity: 0.10
```

- [ ] **Step 8: Write `config/segments/default.yaml`**

```yaml
prices:
  entry_max: 15.0
  accessible_premium_max: 30.0
  premium_max: 75.0
confidence:
  low_max: 50
  emerging_max: 250
  reliable_max: 1000
market:
  hidden_gem_min_rating: 4.2
  premium_icon_min_rating: 4.3
  premium_icon_min_price: 75.0
  overpriced_max_rating: 4.0
  overpriced_min_price: 75.0
  low_confidence_review_max: 50
```

- [ ] **Step 9: Write `config/paths/default.yaml`**

```yaml
raw_dir: data/raw
interim_dir: data/interim
processed_dir: data/processed
exports_dir: data/exports
runs_dir: data/runs
reference_dir: data/reference
snapshots_dir: config/snapshots
source_excel: data/raw/Vivino-export.xlsx
```

- [ ] **Step 10: Commit**

```bash
git add config/
git commit -m "feat(config): add Hydra YAML composition with three weight presets"
```

---

### Task 1.4: Hydra loader integration

**Files:**
- Modify: `src/cantinaiq/config/loader.py`
- Create: `tests/integration/test_hydra_loader.py`

- [ ] **Step 1: Write failing integration test**

```python
# tests/integration/test_hydra_loader.py
from pathlib import Path

from hydra import compose, initialize_config_dir

from cantinaiq.config.loader import config_from_omegaconf

REPO = Path(__file__).resolve().parents[2]
CONFIG_DIR = str((REPO / "config").resolve())


def test_baseline_compose():
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        oc = compose(config_name="pipeline")
    cfg = config_from_omegaconf(oc)
    assert cfg.scoring.weights.weighted_rating == 0.35
    assert cfg.scoring.bayesian_m is None


def test_rating_heavy_override():
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        oc = compose(
            config_name="pipeline",
            overrides=["scoring/weights=rating-heavy"],
        )
    cfg = config_from_omegaconf(oc)
    assert cfg.scoring.weights.weighted_rating == 0.50


def test_inline_override():
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        oc = compose(
            config_name="pipeline",
            overrides=["scoring.bayesian_m=250"],
        )
    cfg = config_from_omegaconf(oc)
    assert cfg.scoring.bayesian_m == 250


def test_hash_differs_between_presets():
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        base = config_from_omegaconf(compose(config_name="pipeline"))
        rh = config_from_omegaconf(
            compose(config_name="pipeline", overrides=["scoring/weights=rating-heavy"])
        )
    assert base.hash != rh.hash
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/integration/test_hydra_loader.py -v
```

Expected: failures (Hydra cannot find the `scoring/weights/baseline.yaml` under a non-default package, depending on how `@package` directives compose). Diagnose and fix in next step.

- [ ] **Step 3: Verify config files use the right `@package` markers**

Already done in Task 1.3 (every weights/*.yaml has `# @package scoring.weights`). If failures persist, inspect with:

```bash
uv run python -c "from hydra import compose, initialize_config_dir; \
import json; \
from omegaconf import OmegaConf; \
initialize_config_dir(config_dir='$(pwd)/config', version_base='1.3').__enter__(); \
print(OmegaConf.to_yaml(compose(config_name='pipeline')))"
```

- [ ] **Step 4: Run tests again, verify pass**

```bash
uv run pytest tests/integration/test_hydra_loader.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_hydra_loader.py
git commit -m "test(config): verify Hydra compose + Pydantic bridge + overrides"
```

---

## Phase 2 — Runlog infrastructure

### Task 2.1: RunLog Pydantic schema

**Files:**
- Create: `src/cantinaiq/runlog/schema.py`
- Create: `tests/unit/test_runlog_schema.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_runlog_schema.py
from datetime import datetime, timezone

from cantinaiq.runlog.schema import RunBundle, StageRunLog


def test_stage_runlog_roundtrip():
    log = StageRunLog(
        stage="cleaning",
        started_at=datetime(2026, 5, 15, 14, 22, tzinfo=timezone.utc),
        finished_at=datetime(2026, 5, 15, 14, 23, tzinfo=timezone.utc),
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


def test_run_bundle_minimum():
    bundle = RunBundle(
        run_id="2026-05-15T14-22__a3f8e1",
        started_at=datetime(2026, 5, 15, 14, 22, tzinfo=timezone.utc),
        finished_at=datetime(2026, 5, 15, 14, 25, tzinfo=timezone.utc),
        stages={},
        pipeline_config={},
        cli_args=["run", "all"],
        git_sha=None,
        python_version="3.13.0",
        package_version="0.1.0",
    )
    assert bundle.run_id.startswith("2026-05-15")
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_runlog_schema.py -v
```

Expected: ImportError.

- [ ] **Step 3: Write `src/cantinaiq/runlog/schema.py`**

```python
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
```

- [ ] **Step 4: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_runlog_schema.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add src/cantinaiq/runlog/schema.py tests/unit/test_runlog_schema.py
git commit -m "feat(runlog): add StageRunLog + RunBundle Pydantic schemas"
```

---

### Task 2.2: RunLog.stage context manager

**Files:**
- Create: `src/cantinaiq/runlog/emitter.py`
- Modify: `src/cantinaiq/runlog/__init__.py`
- Create: `tests/unit/test_runlog_emitter.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_runlog_emitter.py
import json
from pathlib import Path

import pytest

from cantinaiq.config.models import PipelineConfig
from cantinaiq.runlog import RunLog


@pytest.fixture
def cfg() -> PipelineConfig:
    from cantinaiq.config.loader import config_from_dict
    return config_from_dict({
        "cleaning": {}, "enrichment": {}, "segments": {}, "paths": {},
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
    })


def test_stage_writes_log_on_success(tmp_path: Path, cfg: PipelineConfig):
    runs_dir = tmp_path / "runs"
    run_id = "2026-05-15T00-00__test01"
    with RunLog.stage("cleaning", run_id, cfg, runs_dir=runs_dir) as log:
        log.pre_rows = 100
        log.post_rows = 80
        log.drops = {"non_italian": 20}
    target = runs_dir / run_id / "stage-cleaning.json"
    assert target.exists()
    payload = json.loads(target.read_text())
    assert payload["post_rows"] == 80
    assert payload["drops"]["non_italian"] == 20
    assert payload["error"] is None


def test_stage_writes_log_on_failure(tmp_path: Path, cfg: PipelineConfig):
    runs_dir = tmp_path / "runs"
    run_id = "2026-05-15T00-00__test02"
    with pytest.raises(RuntimeError):
        with RunLog.stage("cleaning", run_id, cfg, runs_dir=runs_dir) as log:
            log.pre_rows = 100
            raise RuntimeError("boom")
    target = runs_dir / run_id / "stage-cleaning.json"
    assert target.exists()
    payload = json.loads(target.read_text())
    assert payload["error"]["type"] == "RuntimeError"
    assert "boom" in payload["error"]["message"]


def test_atomic_write(tmp_path: Path, cfg: PipelineConfig):
    """Stage log writes to a temp file then renames — no partial files left behind."""
    runs_dir = tmp_path / "runs"
    run_id = "2026-05-15T00-00__test03"
    with RunLog.stage("ingestion", run_id, cfg, runs_dir=runs_dir) as log:
        log.pre_rows = 5
        log.post_rows = 5
    stage_dir = runs_dir / run_id
    leftovers = [p for p in stage_dir.iterdir() if p.suffix == ".tmp"]
    assert leftovers == []
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_runlog_emitter.py -v
```

Expected: ImportError.

- [ ] **Step 3: Write `src/cantinaiq/runlog/emitter.py`**

```python
"""Context-manager emitter for stage run-logs."""

from __future__ import annotations

import os
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from cantinaiq.config.loader import snapshot_config
from cantinaiq.config.models import PipelineConfig
from cantinaiq.runlog.schema import StageRunLog


class RunLog:
    @staticmethod
    @contextmanager
    def stage(
        name: str,
        run_id: str,
        cfg: PipelineConfig,
        runs_dir: Path,
    ) -> Iterator[StageRunLog]:
        runs_dir = Path(runs_dir)
        stage_dir = runs_dir / run_id
        stage_dir.mkdir(parents=True, exist_ok=True)
        snapshots_dir = cfg.paths.snapshots_dir
        snapshot_ref = snapshot_config(cfg, snapshots_dir)
        started = datetime.now(timezone.utc)
        log = StageRunLog(
            stage=name,
            started_at=started,
            finished_at=started,  # placeholder, overwritten on exit
            config_hash=cfg.hash,
            config_snapshot_ref=str(snapshot_ref),
        )
        try:
            yield log
        except BaseException as exc:
            log.error = {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            }
            log.finished_at = datetime.now(timezone.utc)
            _atomic_write_log(log, stage_dir)
            raise
        log.finished_at = datetime.now(timezone.utc)
        _atomic_write_log(log, stage_dir)


def _atomic_write_log(log: StageRunLog, stage_dir: Path) -> None:
    target = stage_dir / f"stage-{log.stage}.json"
    tmp = target.with_suffix(".tmp")
    tmp.write_text(log.model_dump_json(indent=2))
    os.replace(tmp, target)
```

- [ ] **Step 4: Update `src/cantinaiq/runlog/__init__.py`**

```python
"""Run-log infrastructure (instrumentation for every pipeline stage)."""

from cantinaiq.runlog.emitter import RunLog
from cantinaiq.runlog.schema import RunBundle, StageRunLog

__all__ = ["RunLog", "RunBundle", "StageRunLog"]
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_runlog_emitter.py -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/runlog/ tests/unit/test_runlog_emitter.py
git commit -m "feat(runlog): add RunLog.stage context manager with atomic write + exception capture"
```

---

### Task 2.3: RunLog loader (run-dir → RunBundle)

**Files:**
- Create: `src/cantinaiq/runlog/loader.py`
- Modify: `src/cantinaiq/runlog/__init__.py`
- Create: `tests/unit/test_runlog_loader.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_runlog_loader.py
from pathlib import Path

import pytest

from cantinaiq.config.loader import config_from_dict
from cantinaiq.runlog import RunLog, load_run_bundle


@pytest.fixture
def cfg():
    return config_from_dict({
        "cleaning": {}, "enrichment": {}, "segments": {}, "paths": {},
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
    })


def test_load_run_bundle_with_two_stages(tmp_path: Path, cfg):
    runs_dir = tmp_path / "runs"
    run_id = "2026-05-15T00-00__abc123"
    with RunLog.stage("ingestion", run_id, cfg, runs_dir=runs_dir) as log:
        log.pre_rows = 0
        log.post_rows = 100
    with RunLog.stage("cleaning", run_id, cfg, runs_dir=runs_dir) as log:
        log.pre_rows = 100
        log.post_rows = 80
        log.drops = {"non_italian": 20}
    bundle = load_run_bundle(run_id, runs_dir=runs_dir)
    assert set(bundle.stages.keys()) == {"ingestion", "cleaning"}
    assert bundle.stages["cleaning"].drops["non_italian"] == 20


def test_load_run_bundle_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_run_bundle("does-not-exist", runs_dir=tmp_path)


def test_load_latest_run_id(tmp_path: Path, cfg):
    from cantinaiq.runlog.loader import load_latest_run_id
    runs_dir = tmp_path / "runs"
    for run_id in ("2026-05-14T00-00__aaa", "2026-05-15T00-00__bbb"):
        with RunLog.stage("ingestion", run_id, cfg, runs_dir=runs_dir) as log:
            log.post_rows = 1
    latest = load_latest_run_id(runs_dir)
    assert latest == "2026-05-15T00-00__bbb"
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_runlog_loader.py -v
```

Expected: ImportError on `load_run_bundle`.

- [ ] **Step 3: Write `src/cantinaiq/runlog/loader.py`**

```python
"""Load a run directory into a RunBundle."""

from __future__ import annotations

import platform
from datetime import datetime
from pathlib import Path

from cantinaiq import __version__
from cantinaiq.runlog.schema import RunBundle, StageRunLog


def load_run_bundle(run_id: str, runs_dir: Path) -> RunBundle:
    run_dir = Path(runs_dir) / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    stages: dict[str, StageRunLog] = {}
    for stage_file in sorted(run_dir.glob("stage-*.json")):
        log = StageRunLog.model_validate_json(stage_file.read_text())
        stages[log.stage] = log
    if not stages:
        raise FileNotFoundError(f"No stage logs in {run_dir}")
    earliest = min(s.started_at for s in stages.values())
    latest = max(s.finished_at for s in stages.values())
    return RunBundle(
        run_id=run_id,
        started_at=earliest,
        finished_at=latest,
        stages=stages,
        pipeline_config={},
        cli_args=[],
        git_sha=None,
        python_version=platform.python_version(),
        package_version=__version__,
    )


def load_latest_run_id(runs_dir: Path) -> str:
    runs_dir = Path(runs_dir)
    if not runs_dir.exists():
        raise FileNotFoundError(f"Runs dir not found: {runs_dir}")
    candidates = [p for p in runs_dir.iterdir() if p.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No runs in {runs_dir}")
    return sorted(candidates, key=lambda p: p.name)[-1].name
```

- [ ] **Step 4: Update `src/cantinaiq/runlog/__init__.py`**

```python
"""Run-log infrastructure (instrumentation for every pipeline stage)."""

from cantinaiq.runlog.emitter import RunLog
from cantinaiq.runlog.loader import load_latest_run_id, load_run_bundle
from cantinaiq.runlog.schema import RunBundle, StageRunLog

__all__ = ["RunLog", "RunBundle", "StageRunLog", "load_run_bundle", "load_latest_run_id"]
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_runlog_loader.py -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/runlog/loader.py src/cantinaiq/runlog/__init__.py tests/unit/test_runlog_loader.py
git commit -m "feat(runlog): add bundle loader + latest-run resolution"
```

---

## Phase 3 — CLI skeleton + stage registry

### Task 3.1: Stage registry

**Files:**
- Create: `src/cantinaiq/pipeline.py`
- Create: `tests/unit/test_pipeline_registry.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_pipeline_registry.py
import pytest

from cantinaiq.pipeline import STAGES, get_stage_order, resolve_stage_subset


def test_stages_are_ordered():
    order = get_stage_order()
    assert order == ["ingestion", "cleaning", "validation", "enrichment", "scoring", "export"]


def test_resolve_subset_from_stage():
    assert resolve_stage_subset(start="scoring") == ["scoring", "export"]


def test_resolve_subset_only_one():
    assert resolve_stage_subset(only="cleaning") == ["cleaning"]


def test_resolve_subset_invalid_raises():
    with pytest.raises(ValueError):
        resolve_stage_subset(start="not-a-stage")
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_pipeline_registry.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/pipeline.py`**

```python
"""Stage registry and CLI helpers."""

from __future__ import annotations

from typing import Callable

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
        return _ORDER[_ORDER.index(start):]
    return list(_ORDER)
```

- [ ] **Step 4: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_pipeline_registry.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/cantinaiq/pipeline.py tests/unit/test_pipeline_registry.py
git commit -m "feat(pipeline): add stage registry + subset resolution"
```

---

### Task 3.2: Typer CLI with run / status / audit

**Files:**
- Modify: `src/cantinaiq/cli.py`
- Create: `tests/integration/test_cli_smoke.py`

- [ ] **Step 1: Write failing test**

```python
# tests/integration/test_cli_smoke.py
from typer.testing import CliRunner

from cantinaiq.cli import app

runner = CliRunner()


def test_version():
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert res.stdout.strip() == "0.1.0"


def test_run_help_lists_stages():
    res = runner.invoke(app, ["run", "--help"])
    assert res.exit_code == 0
    assert "ingestion" in res.stdout
    assert "cleaning" in res.stdout


def test_status_when_no_runs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "runs").mkdir(parents=True)
    res = runner.invoke(app, ["status"])
    assert res.exit_code == 0
    assert "No runs" in res.stdout
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/integration/test_cli_smoke.py -v
```

- [ ] **Step 3: Rewrite `src/cantinaiq/cli.py`**

```python
"""Typer CLI entrypoint."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import typer
from hydra import compose, initialize_config_dir
from rich.console import Console

from cantinaiq import __version__
from cantinaiq.config.loader import config_from_omegaconf
from cantinaiq.pipeline import STAGES, get_stage_order, resolve_stage_subset

app = typer.Typer(no_args_is_help=True, help="CantinaIQ pipeline CLI.")
run_app = typer.Typer(no_args_is_help=True, help="Run pipeline stages.")
app.add_typer(run_app, name="run")
console = Console()

CONFIG_DIR = str((Path(__file__).resolve().parents[2] / "config").resolve())


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


def _load_cfg(overrides: list[str]):
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        oc = compose(config_name="pipeline", overrides=overrides)
    return config_from_omegaconf(oc)


def _new_run_id(config_hash: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M")
    return f"{ts}__{config_hash}"


def _execute(stages: list[str], overrides: list[str]) -> None:
    cfg = _load_cfg(overrides)
    run_id = _new_run_id(cfg.hash)
    console.print(f"[bold]CantinaIQ run[/bold] {run_id}  config={cfg.hash}")
    for name in stages:
        fn = STAGES.get(name)
        if fn is None:
            raise typer.Exit(code=2)
        console.print(f"  → [cyan]{name}[/cyan]")
        fn(cfg, run_id)


@run_app.command("ingestion")
def run_ingestion(overrides: Annotated[list[str] | None, typer.Argument()] = None) -> None:
    _execute(["ingestion"], overrides or [])


@run_app.command("cleaning")
def run_cleaning(overrides: Annotated[list[str] | None, typer.Argument()] = None) -> None:
    _execute(["cleaning"], overrides or [])


@run_app.command("validation")
def run_validation(overrides: Annotated[list[str] | None, typer.Argument()] = None) -> None:
    _execute(["validation"], overrides or [])


@run_app.command("enrichment")
def run_enrichment(overrides: Annotated[list[str] | None, typer.Argument()] = None) -> None:
    _execute(["enrichment"], overrides or [])


@run_app.command("scoring")
def run_scoring(overrides: Annotated[list[str] | None, typer.Argument()] = None) -> None:
    _execute(["scoring"], overrides or [])


@run_app.command("export")
def run_export(overrides: Annotated[list[str] | None, typer.Argument()] = None) -> None:
    _execute(["export"], overrides or [])


@run_app.command("all")
def run_all(
    from_stage: Annotated[str | None, typer.Option("--from")] = None,
    overrides: Annotated[list[str] | None, typer.Argument()] = None,
) -> None:
    stages = resolve_stage_subset(start=from_stage)
    _execute(stages, overrides or [])


@app.command()
def status() -> None:
    """Print the most recent run summary."""
    from cantinaiq.runlog import load_latest_run_id, load_run_bundle
    runs_dir = Path("data/runs")
    try:
        run_id = load_latest_run_id(runs_dir)
    except FileNotFoundError:
        console.print("[yellow]No runs found.[/yellow]")
        return
    bundle = load_run_bundle(run_id, runs_dir=runs_dir)
    console.print(f"[bold]Latest run:[/bold] {bundle.run_id}")
    for name, s in bundle.stages.items():
        console.print(f"  {name:12}  pre={s.pre_rows:>8}  post={s.post_rows:>8}  "
                      f"dropped={sum(s.drops.values()):>6}  err={'yes' if s.error else 'no'}")


# Side-effect: register stage callables.
from cantinaiq import ingestion, cleaning, validation, enrichment, scoring, export  # noqa: F401,E402


if __name__ == "__main__":  # pragma: no cover
    app()
```

- [ ] **Step 4: Verify imports do not crash even though stage modules are empty**

Confirm each `src/cantinaiq/<stage>/__init__.py` is importable (already done in Task 0.2). The decorator-registry pattern means stages register themselves later when their `__init__.py` imports their `run` module.

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/integration/test_cli_smoke.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/cli.py tests/integration/test_cli_smoke.py
git commit -m "feat(cli): wire Typer commands for run/status with Hydra-loaded config"
```

---

## Phase 4 — Test fixtures + reference data

### Task 4.1: Generate the 50-row Vivino sample fixture

**Files:**
- Create: `tests/fixtures/build_sample.py`
- Create: `tests/fixtures/vivino_sample.xlsx` (generated)
- Create: `tests/conftest.py`

- [ ] **Step 1: Write `tests/fixtures/build_sample.py`**

```python
"""Generate tests/fixtures/vivino_sample.xlsx — a hand-curated 50-row fixture
covering every dirty pattern in the spec §7.2."""

from __future__ import annotations

from pathlib import Path

import openpyxl

HERE = Path(__file__).parent

# Each tuple: (sheet, wine_name, country, region, rating, rating_count, price)
# Patterns documented inline so the fixture is self-explanatory.
ROWS: list[tuple[str, str, str, str, object, object, object]] = [
    # --- 5 whitelist-matchable producers (good case) ---
    ("Italy", "Castello di Ama Chianti Classico 2020", "Italy", "Toscana", 4.4, 1200, 38.0),
    ("Italy", "Tenuta San Guido Sassicaia 2018", "Italy", "Toscana", 4.7, 4500, 280.0),
    ("Italy", "Marchesi Antinori Tignanello 2019", "Italy", "Toscana", 4.6, 5200, 145.0),
    ("Italy", "Gaja Barbaresco 2017", "Italy", "Piemonte", 4.6, 1800, 230.0),
    ("Italy", "Biondi-Santi Brunello di Montalcino 2016", "Italy", "Toscana", 4.5, 900, 220.0),
    # --- 5 pass-1 misses, pass-2 LLM-cache should resolve ---
    ("Italy", "Tignanello 2019", "Italy", "Toscana", 4.5, 600, 130.0),
    ("Italy", "Sassicaia 2018", "Italy", "Toscana", 4.7, 4000, 290.0),
    ("Italy", "Solaia 2017", "Italy", "Toscana", 4.6, 800, 260.0),
    ("Italy", "Ornellaia 2018", "Italy", "Toscana", 4.5, 1500, 200.0),
    ("Italy", "Masseto 2017", "Italy", "Toscana", 4.8, 700, 850.0),
    # --- 3 truly ambiguous (no producer signal) ---
    ("Italy", "Rosso di Montalcino 2020", "Italy", "Toscana", 4.0, 250, 22.0),
    ("Italy", "Chianti Classico 2021", "Italy", "Toscana", 3.9, 180, 14.0),
    ("Italy", "Bolgheri Superiore 2018", "Italy", "Toscana", 4.2, 320, 55.0),
    # --- 5 macro-regions coverage ---
    ("Italy", "Vietti Barolo Castiglione 2019", "Italy", "Piemonte", 4.3, 1100, 65.0),
    ("Italy", "Allegrini Amarone della Valpolicella 2017", "Italy", "Veneto", 4.4, 1900, 75.0),
    ("Italy", "Planeta Etna Rosso 2020", "Italy", "Sicilia", 4.1, 450, 28.0),
    ("Italy", "Mastroberardino Taurasi 2016", "Italy", "Campania", 4.2, 380, 42.0),
    ("Italy", "Argiolas Turriga 2018", "Italy", "Sardegna", 4.3, 280, 58.0),
    # --- 10 with varying rating_count for Bayesian-shrinkage tests ---
    ("Italy", "Antica Cantina Test Wine A 2020", "Italy", "Toscana", 4.8, 5, 25.0),
    ("Italy", "Antica Cantina Test Wine B 2020", "Italy", "Toscana", 4.6, 50, 25.0),
    ("Italy", "Antica Cantina Test Wine C 2020", "Italy", "Toscana", 4.4, 500, 25.0),
    ("Italy", "Antica Cantina Test Wine D 2020", "Italy", "Toscana", 4.2, 5000, 25.0),
    ("Italy", "Antica Cantina Test Wine E 2020", "Italy", "Toscana", 4.0, 50000, 25.0),
    ("Italy", "Fattoria Pupille Saffredi 2019", "Italy", "Toscana", 4.4, 320, 78.0),
    ("Italy", "Podere Sapaio Volpolo 2020", "Italy", "Toscana", 4.1, 240, 32.0),
    ("Italy", "Villa Russiz Sauvignon 2021", "Italy", "Friuli-Venezia Giulia", 4.0, 180, 22.0),
    ("Italy", "Conte Vistarino Pernice 2019", "Italy", "Lombardia", 4.3, 110, 48.0),
    ("Italy", "Cascina Fontana Barolo 2018", "Italy", "Piemonte", 4.2, 90, 52.0),
    # --- 3 tuple-string country (dirt) ---
    ("Italy", "Dirty Tuple Wine A 2020", "('Italy',)", "Toscana", 4.0, 100, 20.0),
    ("Italy", "Dirty Tuple Wine B 2020", "('Italy',)", "Piemonte", 4.1, 150, 35.0),
    ("Italy", "Dirty Tuple Wine C 2020", "('Italy',)", "Veneto", 3.9, 220, 18.0),
    # --- 2 encoding-corruption rows ---
    ("Italy", "Encoding Test Wine A 2020", "ItalÃ«", "Toscana", 4.0, 100, 20.0),
    ("Italy", "Encoding Test Wine B 2020", "Italy", "ToscÃ na", 4.0, 100, 20.0),
    # --- 4 duplicates (will collapse to 2 in dedupe) ---
    ("Italy", "Frescobaldi Nipozzano Riserva 2019", "Italy", "Toscana", 4.2, 800, 28.0),
    ("Italy", "Frescobaldi Nipozzano Riserva 2019", "Italy", "Toscana", 4.2, 800, 28.0),
    ("Italy", "Bruno Giacosa Barbaresco 2018", "Italy", "Piemonte", 4.5, 600, 95.0),
    ("Italy", "Bruno Giacosa Barbaresco 2018", "Italy", "Piemonte", 4.5, 600, 95.0),
    # --- 5 non-Italian (must be filtered out post-cleaning) ---
    ("France", "Château Margaux 2015", "France", "Bordeaux", 4.8, 5000, 800.0),
    ("Spain", "Vega Sicilia Único 2010", "Spain", "Ribera del Duero", 4.7, 2000, 450.0),
    ("Argentina", "Catena Zapata Malbec 2019", "Argentina", "Mendoza", 4.3, 3000, 35.0),
    ("Portugal", "Quinta do Crasto Reserva 2018", "Portugal", "Douro", 4.4, 800, 38.0),
    ("USA", "Opus One 2018", "USA", "Napa Valley", 4.7, 4000, 380.0),
    # --- 3 missing price ---
    ("Italy", "Missing Price Wine A 2020", "Italy", "Toscana", 4.0, 100, None),
    ("Italy", "Missing Price Wine B 2020", "Italy", "Piemonte", 4.1, 150, None),
    ("Italy", "Missing Price Wine C 2020", "Italy", "Veneto", 3.9, 220, None),
    # --- 3 zero rating_count (validation failures) ---
    ("Italy", "Zero Reviews Wine A 2020", "Italy", "Toscana", 4.5, 0, 20.0),
    ("Italy", "Zero Reviews Wine B 2020", "Italy", "Toscana", 4.6, 0, 25.0),
    ("Italy", "Zero Reviews Wine C 2020", "Italy", "Toscana", 4.7, 0, 30.0),
    # --- 2 rating > 5 (data error, validation failures) ---
    ("Italy", "Impossible Rating Wine A 2020", "Italy", "Toscana", 5.4, 100, 20.0),
    ("Italy", "Impossible Rating Wine B 2020", "Italy", "Toscana", 5.2, 100, 25.0),
]

HEADERS = ["wine_name", "country", "region", "rating", "rating_count", "price"]


def main() -> None:
    by_sheet: dict[str, list[list[object]]] = {}
    for sheet, *rest in ROWS:
        by_sheet.setdefault(sheet, []).append(list(rest))
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for sheet, rows in by_sheet.items():
        ws = wb.create_sheet(title=sheet)
        ws.append(HEADERS)
        for r in rows:
            ws.append(r)
    out = HERE / "vivino_sample.xlsx"
    wb.save(out)
    print(f"wrote {out} with {sum(len(rs) for rs in by_sheet.values())} rows across {len(by_sheet)} sheets")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Generate the fixture**

```bash
uv run python tests/fixtures/build_sample.py
```

Expected: prints `wrote .../vivino_sample.xlsx with 50 rows across 5 sheets`.

- [ ] **Step 3: Write `tests/conftest.py`**

```python
"""Shared fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_xlsx() -> Path:
    return FIXTURES / "vivino_sample.xlsx"


@pytest.fixture
def baseline_cfg_dict() -> dict:
    return {
        "cleaning": {}, "enrichment": {}, "segments": {}, "paths": {},
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
    }


@pytest.fixture
def baseline_cfg(baseline_cfg_dict):
    from cantinaiq.config.loader import config_from_dict
    return config_from_dict(baseline_cfg_dict)
```

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/build_sample.py tests/fixtures/vivino_sample.xlsx tests/conftest.py
git commit -m "test: generate 50-row hand-curated Vivino sample fixture"
```

---

### Task 4.2: Reference data files

**Files:**
- Create: `data/reference/producer_aliases.csv`
- Create: `data/reference/macro_regions.csv`
- Create: `data/reference/known_producers_top50.csv`

- [ ] **Step 1: Write `data/reference/producer_aliases.csv`**

```csv
pattern,canonical_name,match_type
Castello di Ama,Castello di Ama,prefix
Tenuta San Guido,Tenuta San Guido,prefix
Marchesi Antinori,Marchesi Antinori,prefix
Marchese Antinori,Marchesi Antinori,prefix
Antinori,Marchesi Antinori,prefix
Fattoria Le Pupille,Fattoria Le Pupille,prefix
Fattoria Pupille,Fattoria Le Pupille,prefix
Gaja,Gaja,prefix
Biondi-Santi,Biondi-Santi,prefix
Frescobaldi,Marchesi de' Frescobaldi,prefix
Casanova di Neri,Casanova di Neri,prefix
Vietti,Vietti,prefix
Allegrini,Allegrini,prefix
Planeta,Planeta,prefix
Mastroberardino,Mastroberardino,prefix
Argiolas,Argiolas,prefix
Bruno Giacosa,Bruno Giacosa,prefix
Fontodi,Fontodi,prefix
Tenuta dell'Ornellaia,Tenuta dell'Ornellaia,prefix
Ornellaia,Tenuta dell'Ornellaia,prefix
Tenuta Masseto,Tenuta Masseto,prefix
Masseto,Tenuta Masseto,prefix
Solaia,Marchesi Antinori,prefix
Tignanello,Marchesi Antinori,prefix
Sassicaia,Tenuta San Guido,prefix
```

- [ ] **Step 2: Write `data/reference/macro_regions.csv`**

```csv
region,macro_region
Toscana,Toscana
Tuscany,Toscana
Chianti,Toscana
Chianti Classico,Toscana
Brunello di Montalcino,Toscana
Bolgheri,Toscana
Bolgheri Superiore,Toscana
Maremma Toscana,Toscana
Piemonte,Piemonte
Piedmont,Piemonte
Barolo,Piemonte
Barbaresco,Piemonte
Langhe,Piemonte
Roero,Piemonte
Veneto,Veneto
Amarone della Valpolicella,Veneto
Valpolicella,Veneto
Prosecco,Veneto
Soave,Veneto
Sicilia,Sicilia
Sicily,Sicilia
Etna,Sicilia
Etna Rosso,Sicilia
Etna Bianco,Sicilia
Puglia,Puglia
Apulia,Puglia
Primitivo di Manduria,Puglia
Salice Salentino,Puglia
Campania,Campania
Taurasi,Campania
Greco di Tufo,Campania
Fiano di Avellino,Campania
Friuli-Venezia Giulia,Friuli-Venezia Giulia
Friuli,Friuli-Venezia Giulia
Collio,Friuli-Venezia Giulia
Lombardia,Lombardia
Lombardy,Lombardia
Franciacorta,Lombardia
Oltrepò Pavese,Lombardia
Trentino-Alto Adige,Trentino-Alto Adige
Trentino,Trentino-Alto Adige
Alto Adige,Trentino-Alto Adige
Südtirol,Trentino-Alto Adige
Sardegna,Sardegna
Sardinia,Sardegna
Marche,Marche
Verdicchio,Marche
Abruzzo,Abruzzo
Montepulciano d'Abruzzo,Abruzzo
Umbria,Umbria
Sagrantino di Montefalco,Umbria
Lazio,Lazio
Frascati,Lazio
```

- [ ] **Step 3: Write `data/reference/known_producers_top50.csv`**

```csv
canonical_name,macro_region
Marchesi Antinori,Toscana
Tenuta San Guido,Toscana
Gaja,Piemonte
Biondi-Santi,Toscana
Castello di Ama,Toscana
Fontodi,Toscana
Fattoria Le Pupille,Toscana
Marchesi de' Frescobaldi,Toscana
Casanova di Neri,Toscana
Tenuta dell'Ornellaia,Toscana
Tenuta Masseto,Toscana
Allegrini,Veneto
Bruno Giacosa,Piemonte
Vietti,Piemonte
Conterno,Piemonte
Pio Cesare,Piemonte
Planeta,Sicilia
Donnafugata,Sicilia
Tasca d'Almerita,Sicilia
COS,Sicilia
Mastroberardino,Campania
Feudi di San Gregorio,Campania
Argiolas,Sardegna
Sella & Mosca,Sardegna
Banfi,Toscana
Frescobaldi,Toscana
Ruffino,Toscana
Marchesi Mazzei,Toscana
Querciabella,Toscana
Le Macchiole,Toscana
Tua Rita,Toscana
Felsina,Toscana
Isole e Olena,Toscana
Caparzo,Toscana
Bertani,Veneto
Masi,Veneto
Tedeschi,Veneto
Tommasi,Veneto
Zenato,Veneto
Pieropan,Veneto
Inama,Veneto
Cantina Terlano,Trentino-Alto Adige
J. Hofstätter,Trentino-Alto Adige
Tiefenbrunner,Trentino-Alto Adige
Jermann,Friuli-Venezia Giulia
Livio Felluga,Friuli-Venezia Giulia
Schiopetto,Friuli-Venezia Giulia
Marisa Cuomo,Campania
Umani Ronchi,Marche
Garofoli,Marche
```

- [ ] **Step 4: Commit**

```bash
git add data/reference/
git commit -m "data: seed producer aliases, macro-region map, top-50 reference"
```

---

### Task 4.3: LLM cache fixture

**Files:**
- Create: `tests/fixtures/build_llm_cache.py`
- Create: `tests/fixtures/llm_cache.parquet` (generated)

- [ ] **Step 1: Write `tests/fixtures/build_llm_cache.py`**

```python
"""Pre-populate the LLM cache for the 5 fixture wines that pass-1 misses,
so tests never call the API."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

MODEL = "claude-haiku-4-5-20251001"
HERE = Path(__file__).parent

# (wine_name, region, producer, grape, confidence, reasoning)
SEEDS = [
    ("Tignanello 2019", "Toscana", "Marchesi Antinori", "Sangiovese-Cabernet blend", "High", "Tignanello is Antinori's flagship Super Tuscan"),
    ("Sassicaia 2018", "Toscana", "Tenuta San Guido", "Cabernet Sauvignon-Cabernet Franc", "High", "Sassicaia is produced exclusively by Tenuta San Guido"),
    ("Solaia 2017", "Toscana", "Marchesi Antinori", "Cabernet Sauvignon-Sangiovese", "High", "Solaia is Antinori's iconic Cabernet-dominant Super Tuscan"),
    ("Ornellaia 2018", "Toscana", "Tenuta dell'Ornellaia", "Bordeaux blend", "High", "Ornellaia is the eponymous wine of Tenuta dell'Ornellaia"),
    ("Masseto 2017", "Toscana", "Tenuta Masseto", "Merlot", "High", "Masseto is a 100% Merlot from Tenuta Masseto"),
]


def cache_key(wine: str, region: str) -> str:
    return hashlib.sha256(f"{wine}|{region}|{MODEL}".encode()).hexdigest()


def main() -> None:
    now = datetime.now(timezone.utc)
    rows = []
    for wine, region, producer, grape, conf, reason in SEEDS:
        rows.append({
            "cache_key": cache_key(wine, region),
            "wine_name": wine,
            "region": region,
            "producer": producer,
            "inferred_grape_or_style": grape,
            "confidence": conf,
            "reasoning": reason,
            "model_version": MODEL,
            "created_at": now,
        })
    out = HERE / "llm_cache.parquet"
    pl.DataFrame(rows).write_parquet(out)
    print(f"wrote {out} with {len(rows)} cached entries")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Generate**

```bash
uv run python tests/fixtures/build_llm_cache.py
```

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/build_llm_cache.py tests/fixtures/llm_cache.parquet
git commit -m "test: pre-populate LLM cache fixture for 5 ambiguous fixture wines"
```

---

## Phase 5 — Pandera schemas

### Task 5.1: Cleaned + Enriched + Scored schemas

**Files:**
- Create: `src/cantinaiq/validation/schemas.py`
- Create: `tests/schemas/test_schemas_definition.py`

- [ ] **Step 1: Write failing test**

```python
# tests/schemas/test_schemas_definition.py
import polars as pl
import pytest

from cantinaiq.validation.schemas import (
    CleanedSchema,
    EnrichedSchema,
    ScoredWineSchema,
    ScoredProducerSchema,
    ScoredRegionSchema,
)


def _valid_cleaned_row() -> dict:
    return {
        "wine_name": "Test 2020",
        "wine_name_normalised": "test 2020",
        "country": "Italy",
        "region": "Toscana",
        "rating": 4.2,
        "rating_count": 120,
        "price": 25.0,
        "vintage": 2020,
        "producer_hint": "Test",
        "source_sheet": "Italy",
        "run_config_hash": "a3f8e1c2",
    }


def test_cleaned_schema_accepts_valid_row():
    df = pl.DataFrame([_valid_cleaned_row()])
    CleanedSchema.validate(df, lazy=True)


def test_cleaned_schema_rejects_non_italy():
    bad = _valid_cleaned_row() | {"country": "France"}
    df = pl.DataFrame([bad])
    with pytest.raises(Exception):
        CleanedSchema.validate(df, lazy=True)


def test_cleaned_schema_rejects_rating_above_five():
    bad = _valid_cleaned_row() | {"rating": 5.4}
    df = pl.DataFrame([bad])
    with pytest.raises(Exception):
        CleanedSchema.validate(df, lazy=True)


def test_enriched_schema_accepts_valid_row():
    row = _valid_cleaned_row() | {
        "producer_name": "Test",
        "macro_region": "Toscana",
        "price_segment": "Accessible Premium",
        "confidence_segment": "Emerging Signal",
        "enrichment_confidence": "High",
        "inferred_grape_or_style": "Sangiovese",
    }
    df = pl.DataFrame([row])
    EnrichedSchema.validate(df, lazy=True)


def test_scored_wine_schema_accepts_valid_row():
    row = _valid_cleaned_row() | {
        "producer_name": "Test",
        "macro_region": "Toscana",
        "price_segment": "Accessible Premium",
        "confidence_segment": "Emerging Signal",
        "enrichment_confidence": "High",
        "inferred_grape_or_style": "Sangiovese",
        "weighted_rating": 4.15,
        "value_score": 1.27,
        "composite_score": 0.68,
        "market_segment": "Commercial Value",
    }
    df = pl.DataFrame([row])
    ScoredWineSchema.validate(df, lazy=True)


def test_scored_producer_schema_smoke():
    df = pl.DataFrame([{
        "producer_name": "Test",
        "macro_region": "Toscana",
        "wines_in_dataset": 4,
        "total_reviews": 1200,
        "avg_price": 32.5,
        "weighted_rating": 4.2,
        "value_score": 1.3,
        "composite_score": 0.71,
        "market_segment": "Hidden Gem",
        "recommendation": "Target",
        "run_config_hash": "a3f8e1c2",
    }])
    ScoredProducerSchema.validate(df, lazy=True)


def test_scored_region_schema_smoke():
    df = pl.DataFrame([{
        "region": "Toscana",
        "macro_region": "Toscana",
        "wines_in_dataset": 250,
        "total_reviews": 32000,
        "avg_price": 48.0,
        "weighted_rating": 4.15,
        "value_score": 1.21,
        "low_sample_region": False,
        "run_config_hash": "a3f8e1c2",
    }])
    ScoredRegionSchema.validate(df, lazy=True)
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/schemas/test_schemas_definition.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/validation/schemas.py`**

```python
"""Pandera schemas — used both in the validation stage and in the test suite."""

from __future__ import annotations

import pandera.polars as pa
from pandera.typing.polars import Series


class CleanedSchema(pa.DataFrameModel):
    wine_name: Series[str] = pa.Field(nullable=False, str_length={"min_value": 1})
    wine_name_normalised: Series[str] = pa.Field(nullable=False, str_length={"min_value": 1})
    country: Series[str] = pa.Field(isin=["Italy"])
    region: Series[str] = pa.Field(nullable=False, str_length={"min_value": 1})
    rating: Series[float] = pa.Field(ge=0, le=5)
    rating_count: Series[int] = pa.Field(ge=1)
    price: Series[float] = pa.Field(gt=0)
    vintage: Series[int] = pa.Field(ge=1900, le=2100, nullable=True)
    producer_hint: Series[str] = pa.Field(nullable=True)
    source_sheet: Series[str] = pa.Field(nullable=False)
    run_config_hash: Series[str] = pa.Field(str_length=8)

    class Config:
        strict = True
        coerce = False


class EnrichedSchema(CleanedSchema):
    producer_name: Series[str] = pa.Field(nullable=True)
    macro_region: Series[str] = pa.Field(nullable=False)
    price_segment: Series[str] = pa.Field(isin=["Entry", "Accessible Premium", "Premium", "Prestige"])
    confidence_segment: Series[str] = pa.Field(
        isin=["Low Confidence", "Emerging Signal", "Reliable Signal", "Strong Market Signal"]
    )
    enrichment_confidence: Series[str] = pa.Field(isin=["High", "Medium", "Low", "None"])
    inferred_grape_or_style: Series[str] = pa.Field(nullable=True)


class ScoredWineSchema(EnrichedSchema):
    weighted_rating: Series[float] = pa.Field(ge=0, le=5)
    value_score: Series[float] = pa.Field(gt=0)
    composite_score: Series[float] = pa.Field(ge=0, le=1)
    market_segment: Series[str] = pa.Field(
        isin=["Premium Icon", "Hidden Gem", "Commercial Value", "Low Confidence Niche", "Overpriced Risk"]
    )


class ScoredProducerSchema(pa.DataFrameModel):
    producer_name: Series[str] = pa.Field(nullable=False)
    macro_region: Series[str] = pa.Field(nullable=False)
    wines_in_dataset: Series[int] = pa.Field(ge=1)
    total_reviews: Series[int] = pa.Field(ge=1)
    avg_price: Series[float] = pa.Field(gt=0)
    weighted_rating: Series[float] = pa.Field(ge=0, le=5)
    value_score: Series[float] = pa.Field(gt=0)
    composite_score: Series[float] = pa.Field(ge=0, le=1)
    market_segment: Series[str] = pa.Field(
        isin=["Premium Icon", "Hidden Gem", "Commercial Value", "Low Confidence Niche", "Overpriced Risk"]
    )
    recommendation: Series[str] = pa.Field(
        isin=["Target", "Monitor", "Premium Brand Builder", "Value Opportunity", "Avoid for Now"]
    )
    run_config_hash: Series[str] = pa.Field(str_length=8)

    class Config:
        strict = True
        coerce = False


class ScoredRegionSchema(pa.DataFrameModel):
    region: Series[str] = pa.Field(nullable=False)
    macro_region: Series[str] = pa.Field(nullable=False)
    wines_in_dataset: Series[int] = pa.Field(ge=1)
    total_reviews: Series[int] = pa.Field(ge=1)
    avg_price: Series[float] = pa.Field(gt=0)
    weighted_rating: Series[float] = pa.Field(ge=0, le=5)
    value_score: Series[float] = pa.Field(gt=0)
    low_sample_region: Series[bool]
    run_config_hash: Series[str] = pa.Field(str_length=8)

    class Config:
        strict = True
        coerce = False
```

- [ ] **Step 4: Run tests, verify pass**

```bash
uv run pytest tests/schemas/test_schemas_definition.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/cantinaiq/validation/schemas.py tests/schemas/test_schemas_definition.py
git commit -m "feat(validation): add Pandera schemas for cleaned/enriched/scored shapes"
```

---

## Phase 6 — Ingestion stage

### Task 6.1: Ingestion implementation

**Files:**
- Create: `src/cantinaiq/ingestion/run.py`
- Modify: `src/cantinaiq/ingestion/__init__.py`
- Create: `tests/unit/test_ingestion.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_ingestion.py
from pathlib import Path

import polars as pl
import pytest

from cantinaiq.config.loader import config_from_dict
from cantinaiq.ingestion.run import run_ingestion


@pytest.fixture
def cfg(tmp_path: Path, sample_xlsx: Path):
    return config_from_dict({
        "cleaning": {}, "enrichment": {}, "segments": {},
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
        "paths": {
            "raw_dir": str(tmp_path / "data" / "raw"),
            "interim_dir": str(tmp_path / "data" / "interim"),
            "processed_dir": str(tmp_path / "data" / "processed"),
            "exports_dir": str(tmp_path / "data" / "exports"),
            "runs_dir": str(tmp_path / "data" / "runs"),
            "reference_dir": str(tmp_path / "data" / "reference"),
            "snapshots_dir": str(tmp_path / "config" / "snapshots"),
            "source_excel": str(sample_xlsx),
        },
    })


def test_ingestion_reads_all_sheets(cfg):
    out = run_ingestion(cfg, run_id="2026-05-16T00-00__test01")
    assert out.exists()
    df = pl.read_parquet(out)
    assert df.height == 50  # full fixture row count
    assert "source_sheet" in df.columns
    assert set(df["source_sheet"].unique()) == {"Italy", "France", "Spain", "Argentina", "Portugal", "USA"}
    assert df["run_config_hash"].unique().to_list() == [cfg.hash]
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_ingestion.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/ingestion/run.py`**

```python
"""Ingestion stage: read Excel sheets into a single Parquet."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog


@register_stage("ingestion")
def run_ingestion(cfg: PipelineConfig, run_id: str) -> Path:
    interim = Path(cfg.paths.interim_dir)
    interim.mkdir(parents=True, exist_ok=True)
    out = interim / "01_raw.parquet"
    with RunLog.stage("ingestion", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        sheets = pl.read_excel(cfg.paths.source_excel, sheet_id=0)
        if isinstance(sheets, dict):
            frames = []
            counts: dict[str, int] = {}
            for sheet_name, df in sheets.items():
                df = df.with_columns(pl.lit(sheet_name).alias("source_sheet"))
                counts[sheet_name] = df.height
                frames.append(df)
            combined = pl.concat(frames, how="diagonal_relaxed")
        else:
            combined = sheets.with_columns(pl.lit("default").alias("source_sheet"))
            counts = {"default": combined.height}
        combined = combined.with_columns(pl.lit(cfg.hash).alias("run_config_hash"))
        combined.write_parquet(out)
        log.pre_rows = 0
        log.post_rows = combined.height
        log.custom = {
            "sheets_read": list(counts.keys()),
            "rows_per_sheet": counts,
            "column_inventory": combined.columns,
            "output_path": str(out),
        }
    return out
```

- [ ] **Step 4: Update `src/cantinaiq/ingestion/__init__.py`**

```python
"""Ingestion stage."""

from cantinaiq.ingestion.run import run_ingestion

__all__ = ["run_ingestion"]
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_ingestion.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/ingestion/ tests/unit/test_ingestion.py
git commit -m "feat(ingestion): read all Excel sheets, tag source_sheet, write parquet"
```

---

## Phase 7 — Cleaning stage

### Task 7.1: Cleaning rule primitives

**Files:**
- Create: `src/cantinaiq/cleaning/rules.py`
- Create: `tests/unit/test_cleaning_rules.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_cleaning_rules.py
import polars as pl

from cantinaiq.cleaning.rules import (
    extract_vintage,
    fix_encoding,
    normalise_wine_name,
    parse_tuple_string,
)


def test_parse_tuple_string():
    assert parse_tuple_string("('Italy',)") == "Italy"
    assert parse_tuple_string("Italy") == "Italy"
    assert parse_tuple_string("('Italy', 'IT')") == "Italy"
    assert parse_tuple_string("") == ""


def test_fix_encoding():
    assert fix_encoding("ItalÃ«") == "Italië"
    assert fix_encoding("ToscÃ na") == "Toscàna"
    assert fix_encoding("Italy") == "Italy"


def test_normalise_wine_name():
    assert normalise_wine_name("  Castello di Ama  Chianti 2020 ") == "castello di ama chianti 2020"
    assert normalise_wine_name("Tignanello\t2019") == "tignanello 2019"


def test_extract_vintage():
    assert extract_vintage("Castello di Ama Chianti Classico 2020") == 2020
    assert extract_vintage("Tignanello") is None
    assert extract_vintage("Vintage 1899") is None  # out of range
    assert extract_vintage("Some Wine 2025 Reserve") == 2025
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_cleaning_rules.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/cleaning/rules.py`**

```python
"""Pure helpers for cleaning transformations (no Polars I/O)."""

from __future__ import annotations

import ast
import re

_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")


def parse_tuple_string(value: str) -> str:
    if not value:
        return ""
    s = value.strip()
    if s.startswith("(") and s.endswith(")"):
        try:
            parsed = ast.literal_eval(s)
        except (ValueError, SyntaxError):
            return s
        if isinstance(parsed, tuple) and parsed:
            return str(parsed[0])
    return s


_ENCODING_MAP = {
    "Ã«": "ë",
    "Ã¨": "è",
    "Ã©": "é",
    "Ã ": "à",
    "Ã¹": "ù",
    "Ã²": "ò",
    "Ã³": "ó",
    "Ã¬": "ì",
    "Ã­": "í",
    "Ãª": "ê",
    "Ã®": "î",
    "Ã´": "ô",
    "Ã»": "û",
    "Ã§": "ç",
    "Ã±": "ñ",
}


def fix_encoding(value: str) -> str:
    if not value:
        return value
    out = value
    for bad, good in _ENCODING_MAP.items():
        out = out.replace(bad, good)
    return out


def normalise_wine_name(name: str) -> str:
    if not name:
        return ""
    return " ".join(name.split()).lower()


def extract_vintage(name: str) -> int | None:
    if not name:
        return None
    m = _YEAR_RE.search(name)
    return int(m.group(1)) if m else None
```

- [ ] **Step 4: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_cleaning_rules.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/cantinaiq/cleaning/rules.py tests/unit/test_cleaning_rules.py
git commit -m "feat(cleaning): add rule primitives (tuple parse, encoding fix, normalise, vintage)"
```

---

### Task 7.2: Cleaning stage runner

**Files:**
- Create: `src/cantinaiq/cleaning/run.py`
- Modify: `src/cantinaiq/cleaning/__init__.py`
- Create: `tests/unit/test_cleaning_run.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_cleaning_run.py
from pathlib import Path

import polars as pl
import pytest

from cantinaiq.cleaning.run import run_cleaning
from cantinaiq.config.loader import config_from_dict
from cantinaiq.ingestion.run import run_ingestion
from cantinaiq.validation.schemas import CleanedSchema


@pytest.fixture
def cfg(tmp_path: Path, sample_xlsx: Path):
    return config_from_dict({
        "cleaning": {}, "enrichment": {}, "segments": {},
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
        "paths": {
            "raw_dir": str(tmp_path / "data" / "raw"),
            "interim_dir": str(tmp_path / "data" / "interim"),
            "processed_dir": str(tmp_path / "data" / "processed"),
            "exports_dir": str(tmp_path / "data" / "exports"),
            "runs_dir": str(tmp_path / "data" / "runs"),
            "reference_dir": str(tmp_path / "data" / "reference"),
            "snapshots_dir": str(tmp_path / "config" / "snapshots"),
            "source_excel": str(sample_xlsx),
        },
    })


def test_cleaning_filters_non_italian_and_dedupes(cfg):
    run_id = "2026-05-16T00-00__clean01"
    run_ingestion(cfg, run_id)
    out = run_cleaning(cfg, run_id)
    df = pl.read_parquet(out)
    # All rows must be Italy
    assert df["country"].unique().to_list() == ["Italy"]
    # Tuple-strings parsed
    # Dedupe collapsed 4 duplicate rows into 2
    # We had 45 Italian-source rows + 5 non-Italian + 5 dirty ('Italy',) all marked Italy after parse
    # After cleaning: 50 - 5 non-IT - 2 dedupe-collapse = 43, minus invalid (rating>5 / zero count / missing price are NOT yet filtered here — that's validation)
    # The cleaning stage only does parsing + IT-filter + dedupe.
    assert df.height < 45
    # Conform to CleanedSchema (relaxed: validation stage handles the strict checks)
    assert {"wine_name_normalised", "vintage", "producer_hint", "source_sheet"}.issubset(set(df.columns))


def test_cleaning_writes_runlog(cfg, tmp_path: Path):
    run_id = "2026-05-16T00-00__clean02"
    run_ingestion(cfg, run_id)
    run_cleaning(cfg, run_id)
    log = (Path(cfg.paths.runs_dir) / run_id / "stage-cleaning.json")
    assert log.exists()
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_cleaning_run.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/cleaning/run.py`**

```python
"""Cleaning stage: normalisation, encoding fixes, dedupe, IT filter."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from cantinaiq.cleaning.rules import (
    extract_vintage,
    fix_encoding,
    normalise_wine_name,
    parse_tuple_string,
)
from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog


@register_stage("cleaning")
def run_cleaning(cfg: PipelineConfig, run_id: str) -> Path:
    interim = Path(cfg.paths.interim_dir)
    src = interim / "01_raw.parquet"
    out = interim / "02_cleaned.parquet"
    with RunLog.stage("cleaning", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        df = pl.read_parquet(src)
        pre = df.height
        log.pre_rows = pre
        drops: dict[str, int] = {}
        samples: dict[str, list[dict]] = {}

        # 1. Parse tuple-strings + encoding fix on country/region
        df = df.with_columns([
            pl.col("country").map_elements(lambda s: fix_encoding(parse_tuple_string(s or "")), return_dtype=pl.String),
            pl.col("region").map_elements(lambda s: fix_encoding(parse_tuple_string(s or "")), return_dtype=pl.String),
        ])

        # 2. Numeric coercion (rating, rating_count, price)
        df = df.with_columns([
            pl.col("rating").cast(pl.Float64, strict=False),
            pl.col("rating_count").cast(pl.Int64, strict=False),
            pl.col("price").cast(pl.Float64, strict=False),
        ])

        # 3. Drop rows missing required fields (records the drop reason)
        for col in ("country", "region", "wine_name"):
            before = df.height
            df = df.filter(pl.col(col).is_not_null() & (pl.col(col) != ""))
            removed = before - df.height
            if removed:
                drops[f"missing_{col}"] = drops.get(f"missing_{col}", 0) + removed

        # 4. Country titlecase + strip
        df = df.with_columns(pl.col("country").str.strip_chars().str.to_titlecase())

        # 5. IT filter (after parse + titlecase)
        target = cfg.cleaning.italian_country_token
        before = df.height
        non_it_samples = (
            df.filter(pl.col("country") != target)
              .select(["wine_name", "country"])
              .head(3)
              .to_dicts()
        )
        df = df.filter(pl.col("country") == target)
        non_it = before - df.height
        if non_it:
            drops["non_italian"] = non_it
            samples["non_italian"] = non_it_samples

        # 6. Compute helper columns for dedupe
        df = df.with_columns([
            pl.col("wine_name").map_elements(normalise_wine_name, return_dtype=pl.String).alias("wine_name_normalised"),
            pl.col("wine_name").map_elements(
                lambda n: (n.split()[0] if n else None), return_dtype=pl.String
            ).alias("producer_hint"),
            pl.col("wine_name").map_elements(extract_vintage, return_dtype=pl.Int64).alias("vintage"),
        ])

        # 7. Dedupe on configured keys
        before = df.height
        df = df.unique(subset=cfg.cleaning.dedup_keys, keep="first", maintain_order=True)
        collapsed = before - df.height
        if collapsed:
            drops["duplicate"] = collapsed

        # 8. Stamp config hash
        df = df.with_columns(pl.lit(cfg.hash).alias("run_config_hash"))

        df.write_parquet(out)
        log.post_rows = df.height
        log.drops = drops
        log.drop_samples = samples
        log.custom = {
            "it_filter_kept": df.height,
            "output_path": str(out),
        }
    return out
```

- [ ] **Step 4: Update `src/cantinaiq/cleaning/__init__.py`**

```python
"""Cleaning stage."""

from cantinaiq.cleaning.run import run_cleaning

__all__ = ["run_cleaning"]
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_cleaning_run.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/cleaning/ tests/unit/test_cleaning_run.py
git commit -m "feat(cleaning): IT filter + tuple/encoding parse + dedupe with drop accounting"
```

---

## Phase 8 — Validation stage

### Task 8.1: Validation runner with fail-loud schema check

**Files:**
- Create: `src/cantinaiq/validation/run.py`
- Modify: `src/cantinaiq/validation/__init__.py`
- Create: `tests/unit/test_validation_run.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_validation_run.py
from pathlib import Path

import polars as pl
import pytest

from cantinaiq.config.loader import config_from_dict
from cantinaiq.validation.run import run_validation


@pytest.fixture
def cfg(tmp_path: Path):
    return config_from_dict({
        "cleaning": {}, "enrichment": {}, "segments": {},
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
        "paths": {
            "raw_dir": str(tmp_path / "data" / "raw"),
            "interim_dir": str(tmp_path / "data" / "interim"),
            "processed_dir": str(tmp_path / "data" / "processed"),
            "exports_dir": str(tmp_path / "data" / "exports"),
            "runs_dir": str(tmp_path / "data" / "runs"),
            "reference_dir": str(tmp_path / "data" / "reference"),
            "snapshots_dir": str(tmp_path / "config" / "snapshots"),
            "source_excel": str(tmp_path / "missing.xlsx"),
        },
    })


def _write_input(cfg, rows: list[dict]):
    interim = Path(cfg.paths.interim_dir)
    interim.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(rows).write_parquet(interim / "02_cleaned.parquet")


def _valid_row(**overrides) -> dict:
    row = {
        "wine_name": "Test 2020",
        "wine_name_normalised": "test 2020",
        "country": "Italy",
        "region": "Toscana",
        "rating": 4.2,
        "rating_count": 120,
        "price": 25.0,
        "vintage": 2020,
        "producer_hint": "Test",
        "source_sheet": "Italy",
        "run_config_hash": "a3f8e1c2",
    }
    row.update(overrides)
    return row


def test_validation_passes_for_valid_rows(cfg):
    _write_input(cfg, [_valid_row()])
    out = run_validation(cfg, run_id="2026-05-16T00-00__val01")
    assert out.exists()


def test_validation_fails_loud_for_bad_rating(cfg):
    _write_input(cfg, [_valid_row(), _valid_row(rating=5.4)])
    with pytest.raises(Exception):
        run_validation(cfg, run_id="2026-05-16T00-00__val02")
    failures = Path(cfg.paths.runs_dir) / "2026-05-16T00-00__val02" / "validation-failures.parquet"
    assert failures.exists()
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_validation_run.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/validation/run.py`**

```python
"""Validation stage: Pandera contract check; fail-loud on breach."""

from __future__ import annotations

from pathlib import Path

import pandera as pa
import polars as pl

from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog
from cantinaiq.validation.schemas import CleanedSchema


@register_stage("validation")
def run_validation(cfg: PipelineConfig, run_id: str) -> Path:
    interim = Path(cfg.paths.interim_dir)
    src = interim / "02_cleaned.parquet"
    out = interim / "03_validated.parquet"
    runs_dir = Path(cfg.paths.runs_dir) / run_id
    with RunLog.stage("validation", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        df = pl.read_parquet(src)
        log.pre_rows = df.height
        try:
            CleanedSchema.validate(df, lazy=True)
        except pa.errors.SchemaErrors as exc:
            failures_path = runs_dir / "validation-failures.parquet"
            failures_path.parent.mkdir(parents=True, exist_ok=True)
            failure_cases: pl.DataFrame = pl.from_pandas(exc.failure_cases)
            failure_cases.write_parquet(failures_path)
            counts: dict[str, int] = {}
            for check in failure_cases["check"].to_list():
                counts[str(check)] = counts.get(str(check), 0) + 1
            log.schema_failures = counts
            log.custom = {"failures_path": str(failures_path)}
            raise
        df.write_parquet(out)
        log.post_rows = df.height
        log.custom = {"output_path": str(out)}
    return out
```

- [ ] **Step 4: Update `src/cantinaiq/validation/__init__.py`**

```python
"""Validation stage + Pandera schemas."""

from cantinaiq.validation.run import run_validation
from cantinaiq.validation.schemas import (
    CleanedSchema,
    EnrichedSchema,
    ScoredProducerSchema,
    ScoredRegionSchema,
    ScoredWineSchema,
)

__all__ = [
    "run_validation",
    "CleanedSchema",
    "EnrichedSchema",
    "ScoredWineSchema",
    "ScoredProducerSchema",
    "ScoredRegionSchema",
]
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_validation_run.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/validation/ tests/unit/test_validation_run.py
git commit -m "feat(validation): fail-loud Pandera contract + failure-row capture"
```

---

## Phase 9 — Enrichment stage

### Task 9.1: Producer extraction — pass 1 (rules + aliases)

**Files:**
- Create: `src/cantinaiq/enrichment/producer/__init__.py`
- Create: `src/cantinaiq/enrichment/producer/models.py`
- Create: `src/cantinaiq/enrichment/producer/pass1_rules.py`
- Create: `tests/unit/test_producer_pass1.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_producer_pass1.py
from pathlib import Path

import polars as pl

from cantinaiq.enrichment.producer.pass1_rules import Pass1Extractor

ALIAS_CSV = Path("data/reference/producer_aliases.csv")


def test_alias_match():
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    r = ex.extract("Castello di Ama Chianti Classico 2020", region="Toscana")
    assert r.name == "Castello di Ama"
    assert r.confidence == "High"
    assert r.method.startswith("alias:")


def test_honorific_prefix():
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    r = ex.extract("Podere Sapaio Volpolo 2020", region="Toscana")
    assert r.name == "Podere Sapaio"
    assert r.confidence == "Medium"
    assert r.method == "honorific-prefix"


def test_first_token_with_blacklist():
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    r = ex.extract("Chianti Classico 2021", region="Toscana")
    assert r.confidence == "None"  # first token Chianti is blacklisted


def test_first_token_fallback():
    ex = Pass1Extractor(aliases_path=ALIAS_CSV)
    r = ex.extract("Frescobaldi Nipozzano Riserva 2019", region="Toscana")
    # Frescobaldi is in alias whitelist → High; not first-token fallback
    assert r.confidence == "High"
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_producer_pass1.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/enrichment/producer/models.py`**

```python
"""Producer-extraction data classes."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Confidence = Literal["High", "Medium", "Low", "None"]


class ProducerCandidate(BaseModel):
    name: str | None
    confidence: Confidence
    method: str
    inferred_grape_or_style: str | None = None
```

- [ ] **Step 4: Write `src/cantinaiq/enrichment/producer/pass1_rules.py`**

```python
"""Deterministic producer extraction (alias whitelist + honorifics + fallback)."""

from __future__ import annotations

import csv
from pathlib import Path

from cantinaiq.enrichment.producer.models import ProducerCandidate

HONORIFICS = (
    "Marchese", "Marchesi", "Tenuta", "Fattoria", "Castello",
    "Azienda Agricola", "Cantina", "Podere", "Villa", "Conte",
    "Barone", "Antica", "Antichi", "Vigneti", "Cascina", "Casa",
)

WINE_STYLE_BLACKLIST = {
    "Brunello", "Chianti", "Barolo", "Barbaresco", "Amarone",
    "Prosecco", "Rosso", "Bianco", "Bolgheri", "Etna", "Soave",
    "Valpolicella", "Taurasi", "Sangiovese", "Nebbiolo",
    "Verdicchio", "Montepulciano", "Pinot", "Sauvignon",
    "Cabernet", "Merlot", "Vintage", "Riserva",
}


class Pass1Extractor:
    def __init__(self, aliases_path: Path):
        self._aliases: list[tuple[str, str, str]] = []  # (pattern, canonical, match_type)
        with Path(aliases_path).open() as f:
            for row in csv.DictReader(f):
                self._aliases.append((row["pattern"], row["canonical_name"], row["match_type"]))
        # Longest patterns first so multi-word aliases win.
        self._aliases.sort(key=lambda t: -len(t[0]))

    def extract(self, wine_name: str, region: str | None = None) -> ProducerCandidate:  # noqa: ARG002
        if not wine_name:
            return ProducerCandidate(name=None, confidence="None", method="empty-input")
        for pattern, canonical, match_type in self._aliases:
            if match_type == "prefix" and wine_name.lower().startswith(pattern.lower()):
                return ProducerCandidate(name=canonical, confidence="High", method=f"alias:{canonical}")
            if match_type == "contains" and pattern.lower() in wine_name.lower():
                return ProducerCandidate(name=canonical, confidence="High", method=f"alias-contains:{canonical}")
        for hon in HONORIFICS:
            if wine_name.startswith(hon + " "):
                tokens = wine_name.split()
                producer = " ".join(tokens[:3])
                return ProducerCandidate(name=producer, confidence="Medium", method="honorific-prefix")
        first = wine_name.split()[0] if wine_name.strip() else ""
        if first and first not in WINE_STYLE_BLACKLIST:
            return ProducerCandidate(name=first, confidence="Low", method="first-token")
        return ProducerCandidate(name=None, confidence="None", method="no-match")
```

- [ ] **Step 5: Write `src/cantinaiq/enrichment/producer/__init__.py`**

```python
"""Producer-extraction subsystem."""

from cantinaiq.enrichment.producer.models import ProducerCandidate
from cantinaiq.enrichment.producer.pass1_rules import Pass1Extractor

__all__ = ["Pass1Extractor", "ProducerCandidate"]
```

- [ ] **Step 6: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_producer_pass1.py -v
```

- [ ] **Step 7: Commit**

```bash
git add src/cantinaiq/enrichment/producer/ tests/unit/test_producer_pass1.py
git commit -m "feat(enrichment): pass-1 producer extraction (alias whitelist + honorifics)"
```

---

### Task 9.2: LLM cache + pass 2 (with mocked client)

**Files:**
- Create: `src/cantinaiq/enrichment/producer/cache.py`
- Create: `src/cantinaiq/enrichment/producer/pass2_llm.py`
- Create: `tests/unit/test_producer_cache.py`
- Create: `tests/unit/test_producer_pass2.py`

- [ ] **Step 1: Write failing test for cache**

```python
# tests/unit/test_producer_cache.py
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from cantinaiq.enrichment.producer.cache import LLMCache, cache_key


def test_cache_key_is_stable():
    a = cache_key("Tignanello 2019", "Toscana", "claude-haiku-4-5-20251001")
    b = cache_key("Tignanello 2019", "Toscana", "claude-haiku-4-5-20251001")
    assert a == b
    assert a != cache_key("Sassicaia 2018", "Toscana", "claude-haiku-4-5-20251001")


def test_cache_round_trip(tmp_path: Path):
    path = tmp_path / "cache.parquet"
    cache = LLMCache(path=path, model_version="claude-haiku-4-5-20251001")
    cache.put(
        wine_name="Tignanello 2019",
        region="Toscana",
        producer="Marchesi Antinori",
        inferred_grape_or_style="Sangiovese blend",
        confidence="High",
        reasoning="Tignanello is Antinori's flagship",
    )
    cache.flush()
    cache2 = LLMCache(path=path, model_version="claude-haiku-4-5-20251001")
    hit = cache2.get("Tignanello 2019", "Toscana")
    assert hit is not None
    assert hit["producer"] == "Marchesi Antinori"


def test_cache_miss_on_model_version_change(tmp_path: Path):
    path = tmp_path / "cache.parquet"
    cache = LLMCache(path=path, model_version="model-a")
    cache.put("Wine X 2020", "Toscana", "Producer X", None, "High", "n/a")
    cache.flush()
    cache_b = LLMCache(path=path, model_version="model-b")
    assert cache_b.get("Wine X 2020", "Toscana") is None
```

- [ ] **Step 2: Run, verify it fails**

```bash
uv run pytest tests/unit/test_producer_cache.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/enrichment/producer/cache.py`**

```python
"""Persistent Parquet-backed LLM-call cache."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl


def cache_key(wine_name: str, region: str, model_version: str) -> str:
    payload = f"{wine_name}|{region}|{model_version}".encode()
    return hashlib.sha256(payload).hexdigest()


class LLMCache:
    def __init__(self, path: Path, model_version: str):
        self.path = Path(path)
        self.model_version = model_version
        self._loaded: pl.DataFrame
        self._new_rows: list[dict[str, Any]] = []
        if self.path.exists():
            self._loaded = pl.read_parquet(self.path)
        else:
            self._loaded = pl.DataFrame(schema={
                "cache_key": pl.String,
                "wine_name": pl.String,
                "region": pl.String,
                "producer": pl.String,
                "inferred_grape_or_style": pl.String,
                "confidence": pl.String,
                "reasoning": pl.String,
                "model_version": pl.String,
                "created_at": pl.Datetime("us"),
            })

    def get(self, wine_name: str, region: str) -> dict[str, Any] | None:
        key = cache_key(wine_name, region, self.model_version)
        hits = self._loaded.filter(
            (pl.col("cache_key") == key) & (pl.col("model_version") == self.model_version)
        )
        if hits.height == 0:
            return None
        return hits.head(1).to_dicts()[0]

    def put(
        self,
        wine_name: str,
        region: str,
        producer: str | None,
        inferred_grape_or_style: str | None,
        confidence: str,
        reasoning: str,
    ) -> None:
        self._new_rows.append({
            "cache_key": cache_key(wine_name, region, self.model_version),
            "wine_name": wine_name,
            "region": region,
            "producer": producer,
            "inferred_grape_or_style": inferred_grape_or_style,
            "confidence": confidence,
            "reasoning": reasoning,
            "model_version": self.model_version,
            "created_at": datetime.now(timezone.utc),
        })

    def flush(self) -> None:
        if not self._new_rows:
            return
        new_df = pl.DataFrame(self._new_rows)
        combined = pl.concat([self._loaded, new_df], how="diagonal_relaxed")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        combined.write_parquet(self.path)
        self._loaded = combined
        self._new_rows.clear()
```

- [ ] **Step 4: Run cache test, verify pass**

```bash
uv run pytest tests/unit/test_producer_cache.py -v
```

- [ ] **Step 5: Write failing test for pass-2 with mocked client**

```python
# tests/unit/test_producer_pass2.py
import shutil
from pathlib import Path

import pytest

from cantinaiq.enrichment.producer.cache import LLMCache
from cantinaiq.enrichment.producer.pass2_llm import Pass2Resolver, LLMClient


class _RecordingClient(LLMClient):
    def __init__(self):
        self.calls = 0

    def resolve_batch(self, entries):
        self.calls += 1
        return [
            {"id": e["id"], "producer": "MockProducer", "inferred_grape_or_style": None,
             "confidence": "Medium", "reasoning": "mocked"}
            for e in entries
        ]


def test_pass2_uses_cache_when_available(tmp_path: Path):
    cache_path = tmp_path / "cache.parquet"
    shutil.copy("tests/fixtures/llm_cache.parquet", cache_path)
    client = _RecordingClient()
    resolver = Pass2Resolver(
        cache=LLMCache(path=cache_path, model_version="claude-haiku-4-5-20251001"),
        client=client,
        batch_size=50,
    )
    candidates = resolver.resolve([
        {"id": 1, "wine_name": "Tignanello 2019", "region": "Toscana"},
        {"id": 2, "wine_name": "Sassicaia 2018", "region": "Toscana"},
    ])
    assert client.calls == 0  # all served from cache
    assert candidates[1].name == "Marchesi Antinori"
    assert candidates[2].name == "Tenuta San Guido"


def test_pass2_calls_client_for_misses_then_caches(tmp_path: Path):
    cache_path = tmp_path / "cache.parquet"
    client = _RecordingClient()
    cache = LLMCache(path=cache_path, model_version="claude-haiku-4-5-20251001")
    resolver = Pass2Resolver(cache=cache, client=client, batch_size=50)
    candidates = resolver.resolve([
        {"id": 1, "wine_name": "Unknown Wine 2020", "region": "Toscana"},
    ])
    assert client.calls == 1
    assert candidates[1].name == "MockProducer"
    # Subsequent resolution must be cache-hit only
    client2 = _RecordingClient()
    resolver2 = Pass2Resolver(
        cache=LLMCache(path=cache_path, model_version="claude-haiku-4-5-20251001"),
        client=client2, batch_size=50,
    )
    resolver2.resolve([{"id": 1, "wine_name": "Unknown Wine 2020", "region": "Toscana"}])
    assert client2.calls == 0
```

- [ ] **Step 6: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_producer_pass2.py -v
```

- [ ] **Step 7: Write `src/cantinaiq/enrichment/producer/pass2_llm.py`**

```python
"""Pass-2 LLM disambiguation with cache."""

from __future__ import annotations

import json
import os
from typing import Any, Protocol

from cantinaiq.enrichment.producer.cache import LLMCache
from cantinaiq.enrichment.producer.models import ProducerCandidate


SYSTEM_PROMPT = """You are extracting Italian wine producer names from raw Vivino wine entries.

For each entry, return JSON with:
  - producer: the canonical producer/winery name. Use full Italian honorific
    where standard ("Tenuta San Guido", not "San Guido"). If you are not
    confident the wine name actually contains a producer, return null.
  - inferred_grape_or_style: e.g. "Sangiovese", "Nebbiolo", "Sangiovese-
    dominant blend", or null if uncertain.
  - confidence: "High" | "Medium" | "Low".
  - reasoning: <=15 words.

Rules:
  - Producer != appellation. "Brunello di Montalcino" is an appellation.
  - Producer != wine name. "Sassicaia" is a wine; the producer is "Tenuta San Guido".
  - If no producer signal, return null with confidence "Low".

Return: JSON array of { id, producer, inferred_grape_or_style, confidence, reasoning }."""


class LLMClient(Protocol):
    def resolve_batch(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]: ...


class AnthropicLLMClient:
    def __init__(self, model: str = "claude-haiku-4-5-20251001", temperature: float = 0.0):
        from anthropic import Anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def resolve_batch(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        user_msg = "Entries:\n" + json.dumps(entries, ensure_ascii=False)
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=self.temperature,
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if hasattr(b, "text"))
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1:
            raise ValueError(f"Unexpected LLM output (no JSON array): {text[:200]!r}")
        return json.loads(text[start:end + 1])


class Pass2Resolver:
    def __init__(self, cache: LLMCache, client: LLMClient, batch_size: int = 50):
        self.cache = cache
        self.client = client
        self.batch_size = batch_size

    def resolve(self, entries: list[dict[str, Any]]) -> dict[int, ProducerCandidate]:
        out: dict[int, ProducerCandidate] = {}
        misses: list[dict[str, Any]] = []
        for e in entries:
            hit = self.cache.get(e["wine_name"], e["region"])
            if hit is not None:
                out[e["id"]] = ProducerCandidate(
                    name=hit["producer"],
                    confidence=hit["confidence"],
                    method=f"llm-cache:{hit['confidence']}",
                    inferred_grape_or_style=hit.get("inferred_grape_or_style"),
                )
            else:
                misses.append(e)
        for i in range(0, len(misses), self.batch_size):
            batch = misses[i:i + self.batch_size]
            results = self.client.resolve_batch(batch)
            for entry, res in zip(batch, results, strict=False):
                self.cache.put(
                    wine_name=entry["wine_name"],
                    region=entry["region"],
                    producer=res.get("producer"),
                    inferred_grape_or_style=res.get("inferred_grape_or_style"),
                    confidence=res.get("confidence", "Low"),
                    reasoning=res.get("reasoning", ""),
                )
                out[entry["id"]] = ProducerCandidate(
                    name=res.get("producer"),
                    confidence=res.get("confidence", "Low"),
                    method=f"llm-fresh:{res.get('confidence', 'Low')}",
                    inferred_grape_or_style=res.get("inferred_grape_or_style"),
                )
        self.cache.flush()
        return out
```

- [ ] **Step 8: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_producer_pass2.py -v
```

- [ ] **Step 9: Commit**

```bash
git add src/cantinaiq/enrichment/producer/cache.py src/cantinaiq/enrichment/producer/pass2_llm.py \
        tests/unit/test_producer_cache.py tests/unit/test_producer_pass2.py
git commit -m "feat(enrichment): LLM cache + pass-2 resolver with Anthropic client + mock-friendly Protocol"
```

---

### Task 9.3: Enrichment runner (macro-region + segments + producer)

**Files:**
- Create: `src/cantinaiq/enrichment/run.py`
- Modify: `src/cantinaiq/enrichment/__init__.py`
- Create: `tests/unit/test_enrichment_run.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_enrichment_run.py
from pathlib import Path
import shutil

import polars as pl
import pytest

from cantinaiq.cleaning.run import run_cleaning
from cantinaiq.config.loader import config_from_dict
from cantinaiq.enrichment.run import run_enrichment
from cantinaiq.ingestion.run import run_ingestion
from cantinaiq.validation.run import run_validation
from cantinaiq.validation.schemas import EnrichedSchema


@pytest.fixture
def cfg(tmp_path: Path, sample_xlsx: Path):
    # Copy reference data into tmp_path so paths resolve from there
    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    shutil.copy("data/reference/producer_aliases.csv", ref / "producer_aliases.csv")
    shutil.copy("data/reference/macro_regions.csv", ref / "macro_regions.csv")
    shutil.copy("data/reference/known_producers_top50.csv", ref / "known_producers_top50.csv")
    shutil.copy("tests/fixtures/llm_cache.parquet", ref / "llm_cache.parquet")
    return config_from_dict({
        "cleaning": {}, "segments": {},
        "enrichment": {
            "aliases_path": str(ref / "producer_aliases.csv"),
            "macro_regions_path": str(ref / "macro_regions.csv"),
            "known_top50_path": str(ref / "known_producers_top50.csv"),
            "llm": {"cache_path": str(ref / "llm_cache.parquet")},
        },
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
        "paths": {
            "raw_dir": str(tmp_path / "data" / "raw"),
            "interim_dir": str(tmp_path / "data" / "interim"),
            "processed_dir": str(tmp_path / "data" / "processed"),
            "exports_dir": str(tmp_path / "data" / "exports"),
            "runs_dir": str(tmp_path / "data" / "runs"),
            "reference_dir": str(ref),
            "snapshots_dir": str(tmp_path / "config" / "snapshots"),
            "source_excel": str(sample_xlsx),
        },
    })


def test_enrichment_full_path(cfg):
    run_id = "2026-05-16T00-00__enr01"
    run_ingestion(cfg, run_id)
    run_cleaning(cfg, run_id)
    # The fixture deliberately includes rows that fail validation (rating>5, etc.);
    # filter those out manually to test enrichment in isolation.
    interim = Path(cfg.paths.interim_dir)
    cleaned = pl.read_parquet(interim / "02_cleaned.parquet")
    safe = cleaned.filter(
        (pl.col("rating") <= 5) & (pl.col("rating_count") >= 1) & (pl.col("price") > 0)
    )
    safe.write_parquet(interim / "03_validated.parquet")
    out = run_enrichment(cfg, run_id)
    df = pl.read_parquet(out)
    # All rows should have a price_segment and confidence_segment
    assert df["price_segment"].null_count() == 0
    assert df["confidence_segment"].null_count() == 0
    # Macro-region must be assigned
    assert df["macro_region"].null_count() == 0
    # Producer extraction coverage: most fixture rows should resolve
    high_or_med = df.filter(pl.col("enrichment_confidence").is_in(["High", "Medium"])).height
    assert high_or_med >= df.height * 0.5
    # Pandera schema
    EnrichedSchema.validate(df, lazy=True)
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_enrichment_run.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/enrichment/run.py`**

```python
"""Enrichment stage: macro-region, price/confidence segments, producer extraction."""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any

import polars as pl

from cantinaiq.config.models import PipelineConfig
from cantinaiq.enrichment.producer.cache import LLMCache
from cantinaiq.enrichment.producer.models import ProducerCandidate
from cantinaiq.enrichment.producer.pass1_rules import Pass1Extractor
from cantinaiq.enrichment.producer.pass2_llm import (
    AnthropicLLMClient,
    LLMClient,
    Pass2Resolver,
)
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog


def _load_macro_regions(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with Path(path).open() as f:
        for row in csv.DictReader(f):
            mapping[row["region"].strip().lower()] = row["macro_region"].strip()
    return mapping


def _price_segment(price: float, seg) -> str:
    if price <= seg.prices.entry_max:
        return "Entry"
    if price <= seg.prices.accessible_premium_max:
        return "Accessible Premium"
    if price <= seg.prices.premium_max:
        return "Premium"
    return "Prestige"


def _confidence_segment(count: int, seg) -> str:
    if count < seg.confidence.low_max:
        return "Low Confidence"
    if count < seg.confidence.emerging_max:
        return "Emerging Signal"
    if count < seg.confidence.reliable_max:
        return "Reliable Signal"
    return "Strong Market Signal"


@register_stage("enrichment")
def run_enrichment(
    cfg: PipelineConfig,
    run_id: str,
    llm_client: LLMClient | None = None,
) -> Path:
    interim = Path(cfg.paths.interim_dir)
    processed = Path(cfg.paths.processed_dir)
    processed.mkdir(parents=True, exist_ok=True)
    out = processed / "italian_wines_enriched.parquet"
    src = interim / "03_validated.parquet"
    with RunLog.stage("enrichment", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        df = pl.read_parquet(src)
        log.pre_rows = df.height

        # 1. macro-region lookup
        macro_map = _load_macro_regions(cfg.enrichment.macro_regions_path)
        df = df.with_columns(
            pl.col("region").map_elements(
                lambda r: macro_map.get((r or "").strip().lower(), r),
                return_dtype=pl.String,
            ).alias("macro_region")
        )

        # 2. price segment + confidence segment
        seg = cfg.segments
        df = df.with_columns([
            pl.col("price").map_elements(lambda p: _price_segment(p, seg), return_dtype=pl.String).alias("price_segment"),
            pl.col("rating_count").map_elements(lambda c: _confidence_segment(c, seg), return_dtype=pl.String).alias("confidence_segment"),
        ])

        # 3. Pass-1 producer extraction
        p1 = Pass1Extractor(aliases_path=cfg.enrichment.aliases_path)
        rows = df.select(["wine_name", "region"]).to_dicts()
        pass1_results: list[ProducerCandidate] = [
            p1.extract(r["wine_name"], r.get("region")) for r in rows
        ]

        # 4. Identify pass-2 candidates (confidence Low or None)
        candidates_for_p2 = [
            {"id": i, "wine_name": rows[i]["wine_name"], "region": rows[i]["region"]}
            for i, c in enumerate(pass1_results)
            if c.confidence in ("Low", "None")
        ]
        pass2_results: dict[int, ProducerCandidate] = {}
        llm_new_calls = 0
        if candidates_for_p2:
            client = llm_client or _default_llm_client(cfg)
            cache = LLMCache(
                path=cfg.enrichment.llm.cache_path,
                model_version=cfg.enrichment.llm.model,
            )
            resolver = Pass2Resolver(cache=cache, client=client, batch_size=cfg.enrichment.llm.batch_size)
            pass2_results = resolver.resolve(candidates_for_p2)
            # We cannot easily count fresh calls without instrumenting the client;
            # leave it as 0 for default-client runs and let the recording client in tests inspect.
        merged: list[ProducerCandidate] = []
        for i, c in enumerate(pass1_results):
            if i in pass2_results:
                merged.append(pass2_results[i])
            else:
                merged.append(c)

        producer_df = pl.DataFrame({
            "producer_name": [c.name for c in merged],
            "enrichment_confidence": [c.confidence for c in merged],
            "inferred_grape_or_style": [c.inferred_grape_or_style for c in merged],
        })
        df = pl.concat([df, producer_df], how="horizontal")

        # 5. Coverage report
        total = df.height
        coverage = df.filter(pl.col("enrichment_confidence").is_in(["High", "Medium"])).height
        per_region = (
            df.group_by("macro_region")
              .agg(
                  pl.len().alias("n"),
                  pl.col("enrichment_confidence").is_in(["High", "Medium"]).sum().alias("hi_med"),
              )
              .to_dicts()
        )

        df.write_parquet(out)
        log.post_rows = df.height
        log.custom = {
            "enrichment_coverage_overall": coverage / total if total else 0.0,
            "enrichment_coverage_per_macro_region": {
                r["macro_region"]: (r["hi_med"] / r["n"] if r["n"] else 0.0) for r in per_region
            },
            "pass1_resolved": sum(1 for c in pass1_results if c.confidence in ("High", "Medium")),
            "pass2_invoked_count": len(candidates_for_p2),
            "llm_new_calls": llm_new_calls,
            "output_path": str(out),
        }
    return out


def _default_llm_client(cfg: PipelineConfig) -> LLMClient:
    if os.environ.get("CANTINAIQ_DISABLE_LLM") == "1":
        raise RuntimeError("LLM client disabled and pass-2 candidates remain; populate the cache first.")
    return AnthropicLLMClient(
        model=cfg.enrichment.llm.model,
        temperature=cfg.enrichment.llm.temperature,
    )
```

- [ ] **Step 4: Update `src/cantinaiq/enrichment/__init__.py`**

```python
"""Enrichment stage."""

from cantinaiq.enrichment.run import run_enrichment

__all__ = ["run_enrichment"]
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_enrichment_run.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/enrichment/ tests/unit/test_enrichment_run.py
git commit -m "feat(enrichment): macro-region map + segments + two-pass producer extraction"
```

---

## Phase 10 — Scoring stage

### Task 10.1: Bayesian + value-score math (with Hypothesis)

**Files:**
- Create: `src/cantinaiq/scoring/math.py`
- Create: `tests/properties/test_bayesian_properties.py`
- Create: `tests/properties/test_value_score_properties.py`
- Create: `tests/unit/test_scoring_math.py`

- [ ] **Step 1: Write failing tests `tests/unit/test_scoring_math.py`**

```python
import math

import pytest

from cantinaiq.scoring.math import bayesian_weighted_rating, composite_score, value_score


def test_bayesian_at_zero_reviews_undefined():
    # rating_count must be >= 1; defensive: function should raise on zero
    with pytest.raises(ValueError):
        bayesian_weighted_rating(rating=4.5, rating_count=0, m=100, global_mean=4.0)


def test_bayesian_high_volume_dominates():
    wr = bayesian_weighted_rating(rating=4.5, rating_count=10_000, m=100, global_mean=4.0)
    assert math.isclose(wr, 4.4950495049504955, rel_tol=1e-9)


def test_value_score_simple():
    # weighted_rating / log(price + 1)
    vs = value_score(weighted_rating=4.0, price=10.0)
    assert math.isclose(vs, 4.0 / math.log(11), rel_tol=1e-9)


def test_composite_score_baseline():
    s = composite_score(
        weighted_rating_norm=0.85,
        market_confidence_norm=0.50,
        value_norm=0.70,
        premium_fit_norm=0.60,
        portfolio_opportunity_norm=0.40,
        weights=(0.35, 0.20, 0.20, 0.15, 0.10),
    )
    # 0.85*.35 + 0.50*.20 + 0.70*.20 + 0.60*.15 + 0.40*.10 = 0.6325
    assert math.isclose(s, 0.6325, rel_tol=1e-9)
```

- [ ] **Step 2: Write Hypothesis properties `tests/properties/test_bayesian_properties.py`**

```python
import math

from hypothesis import given, settings
from hypothesis import strategies as st

from cantinaiq.scoring.math import bayesian_weighted_rating


@given(
    rating=st.floats(min_value=0, max_value=5, allow_nan=False, allow_infinity=False),
    rating_count=st.integers(min_value=1, max_value=100_000),
    m=st.integers(min_value=1, max_value=10_000),
    global_mean=st.floats(min_value=3.0, max_value=4.5, allow_nan=False),
)
def test_weighted_rating_is_convex_combination(rating, rating_count, m, global_mean):
    wr = bayesian_weighted_rating(rating, rating_count, m, global_mean)
    lo, hi = min(rating, global_mean), max(rating, global_mean)
    assert lo - 1e-9 <= wr <= hi + 1e-9


@given(
    rating=st.floats(min_value=0, max_value=5, allow_nan=False),
    m=st.integers(min_value=1, max_value=10_000),
    global_mean=st.floats(min_value=3.0, max_value=4.5, allow_nan=False),
)
@settings(max_examples=200)
def test_high_volume_approaches_rating(rating, m, global_mean):
    wr_low = bayesian_weighted_rating(rating, rating_count=1, m=m, global_mean=global_mean)
    wr_high = bayesian_weighted_rating(rating, rating_count=10_000_000, m=m, global_mean=global_mean)
    assert abs(wr_high - rating) <= abs(wr_low - rating) + 1e-9


@given(
    rating=st.floats(min_value=0, max_value=5, allow_nan=False),
    rating_count=st.integers(min_value=1, max_value=100_000),
    global_mean=st.floats(min_value=3.0, max_value=4.5, allow_nan=False),
)
@settings(max_examples=200)
def test_high_m_approaches_global_mean(rating, rating_count, global_mean):
    wr_low_m = bayesian_weighted_rating(rating, rating_count, m=1, global_mean=global_mean)
    wr_high_m = bayesian_weighted_rating(rating, rating_count, m=10_000_000, global_mean=global_mean)
    assert abs(wr_high_m - global_mean) <= abs(wr_low_m - global_mean) + 1e-9
```

- [ ] **Step 3: Write Hypothesis properties `tests/properties/test_value_score_properties.py`**

```python
from hypothesis import given
from hypothesis import strategies as st

from cantinaiq.scoring.math import value_score


@given(
    wr=st.floats(min_value=0.1, max_value=5, allow_nan=False),
    price_low=st.floats(min_value=1.0, max_value=50, allow_nan=False),
    price_high=st.floats(min_value=51, max_value=1000, allow_nan=False),
)
def test_value_decreases_in_price(wr, price_low, price_high):
    assert value_score(wr, price_low) > value_score(wr, price_high)


@given(
    price=st.floats(min_value=1, max_value=1000, allow_nan=False),
    wr_low=st.floats(min_value=0.1, max_value=2.5, allow_nan=False),
    wr_high=st.floats(min_value=2.6, max_value=5, allow_nan=False),
)
def test_value_increases_in_rating(price, wr_low, wr_high):
    assert value_score(wr_high, price) > value_score(wr_low, price)
```

- [ ] **Step 4: Run tests, verify they fail**

```bash
uv run pytest tests/unit/test_scoring_math.py tests/properties/ -v
```

- [ ] **Step 5: Write `src/cantinaiq/scoring/math.py`**

```python
"""Pure scoring functions — no Polars I/O. Targets of Hypothesis property tests."""

from __future__ import annotations

import math


def bayesian_weighted_rating(rating: float, rating_count: int, m: int, global_mean: float) -> float:
    if rating_count < 1:
        raise ValueError(f"rating_count must be >= 1, got {rating_count}")
    n = rating_count
    return (n / (n + m)) * rating + (m / (n + m)) * global_mean


def value_score(weighted_rating: float, price: float) -> float:
    if price <= 0:
        raise ValueError(f"price must be > 0, got {price}")
    return weighted_rating / math.log(price + 1)


def composite_score(
    weighted_rating_norm: float,
    market_confidence_norm: float,
    value_norm: float,
    premium_fit_norm: float,
    portfolio_opportunity_norm: float,
    weights: tuple[float, float, float, float, float],
) -> float:
    w1, w2, w3, w4, w5 = weights
    return (
        weighted_rating_norm * w1
        + market_confidence_norm * w2
        + value_norm * w3
        + premium_fit_norm * w4
        + portfolio_opportunity_norm * w5
    )
```

- [ ] **Step 6: Run all tests, verify pass**

```bash
uv run pytest tests/unit/test_scoring_math.py tests/properties/ -v
```

- [ ] **Step 7: Commit**

```bash
git add src/cantinaiq/scoring/math.py tests/unit/test_scoring_math.py tests/properties/
git commit -m "feat(scoring): Bayesian weighted rating + value score + composite, with Hypothesis properties"
```

---

### Task 10.2: Scoring stage runner

**Files:**
- Create: `src/cantinaiq/scoring/run.py`
- Modify: `src/cantinaiq/scoring/__init__.py`
- Create: `tests/unit/test_scoring_run.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_scoring_run.py
from pathlib import Path
import shutil

import polars as pl
import pytest

from cantinaiq.cleaning.run import run_cleaning
from cantinaiq.config.loader import config_from_dict
from cantinaiq.enrichment.run import run_enrichment
from cantinaiq.ingestion.run import run_ingestion
from cantinaiq.scoring.run import run_scoring
from cantinaiq.validation.schemas import ScoredProducerSchema, ScoredRegionSchema, ScoredWineSchema


@pytest.fixture
def cfg(tmp_path: Path, sample_xlsx: Path):
    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    for f in ("producer_aliases.csv", "macro_regions.csv", "known_producers_top50.csv"):
        shutil.copy(f"data/reference/{f}", ref / f)
    shutil.copy("tests/fixtures/llm_cache.parquet", ref / "llm_cache.parquet")
    return config_from_dict({
        "cleaning": {}, "segments": {},
        "enrichment": {
            "aliases_path": str(ref / "producer_aliases.csv"),
            "macro_regions_path": str(ref / "macro_regions.csv"),
            "known_top50_path": str(ref / "known_producers_top50.csv"),
            "llm": {"cache_path": str(ref / "llm_cache.parquet")},
        },
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
        "paths": {
            "raw_dir": str(tmp_path / "data" / "raw"),
            "interim_dir": str(tmp_path / "data" / "interim"),
            "processed_dir": str(tmp_path / "data" / "processed"),
            "exports_dir": str(tmp_path / "data" / "exports"),
            "runs_dir": str(tmp_path / "data" / "runs"),
            "reference_dir": str(ref),
            "snapshots_dir": str(tmp_path / "config" / "snapshots"),
            "source_excel": str(sample_xlsx),
        },
    })


def test_scoring_produces_three_outputs(cfg):
    run_id = "2026-05-16T00-00__sc01"
    run_ingestion(cfg, run_id)
    run_cleaning(cfg, run_id)
    interim = Path(cfg.paths.interim_dir)
    cleaned = pl.read_parquet(interim / "02_cleaned.parquet")
    safe = cleaned.filter(
        (pl.col("rating") <= 5) & (pl.col("rating_count") >= 1) & (pl.col("price") > 0)
    )
    safe.write_parquet(interim / "03_validated.parquet")
    run_enrichment(cfg, run_id)
    paths = run_scoring(cfg, run_id)
    wines = pl.read_parquet(paths["wines"])
    producers = pl.read_parquet(paths["producers"])
    regions = pl.read_parquet(paths["regions"])
    ScoredWineSchema.validate(wines, lazy=True)
    ScoredProducerSchema.validate(producers, lazy=True)
    ScoredRegionSchema.validate(regions, lazy=True)
    # composite_score in [0, 1]
    assert wines["composite_score"].max() <= 1.0
    assert wines["composite_score"].min() >= 0.0
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_scoring_run.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/scoring/run.py`**

```python
"""Scoring stage: weighted rating, value score, composite, segmentation, aggregations."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog
from cantinaiq.scoring.math import bayesian_weighted_rating, composite_score, value_score


def _market_segment(row: dict, seg) -> str:
    r = row["weighted_rating"]
    p = row["price"]
    n = row["rating_count"]
    if n < seg.market.low_confidence_review_max:
        return "Low Confidence Niche"
    if r >= seg.market.premium_icon_min_rating and p >= seg.market.premium_icon_min_price:
        return "Premium Icon"
    if r >= seg.market.hidden_gem_min_rating and p < seg.market.premium_icon_min_price:
        return "Hidden Gem"
    if r <= seg.market.overpriced_max_rating and p >= seg.market.overpriced_min_price:
        return "Overpriced Risk"
    return "Commercial Value"


def _recommend(market_segment: str, composite: float) -> str:
    if market_segment == "Premium Icon" and composite >= 0.65:
        return "Premium Brand Builder"
    if market_segment == "Hidden Gem" and composite >= 0.60:
        return "Target"
    if market_segment == "Commercial Value" and composite >= 0.55:
        return "Value Opportunity"
    if market_segment == "Overpriced Risk":
        return "Avoid for Now"
    return "Monitor"


@register_stage("scoring")
def run_scoring(cfg: PipelineConfig, run_id: str) -> dict[str, Path]:
    processed = Path(cfg.paths.processed_dir)
    processed.mkdir(parents=True, exist_ok=True)
    src = processed / "italian_wines_enriched.parquet"
    out_wines = processed / "wines_scored.parquet"
    out_producers = processed / "producers_scored.parquet"
    out_regions = processed / "regions_scored.parquet"
    with RunLog.stage("scoring", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        df = pl.read_parquet(src)
        log.pre_rows = df.height

        if cfg.scoring.min_reviews_floor > 0:
            before = df.height
            df = df.filter(pl.col("rating_count") >= cfg.scoring.min_reviews_floor)
            log.drops["min_reviews_floor"] = before - df.height

        global_mean = float(df["rating"].mean() or 4.0)
        if cfg.scoring.bayesian_m is not None:
            m_used = cfg.scoring.bayesian_m
            m_strategy = "manual"
        else:
            m_used = int(df["rating_count"].median() or 100)
            m_strategy = "auto-median"

        df = df.with_columns([
            pl.struct(["rating", "rating_count"]).map_elements(
                lambda s: bayesian_weighted_rating(
                    rating=s["rating"], rating_count=s["rating_count"],
                    m=m_used, global_mean=global_mean,
                ),
                return_dtype=pl.Float64,
            ).alias("weighted_rating"),
        ])
        df = df.with_columns([
            pl.struct(["weighted_rating", "price"]).map_elements(
                lambda s: value_score(s["weighted_rating"], s["price"]),
                return_dtype=pl.Float64,
            ).alias("value_score"),
        ])

        # Normalisation for composite score
        def _norm(col: str) -> pl.Expr:
            min_v = df[col].min()
            max_v = df[col].max()
            if max_v is None or min_v is None or max_v == min_v:
                return pl.lit(0.5)
            return (pl.col(col) - min_v) / (max_v - min_v)

        weights = (
            cfg.scoring.weights.weighted_rating,
            cfg.scoring.weights.market_confidence,
            cfg.scoring.weights.value_for_money,
            cfg.scoring.weights.premium_fit,
            cfg.scoring.weights.portfolio_opportunity,
        )

        df = df.with_columns([
            _norm("weighted_rating").alias("_wr_n"),
            _norm("rating_count").alias("_mc_n"),
            _norm("value_score").alias("_v_n"),
            _norm("price").alias("_pf_n"),
            _norm("rating_count").alias("_po_n"),  # placeholder; opportunity-score is rating_count-driven for now
        ])
        df = df.with_columns(
            pl.struct(["_wr_n", "_mc_n", "_v_n", "_pf_n", "_po_n"]).map_elements(
                lambda s: composite_score(
                    s["_wr_n"], s["_mc_n"], s["_v_n"], s["_pf_n"], s["_po_n"],
                    weights=weights,
                ),
                return_dtype=pl.Float64,
            ).alias("composite_score")
        ).drop(["_wr_n", "_mc_n", "_v_n", "_pf_n", "_po_n"])

        df = df.with_columns(
            pl.struct(["weighted_rating", "price", "rating_count"]).map_elements(
                lambda s: _market_segment(s, cfg.segments),
                return_dtype=pl.String,
            ).alias("market_segment")
        )

        df = df.with_columns(pl.lit(cfg.hash).alias("run_config_hash"))
        df.write_parquet(out_wines)

        # Producer aggregation (skip null producers)
        prods = (
            df.filter(pl.col("producer_name").is_not_null())
              .group_by("producer_name")
              .agg(
                  pl.col("macro_region").mode().first().alias("macro_region"),
                  pl.len().alias("wines_in_dataset"),
                  pl.col("rating_count").sum().alias("total_reviews"),
                  pl.col("price").mean().alias("avg_price"),
                  (pl.col("weighted_rating") * pl.col("rating_count")).sum().alias("_num"),
                  pl.col("rating_count").sum().alias("_den"),
                  pl.col("value_score").mean().alias("value_score"),
                  pl.col("composite_score").mean().alias("composite_score"),
                  pl.col("market_segment").mode().first().alias("market_segment"),
              )
              .with_columns((pl.col("_num") / pl.col("_den")).alias("weighted_rating"))
              .drop(["_num", "_den"])
        )
        prods = prods.with_columns(
            pl.struct(["market_segment", "composite_score"]).map_elements(
                lambda s: _recommend(s["market_segment"], s["composite_score"]),
                return_dtype=pl.String,
            ).alias("recommendation")
        ).with_columns(pl.lit(cfg.hash).alias("run_config_hash"))
        prods.write_parquet(out_producers)

        # Region aggregation
        regs = (
            df.group_by("region")
              .agg(
                  pl.col("macro_region").mode().first().alias("macro_region"),
                  pl.len().alias("wines_in_dataset"),
                  pl.col("rating_count").sum().alias("total_reviews"),
                  pl.col("price").mean().alias("avg_price"),
                  (pl.col("weighted_rating") * pl.col("rating_count")).sum().alias("_num"),
                  pl.col("rating_count").sum().alias("_den"),
                  pl.col("value_score").mean().alias("value_score"),
              )
              .with_columns([
                  (pl.col("_num") / pl.col("_den")).alias("weighted_rating"),
                  (pl.col("wines_in_dataset") < 3).alias("low_sample_region"),
              ])
              .drop(["_num", "_den"])
              .with_columns(pl.lit(cfg.hash).alias("run_config_hash"))
        )
        regs.write_parquet(out_regions)

        log.post_rows = df.height
        log.custom = {
            "global_mean_rating": global_mean,
            "m_used": m_used,
            "m_strategy": m_strategy,
            "weights_used": dict(zip(
                ("weighted_rating", "market_confidence", "value_for_money", "premium_fit", "portfolio_opportunity"),
                weights, strict=True,
            )),
            "score_distribution_summary": {
                "composite_p25": float(df["composite_score"].quantile(0.25) or 0),
                "composite_p50": float(df["composite_score"].quantile(0.50) or 0),
                "composite_p75": float(df["composite_score"].quantile(0.75) or 0),
            },
            "outputs": {
                "wines": str(out_wines), "producers": str(out_producers), "regions": str(out_regions),
            },
        }
    return {"wines": out_wines, "producers": out_producers, "regions": out_regions}
```

- [ ] **Step 4: Update `src/cantinaiq/scoring/__init__.py`**

```python
"""Scoring stage."""

from cantinaiq.scoring.math import bayesian_weighted_rating, composite_score, value_score
from cantinaiq.scoring.run import run_scoring

__all__ = ["run_scoring", "bayesian_weighted_rating", "value_score", "composite_score"]
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_scoring_run.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/scoring/ tests/unit/test_scoring_run.py
git commit -m "feat(scoring): pipeline stage producing wines/producers/regions scored parquets"
```

---

## Phase 11 — Export stage

### Task 11.1: JSON exports

**Files:**
- Create: `src/cantinaiq/export/run.py`
- Modify: `src/cantinaiq/export/__init__.py`
- Create: `tests/unit/test_export.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_export.py
import json
from pathlib import Path
import shutil

import polars as pl
import pytest

from cantinaiq.cleaning.run import run_cleaning
from cantinaiq.config.loader import config_from_dict
from cantinaiq.enrichment.run import run_enrichment
from cantinaiq.export.run import run_export
from cantinaiq.ingestion.run import run_ingestion
from cantinaiq.scoring.run import run_scoring


@pytest.fixture
def cfg(tmp_path: Path, sample_xlsx: Path):
    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    for f in ("producer_aliases.csv", "macro_regions.csv", "known_producers_top50.csv"):
        shutil.copy(f"data/reference/{f}", ref / f)
    shutil.copy("tests/fixtures/llm_cache.parquet", ref / "llm_cache.parquet")
    return config_from_dict({
        "cleaning": {}, "segments": {},
        "enrichment": {
            "aliases_path": str(ref / "producer_aliases.csv"),
            "macro_regions_path": str(ref / "macro_regions.csv"),
            "known_top50_path": str(ref / "known_producers_top50.csv"),
            "llm": {"cache_path": str(ref / "llm_cache.parquet")},
        },
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
        "paths": {
            "raw_dir": str(tmp_path / "data" / "raw"),
            "interim_dir": str(tmp_path / "data" / "interim"),
            "processed_dir": str(tmp_path / "data" / "processed"),
            "exports_dir": str(tmp_path / "data" / "exports"),
            "runs_dir": str(tmp_path / "data" / "runs"),
            "reference_dir": str(ref),
            "snapshots_dir": str(tmp_path / "config" / "snapshots"),
            "source_excel": str(sample_xlsx),
        },
    })


def test_export_produces_four_json(cfg):
    run_id = "2026-05-16T00-00__exp01"
    run_ingestion(cfg, run_id)
    run_cleaning(cfg, run_id)
    interim = Path(cfg.paths.interim_dir)
    cleaned = pl.read_parquet(interim / "02_cleaned.parquet")
    safe = cleaned.filter(
        (pl.col("rating") <= 5) & (pl.col("rating_count") >= 1) & (pl.col("price") > 0)
    )
    safe.write_parquet(interim / "03_validated.parquet")
    run_enrichment(cfg, run_id)
    run_scoring(cfg, run_id)
    out = run_export(cfg, run_id)
    expected = {"producer_rankings", "region_rankings", "wine_shortlist", "dashboard_summary"}
    assert set(out) == expected
    for name, path in out.items():
        assert path.exists(), name
        payload = json.loads(path.read_text())
        assert isinstance(payload, (list, dict))
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_export.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/export/run.py`**

```python
"""Export stage: JSON contracts for downstream consumers."""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl

from cantinaiq.config.models import PipelineConfig
from cantinaiq.pipeline import register_stage
from cantinaiq.runlog import RunLog


@register_stage("export")
def run_export(cfg: PipelineConfig, run_id: str) -> dict[str, Path]:
    processed = Path(cfg.paths.processed_dir)
    exports = Path(cfg.paths.exports_dir)
    exports.mkdir(parents=True, exist_ok=True)
    wines = pl.read_parquet(processed / "wines_scored.parquet")
    producers = pl.read_parquet(processed / "producers_scored.parquet")
    regions = pl.read_parquet(processed / "regions_scored.parquet")

    out: dict[str, Path] = {}
    with RunLog.stage("export", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        log.pre_rows = wines.height

        prod_rank = producers.sort("composite_score", descending=True).to_dicts()
        out["producer_rankings"] = exports / "producer_rankings.json"
        out["producer_rankings"].write_text(json.dumps(prod_rank, indent=2, default=str))

        reg_rank = regions.sort("weighted_rating", descending=True).to_dicts()
        out["region_rankings"] = exports / "region_rankings.json"
        out["region_rankings"].write_text(json.dumps(reg_rank, indent=2, default=str))

        shortlist = wines.sort("composite_score", descending=True).head(100).to_dicts()
        out["wine_shortlist"] = exports / "wine_shortlist.json"
        out["wine_shortlist"].write_text(json.dumps(shortlist, indent=2, default=str))

        summary = {
            "run_id": run_id,
            "config_hash": cfg.hash,
            "wines_total": wines.height,
            "producers_total": producers.height,
            "regions_total": regions.height,
            "avg_weighted_rating": float(wines["weighted_rating"].mean() or 0),
            "avg_price": float(wines["price"].mean() or 0),
            "top_regions": (
                regions.sort("weighted_rating", descending=True).head(5)
                       .select(["region", "macro_region", "weighted_rating", "avg_price"])
                       .to_dicts()
            ),
            "top_producers": (
                producers.sort("composite_score", descending=True).head(10)
                         .select(["producer_name", "macro_region", "weighted_rating", "composite_score", "recommendation"])
                         .to_dicts()
            ),
        }
        out["dashboard_summary"] = exports / "dashboard_summary.json"
        out["dashboard_summary"].write_text(json.dumps(summary, indent=2, default=str))

        log.post_rows = wines.height
        log.custom = {
            "records_per_export": {k: (len(json.loads(p.read_text())) if k != "dashboard_summary" else 1)
                                   for k, p in out.items()},
            "outputs": {k: str(v) for k, v in out.items()},
        }
    return out
```

- [ ] **Step 4: Update `src/cantinaiq/export/__init__.py`**

```python
"""Export stage."""

from cantinaiq.export.run import run_export

__all__ = ["run_export"]
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_export.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/export/ tests/unit/test_export.py
git commit -m "feat(export): emit producer/region/shortlist/summary JSON contracts"
```

---

## Phase 12 — Reporting subsystem

### Task 12.1: Charts (matplotlib waterfall + distribution)

**Files:**
- Create: `src/cantinaiq/reporting/charts.py`
- Create: `tests/reporting/test_charts.py`

- [ ] **Step 1: Write failing test**

```python
# tests/reporting/test_charts.py
from pathlib import Path

from cantinaiq.reporting.charts import drop_cascade_waterfall


def test_drop_cascade_waterfall_writes_png(tmp_path: Path):
    out_dir = tmp_path
    cascade = [
        {"stage": "ingestion", "post_rows": 47291},
        {"stage": "cleaning", "post_rows": 9847},
        {"stage": "validation", "post_rows": 9841},
        {"stage": "scoring", "post_rows": 9693},
    ]
    path = drop_cascade_waterfall(cascade, config_hash="abc12345", out_dir=out_dir)
    assert path.exists()
    assert path.suffix == ".svg"
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/reporting/test_charts.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/reporting/charts.py`**

```python
"""Static, deterministic chart generation for the data-quality + methodology reports."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def drop_cascade_waterfall(
    cascade: list[dict],
    config_hash: str,
    out_dir: Path,
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"drop-cascade-{config_hash}.svg"
    stages = [c["stage"] for c in cascade]
    rows = [c["post_rows"] for c in cascade]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(stages, rows, color="#8B7355", edgecolor="#1A1714")
    ax.set_ylabel("Rows remaining")
    ax.set_title("Cleaning cascade")
    for i, v in enumerate(rows):
        ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out
```

- [ ] **Step 4: Run tests, verify pass**

```bash
uv run pytest tests/reporting/test_charts.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/cantinaiq/reporting/charts.py tests/reporting/test_charts.py
git commit -m "feat(reporting): drop-cascade waterfall as deterministic SVG"
```

---

### Task 12.2: Report renderer (Jinja2 + run-bundle context)

**Files:**
- Create: `src/cantinaiq/reporting/context.py`
- Create: `src/cantinaiq/reporting/renderer.py`
- Create: `reports/templates/data-quality.md.j2`
- Create: `tests/reporting/test_renderer.py`

- [ ] **Step 1: Write failing test**

```python
# tests/reporting/test_renderer.py
from datetime import datetime, timezone
from pathlib import Path

from cantinaiq.reporting.renderer import render_report
from cantinaiq.runlog.schema import RunBundle, StageRunLog

TEMPLATES = Path("reports/templates")


def _bundle() -> RunBundle:
    return RunBundle(
        run_id="2026-05-16T00-00__abc12345",
        started_at=datetime(2026, 5, 16, 0, 0, tzinfo=timezone.utc),
        finished_at=datetime(2026, 5, 16, 0, 5, tzinfo=timezone.utc),
        stages={
            "ingestion": StageRunLog(
                stage="ingestion",
                started_at=datetime(2026, 5, 16, 0, 0, tzinfo=timezone.utc),
                finished_at=datetime(2026, 5, 16, 0, 1, tzinfo=timezone.utc),
                pre_rows=0, post_rows=47291,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
            ),
            "cleaning": StageRunLog(
                stage="cleaning",
                started_at=datetime(2026, 5, 16, 0, 1, tzinfo=timezone.utc),
                finished_at=datetime(2026, 5, 16, 0, 2, tzinfo=timezone.utc),
                pre_rows=47291, post_rows=9847,
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


def test_data_quality_report_renders(tmp_path: Path):
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
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/reporting/test_renderer.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/reporting/context.py`**

```python
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
        rows.append(CascadeRow(
            stage=name,
            pre_rows=pre,
            post_rows=post,
            removed=removed,
            pct=pct,
            top_reason=top_reason,
            top_reason_count=top_reason_count,
        ))
        prev = post
    return rows


def build_context(bundle: RunBundle) -> dict[str, Any]:
    return {
        "run": bundle,
        "drop_cascade": build_drop_cascade(bundle),
        "metadata_footer": (
            f"Config hash {bundle.stages[list(bundle.stages)[0]].config_hash} · "
            f"run {bundle.run_id} · cantinaiq {bundle.package_version}"
        ) if bundle.stages else "",
    }
```

- [ ] **Step 4: Write `src/cantinaiq/reporting/renderer.py`**

```python
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
```

- [ ] **Step 5: Write `reports/templates/data-quality.md.j2`**

```markdown
# Data Quality Report

**Run:** `{{ run.run_id }}`
**Pipeline duration:** {{ (run.finished_at - run.started_at).total_seconds() | int }}s

## Drop cascade

| Stage | Pre | Post | Removed | % | Top reason |
|---|---:|---:|---:|---:|---|
{% for row in drop_cascade %}
| {{ row.stage }} | {{ row.pre_rows | thousands }} | {{ row.post_rows | thousands }} | {{ row.removed | thousands }} | {{ row.pct | pct }} | {{ row.top_reason }} ({{ row.top_reason_count | thousands }}) |
{% endfor %}

## Stage details

{% for stage_name, stage in run.stages.items() %}
### {{ stage_name }}

- **Pre rows:** {{ stage.pre_rows | thousands }}
- **Post rows:** {{ stage.post_rows | thousands }}
{% if stage.drops %}
- **Drops:**
{% for reason, count in stage.drops.items() %}
  - {{ reason }}: {{ count | thousands }}
{% endfor %}
{% endif %}
{% if stage.error %}
- **Error:** `{{ stage.error.type }}` — {{ stage.error.message }}
{% endif %}

{% endfor %}

---

*{{ metadata_footer }}*
```

- [ ] **Step 6: Run tests, verify pass**

```bash
uv run pytest tests/reporting/test_renderer.py -v
```

- [ ] **Step 7: Commit**

```bash
git add src/cantinaiq/reporting/context.py src/cantinaiq/reporting/renderer.py \
        reports/templates/data-quality.md.j2 tests/reporting/test_renderer.py
git commit -m "feat(reporting): Jinja2 renderer + data-quality.md.j2 template"
```

---

### Task 12.3: `cantinaiq report build` CLI

**Files:**
- Create: `src/cantinaiq/reporting/cli.py`
- Modify: `src/cantinaiq/reporting/__init__.py`
- Modify: `src/cantinaiq/cli.py`
- Create: `tests/integration/test_report_cli.py`

- [ ] **Step 1: Write failing test**

```python
# tests/integration/test_report_cli.py
from datetime import datetime, timezone
from pathlib import Path

from typer.testing import CliRunner

from cantinaiq.cli import app
from cantinaiq.config.loader import config_from_dict
from cantinaiq.runlog import RunLog


runner = CliRunner()


def _make_run(tmp_path: Path) -> str:
    cfg = config_from_dict({
        "cleaning": {}, "enrichment": {}, "segments": {},
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
        "paths": {
            "raw_dir": str(tmp_path / "data" / "raw"),
            "interim_dir": str(tmp_path / "data" / "interim"),
            "processed_dir": str(tmp_path / "data" / "processed"),
            "exports_dir": str(tmp_path / "data" / "exports"),
            "runs_dir": str(tmp_path / "data" / "runs"),
            "reference_dir": str(tmp_path / "data" / "reference"),
            "snapshots_dir": str(tmp_path / "config" / "snapshots"),
            "source_excel": str(tmp_path / "missing.xlsx"),
        },
    })
    run_id = "2026-05-16T00-00__rep01"
    with RunLog.stage("ingestion", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        log.pre_rows = 0
        log.post_rows = 100
    with RunLog.stage("cleaning", run_id, cfg, runs_dir=cfg.paths.runs_dir) as log:
        log.pre_rows = 100
        log.post_rows = 80
        log.drops = {"non_italian": 20}
    return run_id


def test_report_build_latest(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("reports/templates").mkdir(parents=True)
    Path("reports/templates/data-quality.md.j2").write_text(
        Path("/Users/vincentblokker/ClubVentureProjects/CantinaIQ/reports/templates/data-quality.md.j2").read_text()
        if Path("/Users/vincentblokker/ClubVentureProjects/CantinaIQ/reports/templates/data-quality.md.j2").exists()
        else "# DQ {{ run.run_id }} drops:{% for s in drop_cascade %} {{ s.stage }}={{ s.removed }}{% endfor %}"
    )
    run_id = _make_run(tmp_path)
    res = runner.invoke(app, ["report", "build", "--only", "data-quality"])
    assert res.exit_code == 0, res.stdout
    assert (tmp_path / "reports" / "generated" / "data-quality.md").exists()
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/integration/test_report_cli.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/reporting/cli.py`**

```python
"""`cantinaiq report …` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from cantinaiq.reporting.renderer import render_report
from cantinaiq.runlog import load_latest_run_id, load_run_bundle

report_app = typer.Typer(no_args_is_help=True, help="Render markdown reports from a run.")

TEMPLATES_BY_NAME = {
    "data-quality": "data-quality.md.j2",
}


@report_app.command("build")
def build(
    run: Annotated[str | None, typer.Option("--run")] = None,
    only: Annotated[str | None, typer.Option("--only")] = None,
    templates_dir: Annotated[Path, typer.Option("--templates-dir")] = Path("reports/templates"),
    out_dir: Annotated[Path, typer.Option("--out-dir")] = Path("reports/generated"),
    runs_dir: Annotated[Path, typer.Option("--runs-dir")] = Path("data/runs"),
) -> None:
    run_id = run or load_latest_run_id(runs_dir)
    bundle = load_run_bundle(run_id, runs_dir=runs_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = out_dir / "figures"
    targets = {only: TEMPLATES_BY_NAME[only]} if only else TEMPLATES_BY_NAME
    for name, tpl in targets.items():
        out_path = out_dir / f"{name}.md"
        render_report(
            template_name=tpl,
            bundle=bundle,
            templates_dir=templates_dir,
            out_path=out_path,
            figures_dir=figures_dir,
        )
        typer.echo(str(out_path))
```

- [ ] **Step 4: Update `src/cantinaiq/reporting/__init__.py`**

```python
"""Reporting subsystem."""

from cantinaiq.reporting.charts import drop_cascade_waterfall
from cantinaiq.reporting.cli import report_app
from cantinaiq.reporting.renderer import render_report

__all__ = ["report_app", "render_report", "drop_cascade_waterfall"]
```

- [ ] **Step 5: Modify `src/cantinaiq/cli.py` to mount the report sub-app**

Append after the `app.add_typer(run_app, name="run")` line:

```python
from cantinaiq.reporting import report_app
app.add_typer(report_app, name="report")
```

- [ ] **Step 6: Run tests, verify pass**

```bash
uv run pytest tests/integration/test_report_cli.py -v
```

- [ ] **Step 7: Commit**

```bash
git add src/cantinaiq/reporting/cli.py src/cantinaiq/reporting/__init__.py \
        src/cantinaiq/cli.py tests/integration/test_report_cli.py
git commit -m "feat(reporting): cantinaiq report build CLI"
```

---

## Phase 13 — Integration + audit

### Task 13.1: Audit command

**Files:**
- Modify: `src/cantinaiq/cli.py`
- Create: `tests/integration/test_audit.py`

- [ ] **Step 1: Write failing test**

```python
# tests/integration/test_audit.py
from pathlib import Path

from typer.testing import CliRunner

from cantinaiq.cli import app
from cantinaiq.config.loader import config_from_dict, snapshot_config

runner = CliRunner()


def test_audit_lists_snapshot(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = config_from_dict({
        "cleaning": {}, "enrichment": {}, "segments": {}, "paths": {
            "snapshots_dir": str(tmp_path / "config" / "snapshots"),
        },
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
    })
    snapshot_config(cfg, Path(cfg.paths.snapshots_dir))
    res = runner.invoke(app, ["audit", cfg.hash])
    assert res.exit_code == 0
    assert cfg.hash in res.stdout
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/integration/test_audit.py -v
```

- [ ] **Step 3: Add `audit` command to `src/cantinaiq/cli.py`**

Append before the trailing stage-import block:

```python
@app.command()
def audit(config_hash: str) -> None:
    """Show the snapshot + runs that match a given config hash."""
    snap = Path("config/snapshots") / f"{config_hash}.yaml"
    if not snap.exists():
        console.print(f"[red]No snapshot found for hash {config_hash}[/red]")
        raise typer.Exit(code=1)
    console.print(f"[bold]Snapshot:[/bold] {snap}")
    runs_dir = Path("data/runs")
    if runs_dir.exists():
        matching = [p.name for p in runs_dir.iterdir() if p.is_dir() and p.name.endswith(f"__{config_hash}")]
        console.print(f"[bold]Matching runs:[/bold] {len(matching)}")
        for r in matching:
            console.print(f"  - {r}")
```

- [ ] **Step 4: Run tests, verify pass**

```bash
uv run pytest tests/integration/test_audit.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/cantinaiq/cli.py tests/integration/test_audit.py
git commit -m "feat(cli): cantinaiq audit <hash> — list snapshot and matching runs"
```

---

### Task 13.2: End-to-end pipeline test + multirun isolation

**Files:**
- Create: `tests/integration/test_full_pipeline.py`
- Create: `tests/integration/test_multirun_isolation.py`
- Create: `tests/integration/test_config_hash_stability.py`

- [ ] **Step 1: Write `tests/integration/test_full_pipeline.py`**

```python
from pathlib import Path
import shutil

import polars as pl
import pytest

from cantinaiq.cleaning.run import run_cleaning
from cantinaiq.config.loader import config_from_dict
from cantinaiq.enrichment.run import run_enrichment
from cantinaiq.export.run import run_export
from cantinaiq.ingestion.run import run_ingestion
from cantinaiq.scoring.run import run_scoring


@pytest.fixture
def cfg(tmp_path: Path, sample_xlsx: Path):
    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    for f in ("producer_aliases.csv", "macro_regions.csv", "known_producers_top50.csv"):
        shutil.copy(f"data/reference/{f}", ref / f)
    shutil.copy("tests/fixtures/llm_cache.parquet", ref / "llm_cache.parquet")
    return config_from_dict({
        "cleaning": {}, "segments": {},
        "enrichment": {
            "aliases_path": str(ref / "producer_aliases.csv"),
            "macro_regions_path": str(ref / "macro_regions.csv"),
            "known_top50_path": str(ref / "known_producers_top50.csv"),
            "llm": {"cache_path": str(ref / "llm_cache.parquet")},
        },
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
        "paths": {
            "raw_dir": str(tmp_path / "data" / "raw"),
            "interim_dir": str(tmp_path / "data" / "interim"),
            "processed_dir": str(tmp_path / "data" / "processed"),
            "exports_dir": str(tmp_path / "data" / "exports"),
            "runs_dir": str(tmp_path / "data" / "runs"),
            "reference_dir": str(ref),
            "snapshots_dir": str(tmp_path / "config" / "snapshots"),
            "source_excel": str(sample_xlsx),
        },
    })


def test_full_pipeline_end_to_end(cfg):
    run_id = "2026-05-16T00-00__e2e01"
    run_ingestion(cfg, run_id)
    run_cleaning(cfg, run_id)
    interim = Path(cfg.paths.interim_dir)
    cleaned = pl.read_parquet(interim / "02_cleaned.parquet")
    safe = cleaned.filter(
        (pl.col("rating") <= 5) & (pl.col("rating_count") >= 1) & (pl.col("price") > 0)
    )
    safe.write_parquet(interim / "03_validated.parquet")
    run_enrichment(cfg, run_id)
    run_scoring(cfg, run_id)
    outs = run_export(cfg, run_id)
    for p in outs.values():
        assert p.exists()
```

- [ ] **Step 2: Write `tests/integration/test_config_hash_stability.py`**

```python
from cantinaiq.config.loader import config_from_dict


def test_hash_is_deterministic_under_repetition():
    payload = {
        "cleaning": {}, "enrichment": {}, "segments": {}, "paths": {},
        "scoring": {
            "bayesian_m": 100,
            "weights": {
                "weighted_rating": 0.35, "market_confidence": 0.20,
                "value_for_money": 0.20, "premium_fit": 0.15,
                "portfolio_opportunity": 0.10,
            },
        },
    }
    hashes = {config_from_dict(payload).hash for _ in range(100)}
    assert len(hashes) == 1
```

- [ ] **Step 3: Write `tests/integration/test_multirun_isolation.py`**

```python
from pathlib import Path

from hydra import compose, initialize_config_dir

from cantinaiq.config.loader import config_from_omegaconf

CONFIG_DIR = str((Path(__file__).resolve().parents[2] / "config").resolve())


def test_three_weight_presets_produce_three_hashes():
    hashes = set()
    for preset in ("baseline", "rating-heavy", "value-heavy"):
        with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
            oc = compose(
                config_name="pipeline",
                overrides=[f"scoring/weights={preset}"],
            )
        cfg = config_from_omegaconf(oc)
        hashes.add(cfg.hash)
    assert len(hashes) == 3
```

- [ ] **Step 4: Run all integration tests**

```bash
uv run pytest tests/integration/ -v
```

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_full_pipeline.py tests/integration/test_multirun_isolation.py tests/integration/test_config_hash_stability.py
git commit -m "test(integration): end-to-end pipeline + hash stability + multirun isolation"
```

---

### Task 13.3: First real pipeline run + report

**Files:**
- Modify: `README.md` (add a "Quickstart" section pointing at the CLI)
- Verify: `data/processed/*.parquet`, `data/exports/*.json`, `reports/generated/data-quality.md`

- [ ] **Step 1: Generate the first real run on the actual dataset**

```bash
uv run cantinaiq run all
```

Expected: stages print sequentially; on success, `data/exports/*.json` and `data/runs/<id>/manifest.json` exist.

If the dataset triggers a validation failure (rows with rating>5, etc.), inspect:

```bash
ls data/runs/
cat data/runs/*/validation-failures.parquet  # via duckdb if needed
```

…and decide whether to widen the cleaning drop rules or whether the failure is the *correct* signal.

- [ ] **Step 2: Render the data-quality report**

```bash
uv run cantinaiq report build --only data-quality
```

Expected: `reports/generated/data-quality.md` written; contains real row counts.

- [ ] **Step 3: Add a Quickstart to `README.md`**

Append to `README.md`:

```markdown
## Quickstart

```bash
uv sync
uv run cantinaiq run all
uv run cantinaiq report build
uv run cantinaiq status
```

Outputs land in `data/processed/`, `data/exports/`, and `reports/generated/`.
```

- [ ] **Step 4: Commit the README change (do *not* commit generated data)**

The `.gitignore` from Task 0.3 already excludes `data/{interim,processed,exports}/` and `data/runs/`. `reports/generated/` is also generated and not committed.

```bash
git add README.md
git commit -m "docs: add quickstart pointing at the CLI"
```

- [ ] **Step 5: Push**

```bash
git push
```

---

### Task 13.4: Producer post-hoc validation (spec §5.3)

**Files:**
- Create: `src/cantinaiq/enrichment/producer/validate.py`
- Modify: `src/cantinaiq/enrichment/run.py` (call the validators, attach warnings to run-log)
- Create: `tests/unit/test_producer_validate.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_producer_validate.py
from pathlib import Path

import polars as pl

from cantinaiq.enrichment.producer.validate import (
    distribution_overlap_warning,
    multi_producer_per_wine_warning,
    coverage_warnings,
)

KNOWN = Path("data/reference/known_producers_top50.csv")


def _df(rows: list[dict]) -> pl.DataFrame:
    return pl.DataFrame(rows)


def test_distribution_overlap_warning_below_threshold():
    df = _df([
        {"producer_name": "UnknownA", "macro_region": "Toscana"},
        {"producer_name": "UnknownB", "macro_region": "Toscana"},
        {"producer_name": "UnknownC", "macro_region": "Toscana"},
    ])
    warning = distribution_overlap_warning(df, known_top50_path=KNOWN, threshold=0.6)
    assert warning is not None
    assert warning["overlap"] < 0.6


def test_multi_producer_per_wine_warning():
    df = _df([
        {"wine_name_normalised": "tignanello 2019", "producer_name": "Antinori"},
        {"wine_name_normalised": "tignanello 2019", "producer_name": "Marchesi Antinori"},
        {"wine_name_normalised": "sassicaia 2018", "producer_name": "Tenuta San Guido"},
    ])
    w = multi_producer_per_wine_warning(df)
    assert w is not None
    assert w["inconsistent_count"] == 1


def test_coverage_warnings_below_target():
    df = _df([
        {"enrichment_confidence": "High", "macro_region": "Toscana"},
        {"enrichment_confidence": "None", "macro_region": "Toscana"},
        {"enrichment_confidence": "None", "macro_region": "Toscana"},
        {"enrichment_confidence": "High", "macro_region": "Piemonte"},
    ])
    warnings = coverage_warnings(df, target_overall=0.80, target_per_region=0.70)
    # Overall coverage = 2/4 = 50% → warning
    assert warnings["overall_below_target"] is True
    # Toscana coverage 33% → warning
    assert "Toscana" in warnings["regions_below_target"]
    # Piemonte coverage 100% → no warning
    assert "Piemonte" not in warnings["regions_below_target"]
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/unit/test_producer_validate.py -v
```

- [ ] **Step 3: Write `src/cantinaiq/enrichment/producer/validate.py`**

```python
"""Post-hoc validation of producer extraction (spec §5.3)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import polars as pl


def distribution_overlap_warning(
    enriched: pl.DataFrame,
    known_top50_path: Path,
    threshold: float = 0.6,
) -> dict[str, Any] | None:
    known = set()
    with Path(known_top50_path).open() as f:
        for row in csv.DictReader(f):
            known.add(row["canonical_name"])
    if "producer_name" not in enriched.columns:
        return None
    top50 = (
        enriched.filter(pl.col("producer_name").is_not_null())
                .group_by("producer_name")
                .agg(pl.len().alias("n"))
                .sort("n", descending=True)
                .head(50)
    )
    extracted = set(top50["producer_name"].to_list())
    overlap = len(known & extracted) / max(len(known), 1)
    if overlap < threshold:
        return {"overlap": overlap, "threshold": threshold, "extracted_count": len(extracted)}
    return None


def multi_producer_per_wine_warning(enriched: pl.DataFrame) -> dict[str, Any] | None:
    if "wine_name_normalised" not in enriched.columns or "producer_name" not in enriched.columns:
        return None
    counts = (
        enriched.filter(pl.col("producer_name").is_not_null())
                .group_by("wine_name_normalised")
                .agg(pl.col("producer_name").n_unique().alias("u"))
                .filter(pl.col("u") > 1)
    )
    if counts.height == 0:
        return None
    samples = counts.head(5).to_dicts()
    return {"inconsistent_count": counts.height, "samples": samples}


def coverage_warnings(
    enriched: pl.DataFrame,
    target_overall: float = 0.80,
    target_per_region: float = 0.70,
) -> dict[str, Any]:
    total = enriched.height
    hi_med = enriched.filter(pl.col("enrichment_confidence").is_in(["High", "Medium"])).height
    overall = hi_med / total if total else 0.0
    per_region = (
        enriched.group_by("macro_region")
                .agg(
                    pl.len().alias("n"),
                    pl.col("enrichment_confidence").is_in(["High", "Medium"]).sum().alias("hi_med"),
                )
                .to_dicts()
    )
    regions_below = {
        r["macro_region"]: r["hi_med"] / r["n"] if r["n"] else 0.0
        for r in per_region
        if r["n"] > 0 and (r["hi_med"] / r["n"]) < target_per_region
    }
    return {
        "overall": overall,
        "overall_target": target_overall,
        "overall_below_target": overall < target_overall,
        "regions_below_target": regions_below,
    }
```

- [ ] **Step 4: Wire warnings into `src/cantinaiq/enrichment/run.py`**

After the existing coverage section, append (inside the `with RunLog.stage` block, before `df.write_parquet(out)`):

```python
from cantinaiq.enrichment.producer.validate import (
    coverage_warnings,
    distribution_overlap_warning,
    multi_producer_per_wine_warning,
)

warnings_payload = {
    "coverage": coverage_warnings(
        df,
        target_overall=cfg.enrichment.coverage_target_overall,
        target_per_region=cfg.enrichment.coverage_target_per_region,
    ),
    "distribution": distribution_overlap_warning(df, cfg.enrichment.known_top50_path),
    "multi_producer": multi_producer_per_wine_warning(df),
}
log.custom["warnings"] = warnings_payload
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/unit/test_producer_validate.py tests/unit/test_enrichment_run.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/cantinaiq/enrichment/producer/validate.py src/cantinaiq/enrichment/run.py tests/unit/test_producer_validate.py
git commit -m "feat(enrichment): post-hoc producer validation warnings to run-log"
```

---

### Task 13.5: Remaining charts (rating distribution + confidence donut + coverage bars)

**Files:**
- Modify: `src/cantinaiq/reporting/charts.py`
- Modify: `tests/reporting/test_charts.py`
- Modify: `src/cantinaiq/reporting/renderer.py` (regenerate charts on render)

- [ ] **Step 1: Extend test**

```python
# Append to tests/reporting/test_charts.py
from cantinaiq.reporting.charts import (
    confidence_donut,
    rating_distribution_histogram,
    coverage_bars,
)


def test_rating_distribution_writes_svg(tmp_path: Path):
    pre = [4.5, 4.4, 4.2, 4.0, 3.9]
    post = [4.3, 4.3, 4.2, 4.1, 4.0]
    out = rating_distribution_histogram(pre, post, config_hash="abc12345", out_dir=tmp_path)
    assert out.exists()


def test_confidence_donut_writes_svg(tmp_path: Path):
    counts = {"High": 4000, "Medium": 3000, "Low": 1500, "None": 500}
    out = confidence_donut(counts, config_hash="abc12345", out_dir=tmp_path)
    assert out.exists()


def test_coverage_bars_writes_svg(tmp_path: Path):
    rows = [
        {"macro_region": "Toscana", "coverage": 0.92},
        {"macro_region": "Piemonte", "coverage": 0.88},
        {"macro_region": "Sicilia", "coverage": 0.70},
    ]
    out = coverage_bars(rows, config_hash="abc12345", out_dir=tmp_path)
    assert out.exists()
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/reporting/test_charts.py -v
```

- [ ] **Step 3: Append to `src/cantinaiq/reporting/charts.py`**

```python
def rating_distribution_histogram(
    pre_shrinkage: list[float],
    post_shrinkage: list[float],
    config_hash: str,
    out_dir: Path,
) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"rating-distribution-{config_hash}.svg"
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(pre_shrinkage, bins=20, alpha=0.45, label="raw rating", color="#9B3A2F", edgecolor="#1A1714")
    ax.hist(post_shrinkage, bins=20, alpha=0.65, label="weighted rating", color="#6B8E4E", edgecolor="#1A1714")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Wines")
    ax.set_title("Rating distribution: raw vs Bayesian-shrunk")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out


def confidence_donut(counts: dict[str, int], config_hash: str, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"confidence-mix-{config_hash}.svg"
    labels = ["High", "Medium", "Low", "None"]
    values = [counts.get(lab, 0) for lab in labels]
    palette = ["#6B8E4E", "#1F3A5F", "#8B7355", "#9B3A2F"]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(values, labels=labels, colors=palette, wedgeprops={"width": 0.4}, autopct="%1.0f%%")
    ax.set_title("Producer-extraction confidence mix")
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out


def coverage_bars(rows: list[dict], config_hash: str, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"coverage-per-region-{config_hash}.svg"
    rows_sorted = sorted(rows, key=lambda r: -r["coverage"])
    regions = [r["macro_region"] for r in rows_sorted]
    cov = [r["coverage"] * 100 for r in rows_sorted]
    fig, ax = plt.subplots(figsize=(8, max(3, 0.35 * len(regions) + 1)))
    ax.barh(regions, cov, color="#1F3A5F", edgecolor="#1A1714")
    ax.set_xlabel("High+Medium confidence (%)")
    ax.set_title("Producer-extraction coverage per macro-region")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(out, format="svg")
    plt.close(fig)
    return out
```

- [ ] **Step 4: Run tests, verify pass**

```bash
uv run pytest tests/reporting/test_charts.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/cantinaiq/reporting/charts.py tests/reporting/test_charts.py
git commit -m "feat(reporting): rating-distribution, confidence-donut, coverage-bars SVGs"
```

---

### Task 13.6: Methodology template

**Files:**
- Create: `reports/templates/methodology.md.j2`
- Modify: `src/cantinaiq/reporting/cli.py` (add `methodology` to TEMPLATES_BY_NAME)
- Create: `tests/reporting/test_methodology_template.py`

- [ ] **Step 1: Write failing test**

```python
# tests/reporting/test_methodology_template.py
from datetime import datetime, timezone
from pathlib import Path

from cantinaiq.reporting.renderer import render_report
from cantinaiq.runlog.schema import RunBundle, StageRunLog

TEMPLATES = Path("reports/templates")


def test_methodology_template_renders(tmp_path: Path):
    bundle = RunBundle(
        run_id="2026-05-16T00-00__abc12345",
        started_at=datetime(2026, 5, 16, 0, 0, tzinfo=timezone.utc),
        finished_at=datetime(2026, 5, 16, 0, 5, tzinfo=timezone.utc),
        stages={
            "ingestion": StageRunLog(
                stage="ingestion",
                started_at=datetime(2026, 5, 16, 0, 0, tzinfo=timezone.utc),
                finished_at=datetime(2026, 5, 16, 0, 1, tzinfo=timezone.utc),
                pre_rows=0, post_rows=47291,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
                custom={"sheets_read": ["Italy"]},
            ),
            "cleaning": StageRunLog(
                stage="cleaning",
                started_at=datetime(2026, 5, 16, 0, 1, tzinfo=timezone.utc),
                finished_at=datetime(2026, 5, 16, 0, 2, tzinfo=timezone.utc),
                pre_rows=47291, post_rows=9847,
                drops={"non_italian": 35248},
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
            ),
            "scoring": StageRunLog(
                stage="scoring",
                started_at=datetime(2026, 5, 16, 0, 3, tzinfo=timezone.utc),
                finished_at=datetime(2026, 5, 16, 0, 4, tzinfo=timezone.utc),
                pre_rows=9847, post_rows=9693,
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
```

- [ ] **Step 2: Run test, verify it fails**

```bash
uv run pytest tests/reporting/test_methodology_template.py -v
```

- [ ] **Step 3: Write `reports/templates/methodology.md.j2`**

```markdown
# Methodology

> *This document is part editorial, part generated. Numbers in this section
> are produced by the pipeline run noted in the footer; the narrative is
> hand-written.*

## 1. Research question

How can Slurpini use Dutch Vivino consumer data to prioritise Italian wine
producers and regions for collaboration, based on consumer preference, market
confidence, price positioning, and value for money?

## 2. Dataset

We ingest `data/raw/Vivino-export.xlsx`
({{ run.stages.ingestion.post_rows | thousands }} rows across
{{ run.stages.ingestion.custom.sheets_read | length }} sheets) and treat it as a
consumer-preference signal rather than a measure of objective quality. The
dataset is filtered to Italian wines and de-duplicated before any modelling.

## 3. Cleaning cascade

After parsing, encoding fixes, dedupe and the country filter, we retain
{{ run.stages.cleaning.post_rows | thousands }} Italian wines — a
{{ ((run.stages.ingestion.post_rows - run.stages.cleaning.post_rows) / run.stages.ingestion.post_rows * 100) | round(1) }}%
reduction. The dominant drop reason is *{{ run.stages.cleaning.drops.keys() | list | first if run.stages.cleaning.drops else "(none)" }}*.

## 4. Validation

A Pandera contract enforces `rating ∈ [0, 5]`, `rating_count ≥ 1`, `price > 0`,
and non-empty `country` / `region` after cleaning. Schema failures are written
to `data/runs/<id>/validation-failures.parquet` and the pipeline exits
non-zero — there is no silent contract drift.

## 5. Bayesian weighted rating

We do not use the raw average rating. A wine with a 4.8 rating on 12 reviews
should not outrank a wine with a 4.4 rating on 5,000 reviews. The pipeline
applies a Bayesian shrinkage:

$$
WR = \frac{n}{n + m} \cdot r + \frac{m}{n + m} \cdot \bar{r}
$$

Where $r$ is the Vivino rating, $n$ the rating count, $m$ a shrinkage
threshold, and $\bar{r}$ the global mean across the cleaned Italian dataset.

For this run, $m =$ **{{ run.stages.scoring.custom.m_used }}**
(strategy: `{{ run.stages.scoring.custom.m_strategy }}`) and $\bar{r} =$
**{{ run.stages.scoring.custom.global_mean_rating | round(2) }}**.

## 6. Scoring weights

The composite Slurpini Partner Intelligence Score weights five normalised
components. The weights themselves are a business assumption; they are
versioned in `config/scoring/weights/*.yaml` and reproducible by config hash.

## 7. Segmentation

Wines, producers, and regions are classified into market segments using
configurable rules in `config/segments/default.yaml`. Producers receive a
recommendation in {Target, Monitor, Premium Brand Builder, Value Opportunity,
Avoid for Now} based on segment + composite score.

## 8. Reproducibility

Every output Parquet carries `run_config_hash`. The config that produced this
report is snapshotted at
`{{ run.stages.scoring.config_snapshot_ref }}`. Re-running with
`cantinaiq run all --config-snapshot {{ run.stages.scoring.config_hash }}`
reproduces the same outputs byte-for-byte (modulo timestamp metadata in
run-logs).

---

*{{ metadata_footer }}*
```

- [ ] **Step 4: Modify `src/cantinaiq/reporting/cli.py`**

```python
TEMPLATES_BY_NAME = {
    "data-quality": "data-quality.md.j2",
    "methodology": "methodology.md.j2",
}
```

- [ ] **Step 5: Run tests, verify pass**

```bash
uv run pytest tests/reporting/test_methodology_template.py -v
```

- [ ] **Step 6: Commit**

```bash
git add reports/templates/methodology.md.j2 src/cantinaiq/reporting/cli.py tests/reporting/test_methodology_template.py
git commit -m "feat(reporting): methodology.md.j2 with editorial + injected numbers"
```

---

### Task 13.7: Wire findings one-pager template into report build

**Context:** `reports/templates/findings-one-pager.html.j2` already exists (ported from a Claude Design output, see `reports/findings-one-pager.html` for the reference render with mock data). The template expects extra context fields beyond `RunBundle`: `top_producers`, `matrix.bubbles`, `matrix.callouts`, `matrix.split`, `matrix.totals`, `findings.problem`, `findings.limitations`. This task adds the context-builder for that template and registers it in the report CLI.

**Files:**
- Create: `src/cantinaiq/reporting/findings.py`
- Create: `config/reporting/findings.yaml` (editorial copy)
- Modify: `src/cantinaiq/config/models.py` (add `ReportingConfig.findings`)
- Modify: `src/cantinaiq/reporting/renderer.py` (allow extra context dict)
- Modify: `src/cantinaiq/reporting/cli.py` (register `findings-one-pager`)
- Create: `tests/reporting/test_findings_template.py`

- [ ] **Step 1: Editorial copy in `config/reporting/findings.yaml`**

```yaml
problem: |
  Slurpini must commit annual buying budget to a small set of Italian
  producers before Vinitaly, with rating evidence that is <em>thinly
  distributed, vintage-mixed and platform-biased</em> — every wrong
  commitment costs a year of shelf and a quarter of margin.
limitations:
  - "<b>Selection bias.</b> Producers without a Vivino footprint are invisible to the pipeline; small natural-wine producers are systematically under-counted."
  - "<b>Vintage compression.</b> Ratings are mean-pooled across in-scope vintages, which under-weights producers with strong recent runs."
  - "<b>Single-platform anchoring.</b> Review distributions are drawn from one consumer platform — palate bias is Anglophone."
```

- [ ] **Step 2: Pill colour map + bubble projection in `src/cantinaiq/reporting/findings.py`**

```python
"""Context-builder for the findings-one-pager template."""

from __future__ import annotations

import math
from typing import Any

import polars as pl

PILL_BY_RECOMMENDATION = {
    "Premium Brand Builder": {"stroke": "#5B3A8C", "fill": "rgba(91,58,140,0.10)", "dot": "#5B3A8C", "abbr": "Brand Builder"},
    "Target":                {"stroke": "#1F3A5F", "fill": "rgba(31,58,95,0.10)", "dot": "#1F3A5F", "abbr": "Target"},
    "Value Opportunity":     {"stroke": "#4A6B36", "fill": "rgba(107,142,78,0.14)", "dot": "#6B8E4E", "abbr": "Value Opp."},
    "Monitor":               {"stroke": "#6B6258", "fill": "rgba(107,98,88,0.08)", "dot": "#6B6258", "abbr": "Monitor"},
    "Avoid for Now":         {"stroke": "#7B2A22", "fill": "rgba(155,58,47,0.10)", "dot": "#9B3A2F", "abbr": "Avoid"},
}

SEGMENT_FILL = {
    "Hidden Gem":           "#6B8E4E",
    "Premium Icon":         "#1F3A5F",
    "Commercial Value":     "#8B7355",
    "Overpriced Risk":      "#9B3A2F",
    "Low Confidence Niche": "#8B7355",
}


def _project_x(price: float) -> float:
    return 60.0 + (math.log10(max(price, 1.0)) - 1.0) / (math.log10(320.0) - 1.0) * 500.0


def _project_y(rating: float) -> float:
    return 280.0 - (rating - 3.0) / (4.7 - 3.0) * 260.0


def _bubble_radius(reviews: int) -> float:
    # area ∝ reviews; r ∝ sqrt(reviews); calibrated so 5000 reviews → r ≈ 13
    return min(max(math.sqrt(max(reviews, 1)) * 0.18, 3.0), 14.0)


def build_findings_context(
    producers_scored: pl.DataFrame,
    wines_scored: pl.DataFrame,
    price_split: float,
    rating_split: float,
    reasons: dict[str, str],
    findings_copy: dict[str, Any],
) -> dict[str, Any]:
    top5 = (
        producers_scored.sort("composite_score", descending=True)
                        .head(5)
                        .to_dicts()
    )
    top_producers: list[dict[str, Any]] = []
    for i, p in enumerate(top5, start=1):
        pill = PILL_BY_RECOMMENDATION.get(p["recommendation"], PILL_BY_RECOMMENDATION["Monitor"])
        top_producers.append({
            "rank": i,
            "producer_name": p["producer_name"],
            "region_label": p["macro_region"],
            "recommendation": pill["abbr"],
            "weighted_rating": p["weighted_rating"],
            "avg_price": p["avg_price"],
            "reason": reasons.get(p["producer_name"], ""),
            "pill_stroke": pill["stroke"],
            "pill_fill": pill["fill"],
            "pill_dot": pill["dot"],
        })

    bubbles: list[dict[str, Any]] = []
    for row in producers_scored.to_dicts():
        fill = SEGMENT_FILL.get(row["market_segment"], "#8B7355")
        bubbles.append({
            "cx": _project_x(row["avg_price"]),
            "cy": _project_y(row["weighted_rating"]),
            "r": _bubble_radius(row["total_reviews"]),
            "fill": fill,
            "stroke_color": fill,
            "stroke_width": 0.6,
        })

    callouts: list[dict[str, Any]] = []
    for p in top5[:3]:
        cx = _project_x(p["avg_price"])
        cy = _project_y(p["weighted_rating"])
        callouts.append({
            "label": p["producer_name"],
            "x": cx + 8,
            "y": cy - 16,
            "line_x1": cx,
            "line_y1": cy,
            "line_x2": cx + 6,
            "line_y2": cy - 14,
        })

    return {
        "top_producers": top_producers,
        "matrix": {
            "split": {"price_eur": price_split, "rating": rating_split},
            "bubbles": bubbles,
            "callouts": callouts,
            "totals": {"producers": producers_scored.height, "wines": wines_scored.height},
        },
        "findings": findings_copy,
    }
```

- [ ] **Step 3: Extend `render_report` to accept extra context**

In `src/cantinaiq/reporting/renderer.py`, change the signature:

```python
def render_report(
    template_name: str,
    bundle: RunBundle,
    templates_dir: Path,
    out_path: Path,
    figures_dir: Path | None = None,
    extra_context: dict[str, Any] | None = None,
) -> Path:
    ...
    ctx = build_context(bundle)
    ctx["figures_dir"] = str(figures_dir) if figures_dir else ""
    if extra_context:
        ctx.update(extra_context)
    ...
```

- [ ] **Step 4: Register the template in `src/cantinaiq/reporting/cli.py`**

```python
TEMPLATES_BY_NAME = {
    "data-quality":       "data-quality.md.j2",
    "methodology":        "methodology.md.j2",
    "findings-one-pager": "findings-one-pager.html.j2",
}
```

And in `build`, when `name == "findings-one-pager"`, load `producers_scored.parquet` + `wines_scored.parquet` from `data/processed/`, read editorial copy from `config/reporting/findings.yaml`, build the extra context via `build_findings_context`, and pass it to `render_report`.

- [ ] **Step 5: Write the test**

```python
# tests/reporting/test_findings_template.py
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from cantinaiq.reporting.findings import build_findings_context
from cantinaiq.reporting.renderer import render_report
from cantinaiq.runlog.schema import RunBundle, StageRunLog

TEMPLATES = Path("reports/templates")


def _bundle() -> RunBundle:
    return RunBundle(
        run_id="2026-05-16T00-00__abc12345",
        started_at=datetime(2026, 5, 16, 14, 22, tzinfo=timezone.utc),
        finished_at=datetime(2026, 5, 16, 14, 28, tzinfo=timezone.utc),
        stages={
            "ingestion": StageRunLog(
                stage="ingestion",
                started_at=datetime(2026, 5, 16, 14, 22, tzinfo=timezone.utc),
                finished_at=datetime(2026, 5, 16, 14, 23, tzinfo=timezone.utc),
                pre_rows=0, post_rows=47291,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
            ),
            "cleaning": StageRunLog(
                stage="cleaning",
                started_at=datetime(2026, 5, 16, 14, 23, tzinfo=timezone.utc),
                finished_at=datetime(2026, 5, 16, 14, 24, tzinfo=timezone.utc),
                pre_rows=47291, post_rows=8247,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
            ),
            "scoring": StageRunLog(
                stage="scoring",
                started_at=datetime(2026, 5, 16, 14, 25, tzinfo=timezone.utc),
                finished_at=datetime(2026, 5, 16, 14, 27, tzinfo=timezone.utc),
                pre_rows=8247, post_rows=8247,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
                custom={
                    "m_used": 38,
                    "m_strategy": "auto-median",
                    "global_mean_rating": 3.84,
                    "weights_used": {
                        "weighted_rating": 0.35, "market_confidence": 0.20,
                        "value_for_money": 0.20, "premium_fit": 0.15,
                        "portfolio_opportunity": 0.10,
                    },
                },
            ),
        },
        pipeline_config={},
        cli_args=[],
        git_sha=None,
        python_version="3.13.0",
        package_version="0.1.0",
    )


def test_findings_one_pager_renders(tmp_path: Path):
    producers = pl.DataFrame([
        {"producer_name": "Tenuta San Guido", "macro_region": "Toscana", "wines_in_dataset": 4,
         "total_reviews": 4500, "avg_price": 248.0, "weighted_rating": 4.58,
         "value_score": 1.2, "composite_score": 0.92,
         "market_segment": "Premium Icon", "recommendation": "Premium Brand Builder",
         "run_config_hash": "abc12345"},
        {"producer_name": "Gaja", "macro_region": "Piemonte", "wines_in_dataset": 3,
         "total_reviews": 1800, "avg_price": 212.0, "weighted_rating": 4.54,
         "value_score": 1.1, "composite_score": 0.89,
         "market_segment": "Premium Icon", "recommendation": "Premium Brand Builder",
         "run_config_hash": "abc12345"},
        {"producer_name": "Marchesi Antinori", "macro_region": "Toscana", "wines_in_dataset": 12,
         "total_reviews": 5200, "avg_price": 96.0, "weighted_rating": 4.38,
         "value_score": 1.3, "composite_score": 0.85,
         "market_segment": "Premium Icon", "recommendation": "Target",
         "run_config_hash": "abc12345"},
        {"producer_name": "COS", "macro_region": "Sicilia", "wines_in_dataset": 5,
         "total_reviews": 450, "avg_price": 38.0, "weighted_rating": 4.16,
         "value_score": 1.5, "composite_score": 0.78,
         "market_segment": "Hidden Gem", "recommendation": "Value Opportunity",
         "run_config_hash": "abc12345"},
        {"producer_name": "Mastroberardino", "macro_region": "Campania", "wines_in_dataset": 6,
         "total_reviews": 380, "avg_price": 42.0, "weighted_rating": 4.07,
         "value_score": 1.4, "composite_score": 0.74,
         "market_segment": "Hidden Gem", "recommendation": "Value Opportunity",
         "run_config_hash": "abc12345"},
    ])
    wines = pl.DataFrame({"wine_name": ["x"] * 8247})
    extra = build_findings_context(
        producers_scored=producers,
        wines_scored=wines,
        price_split=60.0,
        rating_split=4.05,
        reasons={
            "Tenuta San Guido": "Anchor prestige tier; protect existing allocation.",
            "Gaja": "Hold annual cadence; rating stable, no upside.",
            "Marchesi Antinori": "Top composite at €96 — pivotal Premium-tier producer.",
            "COS": "Rating 4.16 at €38 — strongest margin-per-quality this run.",
            "Mastroberardino": "South-Italy diversification; under-represented region.",
        },
        findings_copy={
            "problem": "Test problem statement.",
            "limitations": ["Lim A.", "Lim B.", "Lim C."],
        },
    )
    out = render_report(
        template_name="findings-one-pager.html.j2",
        bundle=_bundle(),
        templates_dir=TEMPLATES,
        out_path=tmp_path / "one-pager.html",
        extra_context=extra,
    )
    text = out.read_text()
    assert "Tenuta San Guido" in text
    assert "8,247 wines" in text
    assert "m = 38" in text
    assert "μ = 3.84" in text
    assert "Test problem statement." in text
    assert "Lim A." in text
```

- [ ] **Step 6: Run, fix, commit**

```bash
uv run pytest tests/reporting/test_findings_template.py -v
git add src/cantinaiq/reporting/findings.py src/cantinaiq/reporting/renderer.py \
        src/cantinaiq/reporting/cli.py config/reporting/findings.yaml \
        tests/reporting/test_findings_template.py
git commit -m "feat(reporting): wire findings-one-pager.html.j2 into report build"
```

---

## Self-review

After implementation, re-run the entire test suite and confirm acceptance criteria from spec §11:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src/
uv run pytest --cov=src/cantinaiq --cov-fail-under=85
```

Expected: all green. Acceptance criteria 1–7 from the spec are now mechanically verifiable:

1. ✅ `uv run cantinaiq run all` produces `data/exports/*.json` + `reports/generated/data-quality.md` deterministically (Task 13.3).
2. ✅ `uv run pytest` ≥85% coverage (CI gate from Task 0.3).
3. ✅ Drop-cascade table generated 100% from `RunBundle` (Tasks 12.2 + 12.3).
4. ✅ `cantinaiq audit <hash>` non-empty (Task 13.1).
5. ✅ Pandera schemas pass on every committed-shape Parquet (Tasks 5.1 + 9.3 + 10.2).
6. ✅ Known-producer overlap warning logic — implemented in Task 13.4 (`distribution_overlap_warning`, `multi_producer_per_wine_warning`, `coverage_warnings` wired into `run_enrichment`).
7. ✅ Design doc, source files, lockfile, and snapshots committed (Tasks 0.x + 1.x).

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-15-cantinaiq-data-pipeline.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
