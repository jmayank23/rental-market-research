"""Tests covering rent_model training outputs."""

import json

import joblib
import numpy as np
import pandas as pd
import pytest

import rent_model
from poi import POI


TSMC = POI(slug="tsmc-az", name="TSMC AZ", latitude=33.775196, longitude=-112.160449, radius_miles=15)


def _train(tmp_path, monkeypatch, rentals, model_name="rf"):
    rental_path = tmp_path / "rental.json"
    with open(rental_path, "w") as f:
        json.dump(rentals, f)
    model_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "metrics.json"
    monkeypatch.setattr(rent_model, "N_ITER", 2)
    monkeypatch.setattr(rent_model, "CV_FOLDS", 2)
    rent_model.train(rental_path, model_path, metrics_path, TSMC, model_name=model_name)
    return {
        "model_path": model_path,
        "metrics_path": metrics_path,
        "metrics": json.loads(metrics_path.read_text()),
        "rentals": rentals,
    }


@pytest.fixture
def trained(tmp_path, monkeypatch, rental_listings_fixture):
    """Train a small RF model on the rental fixture and return the artifacts."""
    return _train(tmp_path, monkeypatch, rental_listings_fixture, model_name="rf")


@pytest.fixture
def trained_lgbm(tmp_path, monkeypatch, rental_listings_fixture):
    return _train(tmp_path, monkeypatch, rental_listings_fixture, model_name="lgbm")


def test_residual_quantiles_recorded(trained):
    metrics = trained["metrics"]
    assert "residual_quantiles" in metrics
    quantiles = metrics["residual_quantiles"]
    assert {"q10", "q50", "q90"} <= quantiles.keys()
    assert quantiles["q10"] <= quantiles["q50"] <= quantiles["q90"]


def test_metrics_record_log_target_transform(trained):
    """The metrics file must record that the target was log-transformed."""
    assert trained["metrics"].get("target_transform") == "log1p"


def test_metrics_record_poi(trained):
    poi = trained["metrics"]["poi"]
    assert poi["slug"] == "tsmc-az"
    assert poi["radius_miles"] == 15


def test_target_log_transform_round_trip(trained):
    """Predictions come back in dollar space (positive, sane order of magnitude)."""
    estimator = joblib.load(trained["model_path"])
    rentals = trained["rentals"]
    sample = pd.DataFrame(rentals).head(5)
    # The estimator expects FEATURES to include distanceToPoi.
    sample = sample.assign(distanceToPoi=1.0)
    preds = estimator.predict(sample[rent_model.FEATURES])
    assert np.all(preds > 0), "log target round-trip must yield positive dollar values"
    assert np.all(preds < 1_000_000), "predictions should be within a sane rent range"


def test_group_split_no_address_leakage(tmp_path, monkeypatch, rental_listings_fixture):
    """formattedAddress used as group key — no address may appear in both splits."""
    rentals = list(rental_listings_fixture)

    # Force three duplicate addresses so we can detect leakage.
    duplicate = rentals[0]["formattedAddress"]
    for r in rentals[:5]:
        r["formattedAddress"] = duplicate

    rental_path = tmp_path / "rental.json"
    with open(rental_path, "w") as f:
        json.dump(rentals, f)

    monkeypatch.setattr(rent_model, "N_ITER", 2)
    monkeypatch.setattr(rent_model, "CV_FOLDS", 2)

    rent_model.train(
        rental_path,
        tmp_path / "m.joblib",
        tmp_path / "m.json",
        TSMC,
    )
    metrics = json.loads((tmp_path / "m.json").read_text())
    assert metrics["group_overlap"] == 0


def test_persisted_estimator_predicts(trained):
    """Smoke check that the persisted estimator can score new rows."""
    estimator = joblib.load(trained["model_path"])
    sample = pd.DataFrame(trained["rentals"]).head(3).assign(distanceToPoi=2.0)
    preds = estimator.predict(sample[rent_model.FEATURES])
    assert len(preds) == 3


def test_metrics_record_model_name_rf(trained):
    assert trained["metrics"]["model_name"] == "rf"


def test_lightgbm_trains_and_serializes(trained_lgbm):
    """LGBM end-to-end: trains, persists, predicts in dollar space."""
    assert trained_lgbm["metrics"]["model_name"] == "lgbm"
    estimator = joblib.load(trained_lgbm["model_path"])
    sample = pd.DataFrame(trained_lgbm["rentals"]).head(3).assign(distanceToPoi=2.0)
    preds = estimator.predict(sample[rent_model.FEATURES])
    assert len(preds) == 3
    assert np.all(preds > 0)


def test_feature_importance_recorded_rf(trained):
    fi = trained["metrics"]["feature_importance"]
    assert isinstance(fi, dict)
    assert len(fi) > 0
    weights = list(fi.values())
    assert pytest.approx(sum(weights), abs=0.01) == 1.0
    # Iteration order should be by descending weight (Python 3.7+ preserves dict order)
    assert weights == sorted(weights, reverse=True)


def test_feature_importance_recorded_lgbm(trained_lgbm):
    fi = trained_lgbm["metrics"]["feature_importance"]
    assert pytest.approx(sum(fi.values()), abs=0.01) == 1.0


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        rent_model._make_model("xgboost")
