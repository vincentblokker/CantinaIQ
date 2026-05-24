from cantinaiq.config.loader import config_from_dict


def test_hash_is_deterministic_under_repetition() -> None:
    payload = {
        "cleaning": {},
        "enrichment": {},
        "segments": {},
        "paths": {},
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
    }
    hashes = {config_from_dict(payload).hash for _ in range(100)}
    assert len(hashes) == 1
