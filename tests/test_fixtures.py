"""Fixture invariants — load shape and required fields for downstream tests."""

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURE_FILES = ["sale_listings.json", "rental_listings.json"]

REQUIRED_KEYS = {
    "id",
    "formattedAddress",
    "latitude",
    "longitude",
    "propertyType",
    "bedrooms",
    "bathrooms",
    "squareFootage",
    "price",
    "status",
}


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_fixture_loads(filename):
    payload = json.load(open(FIXTURES_DIR / filename))
    assert "listings" in payload
    assert payload["_count"] == len(payload["listings"])
    assert payload["_count"] > 0


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_fixture_shape(filename):
    listings = json.load(open(FIXTURES_DIR / filename))["listings"]
    for record in listings:
        missing = REQUIRED_KEYS - set(record.keys())
        assert not missing, f"required keys missing from {filename}: {missing}"
