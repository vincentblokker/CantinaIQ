from pathlib import Path

from hydra import compose, initialize_config_dir

from cantinaiq.config.loader import config_from_omegaconf

CONFIG_DIR = str((Path(__file__).resolve().parents[2] / "config").resolve())


def test_three_weight_presets_produce_three_hashes() -> None:
    hashes: set[str] = set()
    for preset in ("baseline", "rating-heavy", "value-heavy"):
        with initialize_config_dir(config_dir=CONFIG_DIR, version_base="1.3"):
            oc = compose(
                config_name="pipeline",
                overrides=[f"scoring/weights={preset}"],
            )
        cfg = config_from_omegaconf(oc)
        hashes.add(cfg.hash)
    assert len(hashes) == 3
