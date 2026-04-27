"""
Builds anonymized test fixtures from real RentCast data.

Pulls a small slice of sale and rental listings within a tight radius of the
default POI, strips all PII (addresses, agents, offices, MLS numbers, history),
jitters lat/lon by ~100m, and writes them to tests/fixtures/.

The committed fixtures contain only model-relevant numeric / structural fields
plus synthetic addresses, so CI can run without an API key and contributors
don't leak real listing contact info.

Usage:
    uv run python scripts/build_test_fixtures.py
"""

import hashlib
import json
import os
import random
import re
import sys
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
JITTER_DEG = 0.001  # ~100m
SEED = 42

KEEP_TOP_LEVEL = {
    "state",
    "stateFips",
    "countyFips",
    "propertyType",
    "bedrooms",
    "bathrooms",
    "squareFootage",
    "lotSize",
    "yearBuilt",
    "status",
    "price",
    "listingType",
    "listedDate",
    "removedDate",
    "createdDate",
    "lastSeenDate",
    "daysOnMarket",
}

PII_PATTERNS = [
    re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),  # phone
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),  # email
    re.compile(r"https?://[^\s\"']+"),  # website
]


def _hash_id(raw: str, kind: str) -> str:
    h = hashlib.sha256(raw.encode()).hexdigest()[:10]
    return f"{kind}-id{h}"


def _jitter(value: float, rng: random.Random) -> float:
    return round(value + rng.uniform(-JITTER_DEG, JITTER_DEG), 6)


def anonymize(record: dict, kind: str, idx: int, rng: random.Random) -> dict:
    """Allow-list anonymization: keep only safe fields, synthesize the rest."""
    out: dict = {k: record.get(k) for k in KEEP_TOP_LEVEL if k in record}

    raw_id = record.get("id") or record.get("formattedAddress") or f"{kind}-{idx}"
    out["id"] = _hash_id(raw_id, kind)

    fake_num = 100 + idx
    out["formattedAddress"] = f"{fake_num} Test St, Test City, AZ 85000"
    out["addressLine1"] = f"{fake_num} Test St"
    out["addressLine2"] = None
    out["city"] = "Test City"
    out["zipCode"] = "85000"
    out["county"] = "Test County"

    lat = record.get("latitude")
    lon = record.get("longitude")
    out["latitude"] = _jitter(lat, rng) if lat is not None else None
    out["longitude"] = _jitter(lon, rng) if lon is not None else None

    hoa = record.get("hoa")
    if isinstance(hoa, dict) and "fee" in hoa:
        out["hoa"] = {"fee": hoa["fee"]}

    return out


def _scan_for_pii(blob: str, originals: list[str]) -> list[str]:
    """Return list of leaks detected. Empty list = clean."""
    leaks: list[str] = []
    for pat in PII_PATTERNS:
        for m in pat.findall(blob):
            leaks.append(f"pattern:{pat.pattern}:{m}")
    for raw in originals:
        if raw and len(raw) > 6 and raw in blob:
            leaks.append(f"raw:{raw[:40]}")
    return leaks


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
            import time

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


def build(endpoint: str, kind: str, output_path: Path) -> None:
    print(f"Fetching {kind} listings from {endpoint}...")
    raw = fetch(endpoint)
    print(f"  Got {len(raw)} records")

    rng = random.Random(SEED)

    originals: list[str] = []
    for r in raw:
        for key in ("formattedAddress", "addressLine1", "city", "zipCode", "mlsNumber"):
            v = r.get(key)
            if isinstance(v, str):
                originals.append(v)
        for office_key in ("listingAgent", "listingOffice", "builder"):
            office = r.get(office_key) or {}
            for f in ("name", "phone", "email", "website"):
                v = office.get(f) if isinstance(office, dict) else None
                if isinstance(v, str):
                    originals.append(v)

    anonymized = [anonymize(r, kind, i, rng) for i, r in enumerate(raw)]

    blob = json.dumps(anonymized, indent=2)
    leaks = _scan_for_pii(blob, originals)
    if leaks:
        print("ANONYMIZATION FAILED — leaks detected:")
        for leak in leaks[:10]:
            print(f"  {leak}")
            tag = leak.split(":", 2)[-1]
            idx = blob.find(tag)
            if idx >= 0:
                print(f"    context: ...{blob[max(0,idx-60):idx+len(tag)+20]}...")
        sys.exit(1)

    payload = {
        "_generated_at": datetime.now(timezone.utc).isoformat(),
        "_source": endpoint,
        "_count": len(anonymized),
        "listings": anonymized,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Wrote {output_path} ({len(anonymized)} records)")


def main() -> None:
    if not API_KEY:
        sys.exit("RENTCAST_API_KEY not set in environment or .env")

    build("/listings/sale", "sale", FIXTURES_DIR / "sale_listings.json")
    build("/listings/rental/long-term", "rental", FIXTURES_DIR / "rental_listings.json")
    print("\nFixtures built. Re-run only if the source schema changes.")


if __name__ == "__main__":
    main()
