"""Producer clustering — KMeans on a 4-feature space.

Features: standardised (weighted_rating, value_score, total_reviews, avg_price).
Output: an additional `cluster_id` column on the producer dataframe.

Clustering is *complementary* to the rule-based market_segment — segments
encode business intent ("Premium Icon"), clusters encode empirical similarity
("producers in cluster 2 look like each other in the feature space"). Both
columns coexist.
"""

from __future__ import annotations

import numpy as np
import polars as pl
from sklearn.cluster import KMeans  # type: ignore[import-untyped]
from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]

FEATURES = ["weighted_rating", "value_score", "total_reviews", "avg_price"]


def build_feature_matrix(df: pl.DataFrame) -> tuple[np.ndarray, list[str]]:
    """Return (X_scaled, producer_names). Rows with any null in features are dropped."""
    keep = df.drop_nulls(subset=FEATURES)
    raw = keep.select(FEATURES).to_numpy()
    scaler = StandardScaler()
    return scaler.fit_transform(raw), keep["producer_name"].to_list()


def fit_kmeans_clusters(
    df: pl.DataFrame, n_clusters: int = 5, random_state: int = 42
) -> pl.DataFrame:
    """Return `df` with a `cluster_id` column appended (Int64)."""
    X, names = build_feature_matrix(df)
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")
    labels = km.fit_predict(X)
    label_map = dict(zip(names, labels.tolist(), strict=True))
    return df.with_columns(
        pl.col("producer_name")
        .map_elements(lambda n: label_map.get(n, -1), return_dtype=pl.Int64)
        .alias("cluster_id")
    )
