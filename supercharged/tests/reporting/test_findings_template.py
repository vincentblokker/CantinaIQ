from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from cantinaiq.reporting.findings import build_findings_context
from cantinaiq.reporting.renderer import render_report
from cantinaiq.runlog.schema import RunBundle, StageRunLog

TEMPLATES = Path("reports/templates")


def _bundle() -> RunBundle:
    return RunBundle(
        run_id="2026-05-16T00-00__abc12345",
        started_at=datetime(2026, 5, 16, 14, 22, tzinfo=UTC),
        finished_at=datetime(2026, 5, 16, 14, 28, tzinfo=UTC),
        stages={
            "ingestion": StageRunLog(
                stage="ingestion",
                started_at=datetime(2026, 5, 16, 14, 22, tzinfo=UTC),
                finished_at=datetime(2026, 5, 16, 14, 23, tzinfo=UTC),
                pre_rows=0,
                post_rows=47291,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
            ),
            "cleaning": StageRunLog(
                stage="cleaning",
                started_at=datetime(2026, 5, 16, 14, 23, tzinfo=UTC),
                finished_at=datetime(2026, 5, 16, 14, 24, tzinfo=UTC),
                pre_rows=47291,
                post_rows=8247,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
            ),
            "scoring": StageRunLog(
                stage="scoring",
                started_at=datetime(2026, 5, 16, 14, 25, tzinfo=UTC),
                finished_at=datetime(2026, 5, 16, 14, 27, tzinfo=UTC),
                pre_rows=8247,
                post_rows=8247,
                config_hash="abc12345",
                config_snapshot_ref="config/snapshots/abc12345.yaml",
                custom={
                    "m_used": 38,
                    "m_strategy": "auto-median",
                    "global_mean_rating": 3.84,
                    "weights_used": {
                        "weighted_rating": 0.35,
                        "market_confidence": 0.20,
                        "value_for_money": 0.20,
                        "premium_fit": 0.15,
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


def test_findings_one_pager_renders(tmp_path: Path) -> None:
    producers = pl.DataFrame(
        [
            {
                "producer_name": "Tenuta San Guido",
                "macro_region": "Toscana",
                "wines_in_dataset": 4,
                "total_reviews": 4500,
                "avg_price": 248.0,
                "weighted_rating": 4.58,
                "value_score": 1.2,
                "composite_score": 0.92,
                "market_segment": "Premium Icon",
                "recommendation": "Premium Brand Builder",
                "run_config_hash": "abc12345",
            },
            {
                "producer_name": "Gaja",
                "macro_region": "Piemonte",
                "wines_in_dataset": 3,
                "total_reviews": 1800,
                "avg_price": 212.0,
                "weighted_rating": 4.54,
                "value_score": 1.1,
                "composite_score": 0.89,
                "market_segment": "Premium Icon",
                "recommendation": "Premium Brand Builder",
                "run_config_hash": "abc12345",
            },
            {
                "producer_name": "Marchesi Antinori",
                "macro_region": "Toscana",
                "wines_in_dataset": 12,
                "total_reviews": 5200,
                "avg_price": 96.0,
                "weighted_rating": 4.38,
                "value_score": 1.3,
                "composite_score": 0.85,
                "market_segment": "Premium Icon",
                "recommendation": "Target",
                "run_config_hash": "abc12345",
            },
            {
                "producer_name": "COS",
                "macro_region": "Sicilia",
                "wines_in_dataset": 5,
                "total_reviews": 450,
                "avg_price": 38.0,
                "weighted_rating": 4.16,
                "value_score": 1.5,
                "composite_score": 0.78,
                "market_segment": "Hidden Gem",
                "recommendation": "Value Opportunity",
                "run_config_hash": "abc12345",
            },
            {
                "producer_name": "Mastroberardino",
                "macro_region": "Campania",
                "wines_in_dataset": 6,
                "total_reviews": 380,
                "avg_price": 42.0,
                "weighted_rating": 4.07,
                "value_score": 1.4,
                "composite_score": 0.74,
                "market_segment": "Hidden Gem",
                "recommendation": "Value Opportunity",
                "run_config_hash": "abc12345",
            },
        ]
    )
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
    assert "8,247" in text
    assert "m = 38" in text
    assert "3.84" in text  # μ value
    assert "Test problem statement." in text
    assert "Lim A." in text
