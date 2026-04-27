import argparse
import json
import os
import time

import requests
from dotenv import load_dotenv

from cli import add_poi_args, resolve_poi
from poi import POI

load_dotenv()

API_KEY = os.environ.get("RENTCAST_API_KEY", "")
BASE_URL = "https://api.rentcast.io/v1"
PAGE_SIZE = 500
REQUEST_TIMEOUT = 30
RETRY_BACKOFFS = (0, 2, 4, 8)
RETRY_STATUSES = {429, 500, 502, 503, 504}


def _request_with_retry(url: str, headers: dict, params: dict) -> requests.Response:
    last_error: Exception | None = None
    for attempt, backoff in enumerate(RETRY_BACKOFFS):
        if backoff:
            time.sleep(backoff)
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            if status not in RETRY_STATUSES:
                raise
            last_error = e
            print(f"  attempt {attempt + 1} failed (HTTP {status}); retrying...")
        except (requests.ConnectionError, requests.Timeout) as e:
            last_error = e
            print(f"  attempt {attempt + 1} failed ({type(e).__name__}); retrying...")
    assert last_error is not None
    raise last_error


def fetch_all_listings(endpoint: str, params: dict) -> list:
    headers = {"Accept": "application/json", "X-Api-Key": API_KEY}
    url = f"{BASE_URL}{endpoint}"
    all_results: list = []

    first_params = {**params, "limit": PAGE_SIZE, "offset": 0, "includeTotalCount": "true"}
    response = _request_with_retry(url, headers, first_params)

    batch = response.json()
    all_results.extend(batch)

    total_header = response.headers.get("X-Total-Count")
    if total_header is None:
        print(f"  WARNING: X-Total-Count missing; assuming single page of {len(batch)} records")
        total = len(batch)
    else:
        total = int(total_header)
    print(f"  Total available: {total}, fetched: {len(batch)}")

    offset = PAGE_SIZE
    while offset < total and len(batch) == PAGE_SIZE:
        page_params = {**params, "limit": PAGE_SIZE, "offset": offset}
        response = _request_with_retry(url, headers, page_params)

        batch = response.json()
        all_results.extend(batch)
        print(f"  Fetched {len(all_results)}/{total}")

        offset += PAGE_SIZE
        if len(batch) < PAGE_SIZE:
            break
        time.sleep(0.25)

    return all_results


def fetch_for_poi(poi: POI) -> None:
    if not API_KEY:
        raise ValueError("RENTCAST_API_KEY environment variable not set")

    out_dir = poi.output_dir()
    location_params = {
        "latitude": poi.latitude,
        "longitude": poi.longitude,
        "radius": poi.radius_miles,
        "status": "Active",
    }

    print(f"POI: {poi.name} ({poi.slug}) — {poi.radius_miles} mi @ ({poi.latitude}, {poi.longitude})")

    print("Fetching sale listings...")
    sale_listings = fetch_all_listings("/listings/sale", location_params)
    sale_path = out_dir / "sale_listings.json"
    with open(sale_path, "w") as f:
        json.dump(sale_listings, f, indent=2)
    print(f"Saved {len(sale_listings)} sale listings → {sale_path}\n")

    print("Fetching rental listings...")
    rental_listings = fetch_all_listings("/listings/rental/long-term", location_params)
    rental_path = out_dir / "rental_listings.json"
    with open(rental_path, "w") as f:
        json.dump(rental_listings, f, indent=2)
    print(f"Saved {len(rental_listings)} rental listings → {rental_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_poi_args(parser)
    args = parser.parse_args()
    poi = resolve_poi(args)
    fetch_for_poi(poi)


if __name__ == "__main__":
    main()
