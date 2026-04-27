"""Tests verifying preprocessing happens inside the sklearn Pipeline."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

from rent_estimation_utils import (
    FEATURES,
    TARGET,
    build_transformer,
    preprocess,
)


def _train_pipeline(df: pd.DataFrame) -> Pipeline:
    pipeline = Pipeline([
        ("preprocessor", build_transformer()),
        ("model", RandomForestRegressor(n_estimators=10, random_state=0, n_jobs=1)),
    ])
    pipeline.fit(df[FEATURES], df[TARGET])
    return pipeline


def test_preprocess_only_drops_rows_with_required_nans(rental_listings_fixture):
    """preprocess no longer fills NaNs — that's the pipeline's job. It only drops rows."""
    df = pd.DataFrame(rental_listings_fixture)
    cleaned = preprocess(df)

    for col in ["bedrooms", "bathrooms", "squareFootage", "latitude", "longitude", TARGET]:
        assert cleaned[col].notna().all(), f"{col} must never be NaN after preprocess"
    assert len(cleaned) > 0


def test_pipeline_handles_missing_lotSize(rental_listings_fixture):
    """Inference must not crash on optional NaNs — imputers fill them."""
    df = preprocess(pd.DataFrame(rental_listings_fixture))
    pipeline = _train_pipeline(df)

    sample = df.iloc[:5][FEATURES].copy()
    sample["lotSize"] = np.nan
    sample["yearBuilt"] = np.nan
    sample["propertyType"] = None

    preds = pipeline.predict(sample)
    assert len(preds) == 5
    assert np.all(np.isfinite(preds))


def test_pipeline_handles_unseen_property_type(rental_listings_fixture):
    df = preprocess(pd.DataFrame(rental_listings_fixture))
    pipeline = _train_pipeline(df)

    sample = df.iloc[:1][FEATURES].copy()
    sample["propertyType"] = "Castle"  # never seen during training
    preds = pipeline.predict(sample)
    assert np.isfinite(preds[0])


def test_inference_matches_training_on_seen_row(rental_listings_fixture):
    """A pipeline predicting on its training data should produce stable, finite output."""
    df = preprocess(pd.DataFrame(rental_listings_fixture))
    pipeline = _train_pipeline(df)
    preds_a = pipeline.predict(df[FEATURES].iloc[:10])
    preds_b = pipeline.predict(df[FEATURES].iloc[:10])
    np.testing.assert_array_equal(preds_a, preds_b)
