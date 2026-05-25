"""Isolation Forest anomaly detection on Vivino review patterns.

Inputs: a polars DataFrame with `rating` and `rating_count` columns.
Outputs: the same DataFrame with `is_anomaly: bool` and
`anomaly_score: float` columns appended.

`anomaly_score` follows sklearn's convention — lower values are more
anomalous. `is_anomaly` is `True` for the `contamination` fraction with the
lowest scores.
"""

from __future__ import annotations

import numpy as np
import polars as pl
from sklearn.ensemble import IsolationForest  # type: ignore[import-untyped]


def flag_review_anomalies(
    df: pl.DataFrame,
    contamination: float = 0.05,
    seed: int = 42,
) -> pl.DataFrame:
    """Return `df` with `is_anomaly` + `anomaly_score` columns appended."""
    rating = df["rating"].cast(pl.Float64).fill_null(0.0).to_numpy()
    rc = df["rating_count"].cast(pl.Int64).fill_null(1).to_numpy()
    rc_log = np.log10(np.maximum(rc, 1))
    X = np.column_stack([rating, rc_log])

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=seed,
    )
    pred = model.fit_predict(X)
    score = model.decision_function(X)
    is_anom = pred == -1
    return df.with_columns(
        pl.Series("is_anomaly", is_anom),
        pl.Series("anomaly_score", score),
    )
