"""
Samples 5 Single Family listings within budget from sale_listings_processed.json,
queries the RentCast rent estimate API for each, and compares against our
model's predicted rent.

Outputs (per-POI):
    outputs/<slug>/validation/sample_properties.json
    outputs/<slug>/validation/rent_estimate_comparison.json

Usage:
    uv run python validation/validate_rent_estimates.py
    uv run python validation/validate_rent_estimates.py --poi austin-tx
"""

import argparse
import json
import os
import random
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cli import add_poi_args, resolve_poi  # noqa: E402
from constants import BUDGET  # noqa: E402
from poi import POI  # noqa: E402

load_dotenv()
API_KEY = os.getenv("RENTCAST_API_KEY")
BASE_URL = "https://api.rentcast.io/v1"

SAMPLE_SIZE = 5
RANDOM_SEED = 42


def is_validation_candidate(listing: dict, budget: float = BUDGET) -> bool:
    price = listing.get("price")
    if price is None or price > budget:
        return False
    if listing.get("propertyType") != "Single Family":
        return False
    if listing.get("predictedRent") is None:
        return False
    return True


def fetch_rentcast_estimate(listing: dict) -> dict:
    params = {
        "address": listing["formattedAddress"],
        "propertyType": listing.get("propertyType"),
        "bedrooms": listing.get("bedrooms"),
        "bathrooms": listing.get("bathrooms"),
        "squareFootage": listing.get("squareFootage"),
    }
    params = {k: v for k, v in params.items() if v is not None}

    resp = requests.get(
        f"{BASE_URL}/avm/rent/long-term",
        headers={"X-Api-Key": API_KEY},
        params=params,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def validate_for_poi(poi: POI) -> None:
    if not API_KEY:
        sys.exit("RENTCAST_API_KEY not set in .env")

    out_dir = poi.output_dir()
    processed_path = out_dir / "sale_listings_processed.json"
    if not processed_path.exists():
        sys.exit(f"{processed_path} missing; run process_listings.py first")

    validation_dir = out_dir / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    sample_path = validation_dir / "sample_properties.json"
    comparison_path = validation_dir / "rent_estimate_comparison.json"

    with open(processed_path) as f:
        listings = json.load(f)

    candidates = [l for l in listings if is_validation_candidate(l)]
    print(f"Eligible listings: {len(candidates):,}")
    if len(candidates) < SAMPLE_SIZE:
        sys.exit(f"Only {len(candidates)} candidates available; need {SAMPLE_SIZE}")

    rng = random.Random(RANDOM_SEED)
    sample = rng.sample(candidates, SAMPLE_SIZE)

    with open(sample_path, "w") as f:
        json.dump(sample, f, indent=2)
    print(f"Saved {SAMPLE_SIZE} sampled properties → {sample_path}\n")

    comparisons = []
    for listing in sample:
        addr = listing["formattedAddress"]
        print(f"  Querying: {addr}")
        try:
            result = fetch_rentcast_estimate(listing)
        except requests.HTTPError as e:
            print(f"    API error: {e}")
            result = {}

        comparisons.append({
            "address": addr,
            "propertyType": listing.get("propertyType"),
            "bedrooms": listing.get("bedrooms"),
            "bathrooms": listing.get("bathrooms"),
            "squareFootage": listing.get("squareFootage"),
            "salePrice": listing.get("price"),
            "ourModel": {
                "predictedRentMin": listing.get("predictedRentMin"),
                "predictedRent": listing.get("predictedRent"),
                "predictedRentMax": listing.get("predictedRentMax"),
            },
            "rentcast": {
                "rentRangeLow": result.get("rentRangeLow"),
                "rent": result.get("rent"),
                "rentRangeHigh": result.get("rentRangeHigh"),
            },
        })

    with open(comparison_path, "w") as f:
        json.dump(comparisons, f, indent=2)
    print(f"\nSaved comparison → {comparison_path}\n")

    print(f"  {'Address':45s} {'Beds':>4} {'SqFt':>6} │ {'Our Min':>8} {'Our':>8} {'Our Max':>8} │ {'RC Low':>8} {'RC':>8} {'RC High':>8}")
    print("  " + "─" * 45 + "─────┬──────────────────────────────┬──────────────────────────────")
    for c in comparisons:
        addr = c["address"][:44]
        beds = int(c["bedrooms"]) if c["bedrooms"] else "?"
        sqft = int(c["squareFootage"]) if c["squareFootage"] else "?"
        om = c["ourModel"]
        rc = c["rentcast"]
        print(
            f"  {addr:45s} {str(beds):>4} {str(sqft):>6} │"
            f" ${om['predictedRentMin'] or 0:>7,} ${om['predictedRent'] or 0:>7,} ${om['predictedRentMax'] or 0:>7,} │"
            f" ${rc['rentRangeLow'] or 0:>7,} ${rc['rent'] or 0:>7,} ${rc['rentRangeHigh'] or 0:>7,}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_poi_args(parser)
    args = parser.parse_args()
    validate_for_poi(resolve_poi(args))


if __name__ == "__main__":
    main()
