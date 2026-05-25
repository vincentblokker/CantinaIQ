"""Producer clustering — KMeans on (rating, value, reviews, price) feature space."""
from __future__ import annotations

import numpy as np
import polars as pl

from cantinaiq.clustering import build_feature_matrix, fit_kmeans_clusters


def test_build_feature_matrix_shape() -> None:
    df = pl.DataFrame(
        {
            "producer_name": ["A", "B", "C"],
            "weighted_rating": [4.5, 4.2, 4.0],
            "value_score": [1.2, 1.5, 1.8],
            "total_reviews": [5000, 3000, 1000],
            "avg_price": [80.0, 25.0, 12.0],
        }
    )
    X, names = build_feature_matrix(df)
    assert X.shape == (3, 4)
    assert names == ["A", "B", "C"]
    assert np.allclose(X.mean(axis=0), 0, atol=1e-9)
    # Standardised: per-feature std ≈ 1 (with population std; sklearn uses ddof=0).
    assert np.allclose(X.std(axis=0), 1, atol=0.1)


def test_fit_kmeans_assigns_three_clusters() -> None:
    df = pl.DataFrame(
        {
            "producer_name": [f"P{i}" for i in range(15)],
            "weighted_rating": [
                4.6, 4.5, 4.7, 4.0, 4.1, 3.9, 4.2, 4.3, 4.2,
                4.5, 4.4, 4.6, 3.8, 3.9, 4.0,
            ],
            "value_score": [
                0.5, 0.6, 0.4, 2.0, 2.1, 1.9, 1.0, 1.1, 1.2,
                0.7, 0.8, 0.6, 2.2, 2.3, 2.1,
            ],
            "total_reviews": [
                10000, 8000, 12000, 500, 600, 400, 3000, 2500, 3500,
                9000, 8500, 11000, 700, 800, 500,
            ],
            "avg_price": [200, 180, 220, 10, 12, 8, 50, 45, 55, 190, 200, 230, 9, 11, 10],
        }
    )
    df_clustered = fit_kmeans_clusters(df, n_clusters=3, random_state=42)
    assert "cluster_id" in df_clustered.columns
    assert df_clustered["cluster_id"].unique().len() == 3
    by_cluster = df_clustered.group_by("cluster_id").agg(
        pl.col("avg_price").mean().alias("mean_price")
    )
    spread = float(by_cluster["mean_price"].max() or 0) - float(by_cluster["mean_price"].min() or 0)
    assert spread > 100
