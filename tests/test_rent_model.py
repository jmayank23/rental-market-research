"""Tests covering rent_model training outputs."""

import json

import joblib
import pandas as pd

import rent_model


def test_residual_quantiles_recorded(tmp_path, monkeypatch, rental_listings_fixture):
    """Trained model metrics file must contain a residual_quantiles block."""
    rental_path = tmp_path / "rental.json"
    with open(rental_path, "w") as f:
        json.dump(rental_listings_fixture, f)

    model_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "metrics.json"

    monkeypatch.setattr(rent_model, "N_ITER", 2)
    monkeypatch.setattr(rent_model, "CV_FOLDS", 2)

    rent_model.train(rental_path, model_path, metrics_path)

    assert model_path.exists()
    metrics = json.loads(metrics_path.read_text())
    assert "residual_quantiles" in metrics
    quantiles = metrics["residual_quantiles"]
    assert {"q10", "q50", "q90"} <= quantiles.keys()
    assert quantiles["q10"] <= quantiles["q50"] <= quantiles["q90"]

    # Smoke check that the persisted pipeline can predict.
    pipeline = joblib.load(model_path)
    preds = pipeline.predict(pd.DataFrame(rental_listings_fixture)[rent_model.FEATURES].head(3))
    assert len(preds) == 3
