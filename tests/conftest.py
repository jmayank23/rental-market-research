import json
from pathlib import Path

import pandas as pd
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load(name: str) -> list[dict]:
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)["listings"]


@pytest.fixture(scope="session")
def sale_listings_fixture() -> list[dict]:
    return _load("sale_listings.json")


@pytest.fixture(scope="session")
def rental_listings_fixture() -> list[dict]:
    return _load("rental_listings.json")


@pytest.fixture(scope="session")
def tiny_rental_df(rental_listings_fixture) -> pd.DataFrame:
    return pd.DataFrame(rental_listings_fixture[:10])
