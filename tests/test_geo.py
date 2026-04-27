"""Tests for the haversine helper."""

import pytest

from geo import haversine_miles


def test_haversine_known_distance_nyc_la():
    nyc = (40.7128, -74.0060)
    la = (34.0522, -118.2437)
    miles = haversine_miles(*nyc, *la)
    assert 2400 < miles < 2500


def test_haversine_zero_distance():
    p = (33.775196, -112.160449)
    assert haversine_miles(*p, *p) == 0.0


def test_haversine_treats_zero_as_valid_coord():
    """Coordinates of 0 are valid (equator/prime meridian) and must compute a real distance."""
    miles = haversine_miles(0.0, 0.0, 0.0, 1.0)
    # 1 deg longitude at the equator ≈ 69.17 miles
    assert 68 < miles < 70
