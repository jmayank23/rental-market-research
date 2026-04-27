"""
Builds test fixtures from real RentCast data.

Pulls a small slice of sale and rental listings within a tight radius of the
default POI and writes them to tests/fixtures/. Use small limits to avoid
burning API credits.

Usage:
    uv run python scripts/build_test_fixtures.py
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = ROOT / "tests" / "fixtures"

load_dotenv(ROOT / ".env")
API_KEY = os.environ.get("RENTCAST_API_KEY", "")
BASE_URL = "https://api.rentcast.io/v1"

POI_LAT = 33.775196
POI_LON = -112.160449
RADIUS_MILES = 5
LIMIT = 50


def fetch(endpoint: str) -> list[dict]:
    headers = {"Accept": "application/json", "X-Api-Key": API_KEY}
    params = {
        "latitude": POI_LAT,
        "longitude": POI_LON,
        "radius": RADIUS_MILES,
        "status": "Active",
        "limit": LIMIT,
        "offset": 0,
    }
    last_error: Exception | None = None
    for attempt, backoff in enumerate([0, 2, 4, 8]):
        if backoff:
            time.sleep(backoff)
        try:
            resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status is not None and status < 500 and status != 429:
                raise
            last_error = e
            print(f"  attempt {attempt + 1} failed ({status or type(e).__name__}); retrying...")
    assert last_error is not None
    raise last_error


def build(endpoint: str, output_path: Path) -> None:
    print(f"Fetching {endpoint}...")
    listings = fetch(endpoint)
    print(f"  Got {len(listings)} records")

    payload = {
        "_generated_at": datetime.now(timezone.utc).isoformat(),
        "_source": endpoint,
        "_count": len(listings),
        "listings": listings,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Wrote {output_path}")


def main() -> None:
    if not API_KEY:
        sys.exit("RENTCAST_API_KEY not set in environment or .env")

    build("/listings/sale", FIXTURES_DIR / "sale_listings.json")
    build("/listings/rental/long-term", FIXTURES_DIR / "rental_listings.json")
    print("\nFixtures built. Re-run only if the source schema changes.")


if __name__ == "__main__":
    main()
