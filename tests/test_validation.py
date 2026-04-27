"""Tests for the validation candidate filter."""

from validation.validate_rent_estimates import is_validation_candidate


def test_rejects_listing_over_budget():
    listing = {
        "price": 9_999_999,
        "propertyType": "Single Family",
        "predictedRent": 2000,
    }
    assert is_validation_candidate(listing, budget=500_000) is False


def test_accepts_listing_under_budget():
    listing = {
        "price": 400_000,
        "propertyType": "Single Family",
        "predictedRent": 2000,
    }
    assert is_validation_candidate(listing, budget=500_000) is True


def test_rejects_non_single_family():
    listing = {
        "price": 400_000,
        "propertyType": "Condo",
        "predictedRent": 2000,
    }
    assert is_validation_candidate(listing) is False


def test_rejects_when_predicted_rent_missing():
    listing = {
        "price": 400_000,
        "propertyType": "Single Family",
        "predictedRent": None,
    }
    assert is_validation_candidate(listing) is False


def test_rejects_when_price_missing():
    listing = {
        "propertyType": "Single Family",
        "predictedRent": 2000,
    }
    assert is_validation_candidate(listing) is False


def test_does_not_check_legacy_within_budget_key():
    """Regression: previous code keyed on a `withinBudget` field that was never set."""
    listing = {
        "price": 400_000,
        "propertyType": "Single Family",
        "predictedRent": 2000,
        # No `withinBudget` field; should still be accepted.
    }
    assert is_validation_candidate(listing) is True
