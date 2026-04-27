"""Smoke tests: every project module imports without side effects."""

import importlib

MODULES = [
    "constants",
    "fetch_listings",
    "process_listings",
    "rent_estimation_utils",
    "rent_model",
]


def test_imports():
    for name in MODULES:
        importlib.import_module(name)
