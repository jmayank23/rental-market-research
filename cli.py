"""Shared CLI surface for resolving a POI from argparse flags."""

from __future__ import annotations

import argparse

from poi import POI, load_named_poi, slugify

DEFAULT_POI_SLUG = "tsmc-az"


def add_poi_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--poi",
        default=None,
        help=f"Slug of pois/<slug>.json. Default: {DEFAULT_POI_SLUG}",
    )
    parser.add_argument("--poi-lat", type=float, default=None, help="Override POI latitude")
    parser.add_argument("--poi-lon", type=float, default=None, help="Override POI longitude")
    parser.add_argument(
        "--poi-radius",
        type=float,
        default=None,
        help="Override POI search radius (miles)",
    )
    parser.add_argument("--poi-name", default=None, help="Display name when overriding")
    parser.add_argument(
        "--poi-slug",
        default=None,
        help="Filesystem slug when overriding (auto-derived from --poi-name otherwise)",
    )


def resolve_poi(args: argparse.Namespace) -> POI:
    """Pick the POI source. Overrides take precedence; otherwise load by slug."""
    overrides = (args.poi_lat, args.poi_lon, args.poi_radius)
    if any(v is not None for v in overrides):
        if any(v is None for v in overrides):
            raise SystemExit(
                "When overriding the POI you must supply --poi-lat, --poi-lon, and --poi-radius together."
            )
        name = args.poi_name or "Custom POI"
        slug = args.poi_slug or slugify(name)
        return POI(
            slug=slug,
            name=name,
            latitude=args.poi_lat,
            longitude=args.poi_lon,
            radius_miles=args.poi_radius,
        )
    return load_named_poi(args.poi or DEFAULT_POI_SLUG)
