"""Tests for the shared --poi CLI surface."""

import argparse

import pytest

from cli import add_poi_args, resolve_poi


def _parse(*argv):
    parser = argparse.ArgumentParser()
    add_poi_args(parser)
    return parser.parse_args(list(argv))


def test_resolves_default_poi_when_no_flags():
    poi = resolve_poi(_parse())
    assert poi.slug == "tsmc-az"


def test_resolves_named_poi():
    poi = resolve_poi(_parse("--poi", "tsmc-az"))
    assert poi.slug == "tsmc-az"


def test_overrides_via_lat_lon_flags():
    poi = resolve_poi(_parse(
        "--poi-lat", "30.27",
        "--poi-lon", "-97.74",
        "--poi-radius", "20",
        "--poi-name", "Austin TX",
    ))
    assert poi.slug == "austin-tx"
    assert poi.name == "Austin TX"
    assert poi.latitude == pytest.approx(30.27)
    assert poi.longitude == pytest.approx(-97.74)
    assert poi.radius_miles == 20


def test_explicit_slug_overrides_derived():
    poi = resolve_poi(_parse(
        "--poi-lat", "30.27",
        "--poi-lon", "-97.74",
        "--poi-radius", "20",
        "--poi-name", "Austin TX",
        "--poi-slug", "atx-test",
    ))
    assert poi.slug == "atx-test"


def test_partial_override_rejected():
    with pytest.raises(SystemExit):
        resolve_poi(_parse("--poi-lat", "30.27"))


def test_unknown_named_poi_raises():
    with pytest.raises(FileNotFoundError):
        resolve_poi(_parse("--poi", "nowhere-bay"))
