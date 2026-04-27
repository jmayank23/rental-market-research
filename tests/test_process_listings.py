"""Tests for process_listings helpers."""

from process_listings import add_distance_to_poi, haversine_miles, monthly_mortgage


def test_distance_to_poi_handles_none_coords():
    listings = [{"latitude": None, "longitude": None}]
    add_distance_to_poi(listings)
    assert listings[0]["distanceToPoi"] is None


def test_distance_to_poi_zero_coords_treated_as_valid():
    """Lat/lon of 0 are valid coordinates (equator/prime meridian) — must not be falsy-skipped."""
    listings = [{"latitude": 0.0, "longitude": 0.0}]
    add_distance_to_poi(listings)
    # TSMC AZ → (0,0) is a long way; just assert it computed something numeric.
    assert listings[0]["distanceToPoi"] is not None
    assert listings[0]["distanceToPoi"] > 0


def test_distance_to_poi_real_listing(sale_listings_fixture):
    listings = [dict(l) for l in sale_listings_fixture[:5]]
    add_distance_to_poi(listings)
    for listing in listings:
        if listing.get("latitude") is not None and listing.get("longitude") is not None:
            assert listing["distanceToPoi"] is not None
            assert listing["distanceToPoi"] >= 0


def test_haversine_known_distance():
    # NYC to LA, ~2451 mi
    nyc = (40.7128, -74.0060)
    la = (34.0522, -118.2437)
    miles = haversine_miles(*nyc, *la)
    assert 2400 < miles < 2500


def test_monthly_mortgage_basic():
    # $100k loan @ 6% over 30 years ≈ $599.55
    payment = monthly_mortgage(100_000, annual_rate=0.06)
    assert 595 < payment < 605
