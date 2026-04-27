"""Tests for POI dataclass + loaders."""

import json

import pytest

from poi import POI, load_named_poi, slugify


def _valid_kwargs(**overrides):
    base = {
        "slug": "tsmc-az",
        "name": "TSMC Arizona Plant",
        "latitude": 33.775196,
        "longitude": -112.160449,
        "radius_miles": 15.0,
    }
    base.update(overrides)
    return base


def test_manual_poi_round_trip():
    poi = POI(**_valid_kwargs())
    assert poi.slug == "tsmc-az"
    assert poi.radius_miles == 15.0


def test_default_poi_file_loads():
    """The shipped default POI should load via the public API."""
    poi = load_named_poi("tsmc-az")
    assert poi.slug == "tsmc-az"
    assert poi.latitude == pytest.approx(33.775196)
    assert poi.longitude == pytest.approx(-112.160449)
    assert poi.radius_miles == 15


def test_json_file_poi_loads(tmp_path):
    path = tmp_path / "place.json"
    path.write_text(json.dumps({
        "slug": "place-x",
        "name": "Test Place",
        "latitude": 40.0,
        "longitude": -75.0,
        "radius_miles": 10,
    }))
    poi = POI.from_json_file(path)
    assert poi.name == "Test Place"
    assert poi.radius_miles == 10


@pytest.mark.parametrize("bad_slug", ["TSMC", "with space", "a/b", "-leading", ""])
def test_slug_must_be_filesystem_safe(bad_slug):
    with pytest.raises(ValueError):
        POI(**_valid_kwargs(slug=bad_slug))


@pytest.mark.parametrize("lat", [-91, 91])
def test_latitude_validated(lat):
    with pytest.raises(ValueError):
        POI(**_valid_kwargs(latitude=lat))


@pytest.mark.parametrize("lon", [-181, 181])
def test_longitude_validated(lon):
    with pytest.raises(ValueError):
        POI(**_valid_kwargs(longitude=lon))


@pytest.mark.parametrize("radius", [0, -5, 101])
def test_radius_validated(radius):
    with pytest.raises(ValueError):
        POI(**_valid_kwargs(radius_miles=radius))


def test_load_named_poi_missing_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("poi.POIS_DIR", tmp_path)
    with pytest.raises(FileNotFoundError):
        load_named_poi("does-not-exist")


@pytest.mark.parametrize("text,expected", [
    ("TSMC Arizona Plant", "tsmc-arizona-plant"),
    ("Austin TX!", "austin-tx"),
    ("  weird   spacing  ", "weird-spacing"),
])
def test_slugify(text, expected):
    assert slugify(text) == expected


def test_output_dir_creates_directory(tmp_path, monkeypatch):
    monkeypatch.setattr("poi.OUTPUTS_DIR", tmp_path)
    poi = POI(**_valid_kwargs(slug="my-place"))
    out = poi.output_dir()
    assert out.exists()
    assert out.name == "my-place"


def test_poi_loads_with_no_cost_assumptions():
    """No cost_assumptions block → all components default to None (will be flagged)."""
    poi = POI(**_valid_kwargs())
    assert poi.cost_assumptions.property_tax_rate is None
    assert poi.cost_assumptions.hoa_monthly is None


def test_poi_loads_cost_assumptions_from_json(tmp_path):
    path = tmp_path / "place.json"
    path.write_text(json.dumps({
        "slug": "place-x",
        "name": "Test Place",
        "latitude": 40.0,
        "longitude": -75.0,
        "radius_miles": 10,
        "cost_assumptions": {
            "property_tax_rate": 0.0072,
            "insurance_annual": 1200,
            "vacancy_rate": 0.06,
        },
    }))
    poi = POI.from_json_file(path)
    assert poi.cost_assumptions.property_tax_rate == 0.0072
    assert poi.cost_assumptions.insurance_annual == 1200
    assert poi.cost_assumptions.hoa_monthly is None  # not provided
