"""Fixture invariants — guards against accidentally committing PII."""

import json
import re
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURE_FILES = ["sale_listings.json", "rental_listings.json"]

PHONE_RE = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
URL_RE = re.compile(r"https?://[^\s\"']+")

REQUIRED_KEYS = {
    "id",
    "formattedAddress",
    "city",
    "state",
    "zipCode",
    "latitude",
    "longitude",
    "propertyType",
    "bedrooms",
    "bathrooms",
    "squareFootage",
    "price",
    "status",
}

FORBIDDEN_KEYS = {"listingAgent", "listingOffice", "builder", "mlsName", "mlsNumber"}


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_fixture_loads(filename):
    payload = json.load(open(FIXTURES_DIR / filename))
    assert "listings" in payload
    assert payload["_count"] == len(payload["listings"])
    assert payload["_count"] > 0


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_no_pii_in_committed_fixtures(filename):
    blob = (FIXTURES_DIR / filename).read_text()
    assert not PHONE_RE.search(blob), f"phone number leaked into {filename}"
    assert not EMAIL_RE.search(blob), f"email leaked into {filename}"
    assert not URL_RE.search(blob), f"URL leaked into {filename}"
    assert "Test City" in blob
    assert "85000" in blob


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_fixture_shape(filename):
    listings = json.load(open(FIXTURES_DIR / filename))["listings"]
    for record in listings:
        missing = REQUIRED_KEYS - set(record.keys())
        assert not missing, f"required keys missing from {filename}: {missing}"
        leaked = FORBIDDEN_KEYS & set(record.keys())
        assert not leaked, f"forbidden contact keys present in {filename}: {leaked}"
        assert record["city"] == "Test City"
        assert record["zipCode"] == "85000"
        assert record["formattedAddress"].startswith(record["addressLine1"])
