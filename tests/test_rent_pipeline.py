"""Tests verifying preprocessing happens inside the sklearn Pipeline."""

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

from poi import POI
from rent_estimation_utils import (
    FEATURES,
    TARGET,
    build_transformer,
    preprocess,
)


TSMC = POI(slug="tsmc-az", name="TSMC AZ", latitude=33.775196, longitude=-112.160449, radius_miles=15)


def _train_pipeline(df: pd.DataFrame) -> Pipeline:
    pipeline = Pipeline([
        ("preprocessor", build_transformer()),
        ("model", RandomForestRegressor(n_estimators=10, random_state=0, n_jobs=1)),
    ])
    pipeline.fit(df[FEATURES], df[TARGET])
    return pipeline


def test_preprocess_drops_required_nans_and_outliers(rental_listings_fixture):
    df = pd.DataFrame(rental_listings_fixture)
    cleaned = preprocess(df, TSMC)

    for col in ["bedrooms", "bathrooms", "squareFootage", "latitude", "longitude", TARGET]:
        assert cleaned[col].notna().all(), f"{col} must never be NaN after preprocess"
    assert len(cleaned) > 0


def test_preprocess_attaches_distance_feature(rental_listings_fixture):
    df = preprocess(pd.DataFrame(rental_listings_fixture), TSMC)
    assert "distanceToPoi" in df.columns
    assert df["distanceToPoi"].notna().all()
    # 5-mi radius fixture, so all distances should be small.
    assert df["distanceToPoi"].max() < 100


def test_preprocess_filters_outlier_prices(rental_listings_fixture):
    df = pd.DataFrame(rental_listings_fixture).copy()
    # Inject obviously-bad rentals — $5 and $999,999 — then ensure they're dropped.
    df.loc[df.index[0], "price"] = 5
    df.loc[df.index[1], "price"] = 999_999
    cleaned = preprocess(df, TSMC)
    assert (cleaned["price"] >= 200).all()
    assert (cleaned["price"] <= 20_000).all()


def test_pipeline_handles_missing_lotSize(rental_listings_fixture):
    df = preprocess(pd.DataFrame(rental_listings_fixture), TSMC)
    pipeline = _train_pipeline(df)

    sample = df.iloc[:5][FEATURES].copy()
    sample["lotSize"] = np.nan
    sample["yearBuilt"] = np.nan
    sample["propertyType"] = None

    preds = pipeline.predict(sample)
    assert len(preds) == 5
    assert np.all(np.isfinite(preds))


def test_pipeline_handles_unseen_property_type(rental_listings_fixture):
    df = preprocess(pd.DataFrame(rental_listings_fixture), TSMC)
    pipeline = _train_pipeline(df)

    sample = df.iloc[:1][FEATURES].copy()
    sample["propertyType"] = "Castle"
    preds = pipeline.predict(sample)
    assert np.isfinite(preds[0])


def test_distance_feature_present_at_inference(rental_listings_fixture):
    """A model trained with distanceToPoi must accept it at inference time."""
    df = preprocess(pd.DataFrame(rental_listings_fixture), TSMC)
    pipeline = _train_pipeline(df)
    sample = df.iloc[:3][FEATURES].copy()
    assert "distanceToPoi" in sample.columns
    preds = pipeline.predict(sample)
    assert np.all(np.isfinite(preds))


def test_inference_matches_training_on_seen_row(rental_listings_fixture):
    df = preprocess(pd.DataFrame(rental_listings_fixture), TSMC)
    pipeline = _train_pipeline(df)
    preds_a = pipeline.predict(df[FEATURES].iloc[:10])
    preds_b = pipeline.predict(df[FEATURES].iloc[:10])
    np.testing.assert_array_equal(preds_a, preds_b)
