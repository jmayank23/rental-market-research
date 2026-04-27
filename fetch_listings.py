import json
import os
import time

import requests
from dotenv import load_dotenv

from constants import LATITUDE, LONGITUDE, RADIUS

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


def main():
    if not API_KEY:
        raise ValueError("RENTCAST_API_KEY environment variable not set")

    location_params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "radius": RADIUS,
        "status": "Active",
    }

    print("Fetching sale listings...")
    sale_listings = fetch_all_listings("/listings/sale", location_params)
    with open("sale_listings.json", "w") as f:
        json.dump(sale_listings, f, indent=2)
    print(f"Saved {len(sale_listings)} sale listings to sale_listings.json\n")

    print("Fetching rental listings...")
    rental_listings = fetch_all_listings("/listings/rental/long-term", location_params)
    with open("rental_listings.json", "w") as f:
        json.dump(rental_listings, f, indent=2)
    print(f"Saved {len(rental_listings)} rental listings to rental_listings.json")


if __name__ == "__main__":
    main()
