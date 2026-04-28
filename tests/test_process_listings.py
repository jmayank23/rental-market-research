"""Tests for process_listings helpers."""

import csv
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np

import process_listings
from finance import monthly_mortgage
from process_listings import (
    add_distance_to_poi,
    add_predicted_rent,
)


TSMC_LAT, TSMC_LON = 33.775196, -112.160449


def test_distance_to_poi_handles_none_coords():
    listings = [{"latitude": None, "longitude": None}]
    add_distance_to_poi(listings, TSMC_LAT, TSMC_LON)
    assert listings[0]["distanceToPoi"] is None


def test_distance_to_poi_zero_coords_treated_as_valid():
    """Lat/lon of 0 are valid coordinates (equator/prime meridian) — must not be falsy-skipped."""
    listings = [{"latitude": 0.0, "longitude": 0.0}]
    add_distance_to_poi(listings, TSMC_LAT, TSMC_LON)
    # TSMC AZ → (0,0) is a long way; just assert it computed something numeric.
    assert listings[0]["distanceToPoi"] is not None
    assert listings[0]["distanceToPoi"] > 0


def test_distance_to_poi_real_listing(sale_listings_fixture):
    listings = [dict(l) for l in sale_listings_fixture[:5]]
    add_distance_to_poi(listings, TSMC_LAT, TSMC_LON)
    for listing in listings:
        if listing.get("latitude") is not None and listing.get("longitude") is not None:
            assert listing["distanceToPoi"] is not None
            assert listing["distanceToPoi"] >= 0


def test_monthly_mortgage_basic():
    # $100k loan @ 6% over 30 years ≈ $599.55
    payment = monthly_mortgage(100_000, annual_rate=0.06)
    assert 595 < payment < 605


class _StubPipeline:
    def predict(self, X):
        # one prediction per non-null row
        return np.full(len(X), 2000.0)


def test_predictions_align_with_input_index():
    """Listings missing required features must keep predictedRent=None;
    listings with required features must get the prediction at their position."""
    listings = [
        {"bedrooms": 3, "bathrooms": 2, "squareFootage": 1500, "latitude": 33.7, "longitude": -112.1},
        {"bedrooms": None},  # missing required
        {"bedrooms": 4, "bathrooms": 3, "squareFootage": 2000, "latitude": 33.7, "longitude": -112.1},
        {"latitude": None},  # missing required
        {"bedrooms": 2, "bathrooms": 1, "squareFootage": 800, "latitude": 33.7, "longitude": -112.1},
    ]
    metrics = {"val_metrics": {"mape": 10.0}}

    with patch("process_listings.joblib.load", return_value=_StubPipeline()):
        with patch("builtins.open"):
            with patch("process_listings.json.load", return_value=metrics):
                add_predicted_rent(listings)

    # Positions 0, 2, 4 had required features → predicted
    assert listings[0]["predictedRent"] == 2000
    assert listings[2]["predictedRent"] == 2000
    assert listings[4]["predictedRent"] == 2000
    # Positions 1, 3 missing required features → None
    assert listings[1]["predictedRent"] is None
    assert listings[3]["predictedRent"] is None


def test_add_predicted_rent_handles_no_eligible_rows():
    """If every listing is missing required features, predict() must not be called."""
    listings = [{"bedrooms": None}, {"bathrooms": None}]
    metrics = {"val_metrics": {"mape": 10.0}}

    pipeline = _StubPipeline()
    with patch("process_listings.joblib.load", return_value=pipeline):
        with patch("builtins.open"):
            with patch("process_listings.json.load", return_value=metrics):
                add_predicted_rent(listings)

    for listing in listings:
        assert listing["predictedRent"] is None
        assert listing["predictedRentMin"] is None
        assert listing["predictedRentMax"] is None


def _viable_listing():
    return {"bedrooms": 3, "bathrooms": 2, "squareFootage": 1500, "latitude": 33.7, "longitude": -112.1}


