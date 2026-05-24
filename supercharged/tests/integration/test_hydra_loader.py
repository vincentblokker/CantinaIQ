from pathlib import Path

from hydra import compose, initialize_config_dir

from cantinaiq.config.loader import config_from_omegaconf

REPO = Path(__file__).resolve().parents[2]
CONFIG_DIR = str((REPO / "config").resolve())


def test_baseline_compose() -> None:
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        oc = compose(config_name="pipeline")
    cfg = config_from_omegaconf(oc)
    assert cfg.scoring.weights.weighted_rating == 0.35
    assert cfg.scoring.bayesian_m is None


def test_rating_heavy_override() -> None:
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        oc = compose(
            config_name="pipeline",
            overrides=["scoring/weights=rating-heavy"],
        )
    cfg = config_from_omegaconf(oc)
    assert cfg.scoring.weights.weighted_rating == 0.50


def test_inline_override() -> None:
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        oc = compose(
            config_name="pipeline",
            overrides=["scoring.bayesian_m=250"],
        )
    cfg = config_from_omegaconf(oc)
    assert cfg.scoring.bayesian_m == 250


def test_hash_differs_between_presets() -> None:
    with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
        base = config_from_omegaconf(compose(config_name="pipeline"))
        rh = config_from_omegaconf(
            compose(config_name="pipeline", overrides=["scoring/weights=rating-heavy"])
        )
    assert base.hash != rh.hash
