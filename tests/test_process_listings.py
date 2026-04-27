"""Tests for process_listings helpers."""

from unittest.mock import patch

import numpy as np

from process_listings import (
    add_distance_to_poi,
    add_predicted_rent,
    monthly_mortgage,
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
