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


def fetch_all_listings(endpoint: str, params: dict) -> list:
    headers = {"Accept": "application/json", "X-Api-Key": API_KEY}
    all_results = []
    offset = 0

    # First request includes total count
    first_params = {**params, "limit": PAGE_SIZE, "offset": 0, "includeTotalCount": "true"}
    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=first_params)
    response.raise_for_status()

    batch = response.json()
    all_results.extend(batch)

    total = int(response.headers.get("X-Total-Count", len(batch)))
    print(f"  Total available: {total}, fetched: {len(batch)}")

    offset = PAGE_SIZE
    while offset < total and len(batch) == PAGE_SIZE:
        page_params = {**params, "limit": PAGE_SIZE, "offset": offset}
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=page_params)
        response.raise_for_status()

        batch = response.json()
        all_results.extend(batch)
        print(f"  Fetched {len(all_results)}/{total}")

        offset += PAGE_SIZE
        if len(batch) < PAGE_SIZE:
            break
        time.sleep(0.25)  # avoid hammering the API

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
