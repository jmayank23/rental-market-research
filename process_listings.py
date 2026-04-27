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
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

from cli import add_poi_args, resolve_poi
from constants import (
    BEDROOMS,
    BUDGET,
    MORTGAGE_COVERAGE_RANGE,
    PROPERTY_TYPES,
    YEAR_MIN,
)
from finance import coverage_ratio, monthly_carrying_cost, monthly_mortgage
from geo import haversine_miles
from poi import POI
from rent_estimation_utils import CAT_FEATURES, FEATURES, REQUIRED_FEATURES

TOP_FEATURES_K = 3


def add_carrying_cost(listings: list[dict], poi: POI) -> list[dict]:
    """Attach a structured carrying-cost breakdown + flat helpers to each listing.

    Components missing from both the listing payload and the POI's
    cost_assumptions are recorded as null and surfaced via costEstimateFlags.
    """
    for listing in listings:
        breakdown = monthly_carrying_cost(listing, poi)
        listing["carryingCost"] = breakdown
        listing["monthlyMortgage"] = breakdown.get("principal_interest")
        listing["carryingCostTotal"] = breakdown.get("total")
        listing["costEstimateFlags"] = ",".join(breakdown.get("missing", []))
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
        carrying = listing.get("carryingCost")
        if carrying is None:
            mortgage = listing.get("monthlyMortgage")
            if rent_min is not None and mortgage:
                listing["mortgageCoverageRatio"] = round(rent_min / mortgage, 3)
            else:
                listing["mortgageCoverageRatio"] = None
            continue
        listing["mortgageCoverageRatio"] = coverage_ratio(rent_min, carrying)
    return listings


def _attach_top_features(selected: list[dict], model_path: str | Path, k: int = TOP_FEATURES_K) -> None:
    """Attach a `topFeatures` JSON blob to each selected listing via SHAP.

    Each entry is the top-k transformed-feature contributions sorted by |SHAP|,
    in log-rent space, with the originating raw value.
    """
    if not selected:
        return
    estimator = joblib.load(model_path)
    inner = estimator.regressor_
    preprocessor = inner.named_steps["preprocessor"]
    model = inner.named_steps["model"]

    df = pd.DataFrame(selected)
    for col in FEATURES:
        if col not in df.columns:
            df[col] = None
    feat_df = df[FEATURES]

    transformed = preprocessor.transform(feat_df)
    transformed_names = preprocessor.get_feature_names_out()

    explainer = shap.TreeExplainer(model)
    raw = explainer.shap_values(transformed)
    if isinstance(raw, list):
        raw = raw[0]
    shap_values = np.asarray(raw)

    def _orig_feature(transformed_name: str) -> str:
        key = transformed_name.split("__", 1)[1] if "__" in transformed_name else transformed_name
        for orig in CAT_FEATURES:
            if key.startswith(f"{orig}_"):
                return orig
        return key

    for i, listing in enumerate(selected):
        order = np.argsort(-np.abs(shap_values[i]))[:k]
        top: list[dict] = []
        for j in order:
            orig = _orig_feature(transformed_names[j])
            value = listing.get(orig)
            top.append({
                "feature": orig,
                "shap": round(float(shap_values[i, j]), 4),
                "value": value,
            })
        listing["topFeatures"] = json.dumps(top)


def export_selected_csv(
    listings: list[dict],
    output_path: str | Path,
    model_path: str | Path | None = None,
) -> None:
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

    if model_path is not None:
        _attach_top_features(selected, model_path)

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
    poi: POI,
) -> None:
    with open(input_path) as f:
        listings = json.load(f)

    listings = add_carrying_cost(listings, poi)
    listings = add_distance_to_poi(listings, poi_lat=poi.latitude, poi_lon=poi.longitude)
    listings = add_predicted_rent(listings, model_path=model_path, metrics_path=metrics_path)
    listings = add_mortgage_coverage_ratio(listings)

    with open(output_path, "w") as f:
        json.dump(listings, f, indent=2)

    total = len(listings)
    selected = sum(1 for l in listings if is_selected(l))
    with_rent = sum(1 for l in listings if l.get("predictedRent") is not None)
    print(f"Processed {total:,} listings — {selected:,} selected — {with_rent:,} with rent estimate")
    _summarize_cost_flags(listings)

    export_selected_csv(listings, csv_path, model_path=model_path)


def _summarize_cost_flags(listings: list[dict]) -> None:
    """Tell the user which carrying-cost components were never available."""
    counts: dict[str, int] = {}
    for l in listings:
        for flag in (l.get("carryingCost") or {}).get("missing") or []:
            counts[flag] = counts.get(flag, 0) + 1
    if counts:
        summary = ", ".join(f"{k}={v:,}" for k, v in sorted(counts.items()))
        print(f"  costEstimateFlags (count of listings missing each): {summary}")


def process_for_poi(poi: POI) -> None:
    out_dir = poi.output_dir()
    process_sale_listings(
        input_path=out_dir / "sale_listings.json",
        output_path=out_dir / "sale_listings_processed.json",
        model_path=out_dir / "rent_model.joblib",
        metrics_path=out_dir / "rent_model_metrics.json",
        csv_path=out_dir / "selected_properties.csv",
        poi=poi,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_poi_args(parser)
    args = parser.parse_args()
    process_for_poi(resolve_poi(args))


if __name__ == "__main__":
    main()
