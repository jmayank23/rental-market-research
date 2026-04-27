"""Score sale listings against a trained rent model and export the shortlist.

Outputs (per-POI):
    outputs/<slug>/sale_listings_processed.json — every listing enriched
    outputs/<slug>/selected_properties.csv      — listings passing the filters

Usage:
    uv run python process_listings.py
    uv run python process_listings.py --poi austin-tx
"""

import argparse
import json
import math
from pathlib import Path

import joblib
import pandas as pd

from cli import add_poi_args, resolve_poi
from constants import (
    BEDROOMS,
    BUDGET,
    INTEREST_RATE,
    LOAN_TERM_MONTHS,
    MORTGAGE_COVERAGE_RANGE,
    PROPERTY_TYPES,
    YEAR_MIN,
)
from poi import POI
from rent_estimation_utils import FEATURES, REQUIRED_FEATURES


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return round(2 * R * math.asin(math.sqrt(a)), 2)


def monthly_mortgage(price: float, annual_rate: float = INTEREST_RATE) -> float:
    """Return the monthly payment on a 30-year fixed mortgage for the given price."""
    r = annual_rate / 12
    return round(price * (r * (1 + r) ** LOAN_TERM_MONTHS) / ((1 + r) ** LOAN_TERM_MONTHS - 1), 2)


def add_monthly_mortgage(listings: list[dict]) -> list[dict]:
    for listing in listings:
        price = listing.get("price")
        listing["monthlyMortgage"] = monthly_mortgage(price) if price else None
    return listings


def is_selected(listing: dict) -> bool:
    price = listing.get("price")
    if price is None or price > BUDGET:
        return False
    if listing.get("propertyType") not in PROPERTY_TYPES:
        return False
    if listing.get("bedrooms") not in BEDROOMS:
        return False
    year = listing.get("yearBuilt")
    if year is None or year < YEAR_MIN:
        return False
    ratio = listing.get("mortgageCoverageRatio")
    if ratio is None or not (MORTGAGE_COVERAGE_RANGE[0] <= ratio <= MORTGAGE_COVERAGE_RANGE[1]):
        return False
    return True


def _load_band(metrics_path: str | Path) -> tuple[float, float]:
    """Return (low_offset, high_offset) so bounds = pred * (1 + offset).

    Prefers val-set residual quantiles if recorded; falls back to ±MAPE for
    older metrics files.
    """
    with open(metrics_path) as f:
        record = json.load(f)
    quantiles = record.get("residual_quantiles")
    if quantiles is not None:
        return quantiles["q10"], quantiles["q90"]
    mape = record["val_metrics"]["mape"] / 100
    return -mape, mape


def add_predicted_rent(
    listings: list[dict],
    model_path: str | Path = "rent_model.joblib",
    metrics_path: str | Path = "rent_model_metrics.json",
) -> list[dict]:
    pipeline = joblib.load(model_path)
    low_offset, high_offset = _load_band(metrics_path)

    df = pd.DataFrame(listings)
    for col in FEATURES:
        if col not in df.columns:
            df[col] = None

    has_features = df[REQUIRED_FEATURES].notna().all(axis=1).to_numpy()
    feat_df = df[FEATURES]

    raw_preds = pipeline.predict(feat_df[has_features]) if has_features.any() else []
    pred_iter = iter(raw_preds)

    for listing, ok in zip(listings, has_features):
        if not ok:
            listing["predictedRent"] = None
            listing["predictedRentMin"] = None
            listing["predictedRentMax"] = None
            continue
        p = float(next(pred_iter))
        listing["predictedRent"] = round(p)
        listing["predictedRentMin"] = max(0, round(p * (1 + low_offset)))
        listing["predictedRentMax"] = max(0, round(p * (1 + high_offset)))

    return listings


def add_distance_to_poi(listings: list[dict], poi_lat: float, poi_lon: float) -> list[dict]:
    for listing in listings:
        lat, lon = listing.get("latitude"), listing.get("longitude")
        if lat is not None and lon is not None:
            listing["distanceToPoi"] = haversine_miles(lat, lon, poi_lat, poi_lon)
        else:
            listing["distanceToPoi"] = None
    return listings


def add_mortgage_coverage_ratio(listings: list[dict]) -> list[dict]:
    for listing in listings:
        rent_min = listing.get("predictedRentMin")
        mortgage = listing.get("monthlyMortgage")
        if rent_min is not None and mortgage:
            listing["mortgageCoverageRatio"] = round(rent_min / mortgage, 3)
        else:
            listing["mortgageCoverageRatio"] = None
    return listings


def export_selected_csv(listings: list[dict], output_path: str | Path) -> None:
    selected = [l for l in listings if is_selected(l)]

    high, low = MORTGAGE_COVERAGE_RANGE[1], MORTGAGE_COVERAGE_RANGE[0]
    excluded_above = sum(1 for l in listings if (l.get("mortgageCoverageRatio") or 0) > high)
    excluded_below = sum(
        1 for l in listings
        if l.get("mortgageCoverageRatio") is not None and l["mortgageCoverageRatio"] < low
    )
    print(
        f"  MORTGAGE_COVERAGE_RANGE filter: "
        f"{excluded_below:,} below {low}, {excluded_above:,} above {high}"
    )

    df = pd.DataFrame(selected)
    df = df.sort_values("mortgageCoverageRatio", ascending=False)
    df.to_csv(output_path, index=False)
    print(f"Exported {len(df):,} selected listings → {output_path}")


def process_sale_listings(
    input_path: str | Path,
    output_path: str | Path,
    model_path: str | Path,
    metrics_path: str | Path,
    csv_path: str | Path,
    poi_lat: float,
    poi_lon: float,
) -> None:
    with open(input_path) as f:
        listings = json.load(f)

    listings = add_monthly_mortgage(listings)
    listings = add_predicted_rent(listings, model_path=model_path, metrics_path=metrics_path)
    listings = add_distance_to_poi(listings, poi_lat=poi_lat, poi_lon=poi_lon)
    listings = add_mortgage_coverage_ratio(listings)

    with open(output_path, "w") as f:
        json.dump(listings, f, indent=2)

    total = len(listings)
    selected = sum(1 for l in listings if is_selected(l))
    with_rent = sum(1 for l in listings if l.get("predictedRent") is not None)
    print(f"Processed {total:,} listings — {selected:,} selected — {with_rent:,} with rent estimate")

    export_selected_csv(listings, csv_path)


def process_for_poi(poi: POI) -> None:
    out_dir = poi.output_dir()
    process_sale_listings(
        input_path=out_dir / "sale_listings.json",
        output_path=out_dir / "sale_listings_processed.json",
        model_path=out_dir / "rent_model.joblib",
        metrics_path=out_dir / "rent_model_metrics.json",
        csv_path=out_dir / "selected_properties.csv",
        poi_lat=poi.latitude,
        poi_lon=poi.longitude,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_poi_args(parser)
    args = parser.parse_args()
    process_for_poi(resolve_poi(args))


if __name__ == "__main__":
    main()