def test_bounds_use_residual_quantiles_when_present():
    """Newer metrics files supply asymmetric residual quantiles."""
    listings = [_viable_listing()]
    metrics = {
        "val_metrics": {"mape": 14.5},
        "residual_quantiles": {"q10": -0.20, "q50": 0.0, "q90": 0.30},
    }
    with patch("process_listings.joblib.load", return_value=_StubPipeline()):
        with patch("builtins.open"):
            with patch("process_listings.json.load", return_value=metrics):
                add_predicted_rent(listings)
    # 2000 * (1 - 0.20) = 1600, 2000 * (1 + 0.30) = 2600
    assert listings[0]["predictedRentMin"] == 1600
    assert listings[0]["predictedRent"] == 2000
    assert listings[0]["predictedRentMax"] == 2600


def test_bounds_fall_back_to_mape_for_legacy_metrics():
    """Older metrics files (no residual_quantiles) still work via ±MAPE."""
    listings = [_viable_listing()]
    metrics = {"val_metrics": {"mape": 10.0}}
    with patch("process_listings.joblib.load", return_value=_StubPipeline()):
        with patch("builtins.open"):
            with patch("process_listings.json.load", return_value=metrics):
                add_predicted_rent(listings)
    assert listings[0]["predictedRentMin"] == 1800
    assert listings[0]["predictedRentMax"] == 2200


def test_bounds_are_non_negative_when_q10_below_minus_one():
    """Defensive: degenerate q10 < -1 must not produce negative bounds."""
    listings = [_viable_listing()]
    metrics = {
        "val_metrics": {"mape": 14.5},
        "residual_quantiles": {"q10": -1.5, "q50": 0.0, "q90": 0.3},
    }
    with patch("process_listings.joblib.load", return_value=_StubPipeline()):
        with patch("builtins.open"):
            with patch("process_listings.json.load", return_value=metrics):
                add_predicted_rent(listings)
    assert listings[0]["predictedRentMin"] == 0


def test_bounds_bracket_prediction_in_normal_case():
    listings = [_viable_listing()]
    metrics = {
        "val_metrics": {"mape": 14.5},
        "residual_quantiles": {"q10": -0.15, "q50": 0.0, "q90": 0.20},
    }
    with patch("process_listings.joblib.load", return_value=_StubPipeline()):
        with patch("builtins.open"):
            with patch("process_listings.json.load", return_value=metrics):
                add_predicted_rent(listings)
    pred = listings[0]["predictedRent"]
    assert listings[0]["predictedRentMin"] <= pred <= listings[0]["predictedRentMax"]


def test_csv_includes_top_features_when_model_provided(tmp_path, monkeypatch, rental_listings_fixture):
    """End-to-end: training a real model and exporting selected listings yields topFeatures column."""
    import json as _json

    import rent_model
    from poi import POI

    poi = POI(slug="tsmc-az", name="TSMC AZ", latitude=33.775196, longitude=-112.160449, radius_miles=15)
    rental_path = tmp_path / "rental.json"
    with open(rental_path, "w") as f:
        _json.dump(rental_listings_fixture, f)
    model_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "metrics.json"

    monkeypatch.setattr(rent_model, "N_ITER", 2)
    monkeypatch.setattr(rent_model, "CV_FOLDS", 2)
    rent_model.train(rental_path, model_path, metrics_path, poi, model_name="rf")

    # Synthesize a single sale-like listing that passes the filters.
    listings = [
        {
            "id": "x", "formattedAddress": "1 Test St", "price": 250_000,
            "propertyType": "Single Family", "bedrooms": 3, "bathrooms": 2,
            "squareFootage": 1500, "lotSize": 5000, "yearBuilt": 2000,
            "latitude": 33.7, "longitude": -112.1, "distanceToPoi": 5.0,
        }
    ]
    process_listings.add_carrying_cost(listings, poi)
    process_listings.add_predicted_rent(listings, model_path=model_path, metrics_path=metrics_path)
    process_listings.add_mortgage_coverage_ratio(listings)

    # Force selection by making the ratio fall in band, regardless of actual prediction.
    listings[0]["mortgageCoverageRatio"] = 1.0

    csv_path = tmp_path / "selected.csv"
    process_listings.export_selected_csv(listings, csv_path, model_path=model_path)

    rows = list(csv.DictReader(open(csv_path)))
    assert len(rows) == 1
    assert "topFeatures" in rows[0]
    parsed = _json.loads(rows[0]["topFeatures"])
    assert len(parsed) == process_listings.TOP_FEATURES_K
    for entry in parsed:
        assert {"feature", "shap", "value"} <= entry.keys()


def test_fmr_check_flags_high_predictions():
    """A predicted rent far above the county FMR triggers fmrFlag='high'."""
    listings = [{
        "county": "Jefferson", "state": "AL", "bedrooms": 3,
        "predictedRent": 4000,  # FY2025 Jefferson AL 3BR FMR is ~$1400
    }]
    process_listings.add_fmr_check(listings)
    assert listings[0]["fmrFlag"] == "high"
    assert listings[0]["fmrDelta"] > 0.5


def test_fmr_check_no_flag_when_county_unknown():
    listings = [{
        "county": "Atlantis", "state": "AA", "bedrooms": 3,
        "predictedRent": 4000,
    }]
    process_listings.add_fmr_check(listings)
    assert listings[0]["fmrRent"] is None
    assert listings[0]["fmrFlag"] == ""


def test_fmr_check_no_flag_when_within_band():
    listings = [{
        "county": "Jefferson", "state": "AL", "bedrooms": 3,
        "predictedRent": 1500,  # close to FY2025 FMR ~$1400
    }]
    process_listings.add_fmr_check(listings)
    assert listings[0]["fmrFlag"] == ""


def test_csv_includes_cost_estimate_flags(tmp_path):
    """Listings carry costEstimateFlags surfacing missing cost components."""
    from poi import POI, CostAssumptions

    poi = POI(
        slug="t",
        name="T",
        latitude=33.0,
        longitude=-112.0,
        radius_miles=10,
        cost_assumptions=CostAssumptions(property_tax_rate=0.01),  # only tax provided
    )

    listings = [{
        "id": "x", "formattedAddress": "1 Test St", "price": 250_000,
        "propertyType": "Single Family", "bedrooms": 3, "bathrooms": 2,
        "squareFootage": 1500, "lotSize": 5000, "yearBuilt": 2000,
        "latitude": 33.7, "longitude": -112.1, "distanceToPoi": 5.0,
        "predictedRent": 2000, "predictedRentMin": 1700, "predictedRentMax": 2400,
    }]
    process_listings.add_carrying_cost(listings, poi)
    process_listings.add_mortgage_coverage_ratio(listings)

    flags = listings[0]["costEstimateFlags"].split(",")
    assert "insurance" in flags
    assert "hoa" in flags
    assert "maintenance" in flags
    assert "vacancy_rate" in flags
    assert "property_tax" not in flags  # provided via POI rate


def test_csv_omits_top_features_when_model_path_is_none(tmp_path):
    """Backwards compatibility: skip SHAP when no model is provided."""
    listings = [{
        "id": "x", "formattedAddress": "1 Test St", "price": 250_000,
        "propertyType": "Single Family", "bedrooms": 3, "bathrooms": 2,
        "squareFootage": 1500, "lotSize": 5000, "yearBuilt": 2000,
        "latitude": 33.7, "longitude": -112.1, "distanceToPoi": 5.0,
        "monthlyMortgage": 1500, "predictedRent": 2000, "predictedRentMin": 1700,
        "predictedRentMax": 2400, "mortgageCoverageRatio": 1.13,
    }]
    csv_path = tmp_path / "selected.csv"
    process_listings.export_selected_csv(listings, csv_path)
    rows = list(csv.DictReader(open(csv_path)))
    assert len(rows) == 1
    assert "topFeatures" not in rows[0]
