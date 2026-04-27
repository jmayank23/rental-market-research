"""Carrying-cost computation for sale listings.

Each component is sourced in priority order:
  1. The listing payload (when RentCast carries the data — only HOA today)
  2. The POI's `cost_assumptions` block (user-supplied)
  3. None, with the component name added to the `missing` list

No defaults are invented. A None in `missing` means the user has not
provided that component for this POI; downstream `costEstimateFlags`
surfaces the gap rather than silently zeroing it.
"""

from __future__ import annotations

from constants import INTEREST_RATE, LOAN_TERM_MONTHS
from poi import POI


def monthly_mortgage(price: float, annual_rate: float = INTEREST_RATE) -> float:
    """Monthly payment on a 30-year fixed mortgage for the given price."""
    r = annual_rate / 12
    return round(price * (r * (1 + r) ** LOAN_TERM_MONTHS) / ((1 + r) ** LOAN_TERM_MONTHS - 1), 2)


def _listing_hoa_fee(listing: dict) -> float | None:
    hoa = listing.get("hoa")
    if isinstance(hoa, dict) and hoa.get("fee") is not None:
        return float(hoa["fee"])
    return None


def monthly_carrying_cost(listing: dict, poi: POI) -> dict:
    """Return a structured monthly-cost breakdown.

    Keys: principal_interest, property_tax, insurance, hoa, maintenance,
    vacancy_rate (the rate, applied later to predicted rent), total
    (sum of non-null cost components), missing (list of components that
    fell through to None).
    """
    price = listing.get("price")
    if not price or price <= 0:
        return {
            "principal_interest": None,
            "property_tax": None,
            "insurance": None,
            "hoa": None,
            "maintenance": None,
            "vacancy_rate": None,
            "total": None,
            "missing": ["price"],
        }

    ca = poi.cost_assumptions

    principal_interest = monthly_mortgage(price)

    if ca.property_tax_rate is not None:
        property_tax = round(price * ca.property_tax_rate / 12, 2)
    else:
        property_tax = None

    insurance = round(ca.insurance_annual / 12, 2) if ca.insurance_annual is not None else None

    listing_hoa = _listing_hoa_fee(listing)
    if listing_hoa is not None:
        hoa = round(listing_hoa, 2)
    elif ca.hoa_monthly is not None:
        hoa = round(ca.hoa_monthly, 2)
    else:
        hoa = None

    if ca.maintenance_rate_of_price is not None:
        maintenance = round(price * ca.maintenance_rate_of_price / 12, 2)
    else:
        maintenance = None

    components = {
        "principal_interest": principal_interest,
        "property_tax": property_tax,
        "insurance": insurance,
        "hoa": hoa,
        "maintenance": maintenance,
    }
    missing = [k for k, v in components.items() if v is None]
    if ca.vacancy_rate is None:
        missing.append("vacancy_rate")

    total = round(sum(v for v in components.values() if v is not None), 2)

    return {
        **components,
        "vacancy_rate": ca.vacancy_rate,
        "total": total,
        "missing": missing,
    }


def coverage_ratio(predicted_rent_min: float | None, carrying: dict) -> float | None:
    """Compute mortgageCoverageRatio honoring vacancy when the rate is supplied.

    Returns None if predicted_rent_min is missing or carrying total is 0/None.
    """
    if predicted_rent_min is None or not carrying.get("total"):
        return None
    rent = float(predicted_rent_min)
    vacancy_rate = carrying.get("vacancy_rate")
    if vacancy_rate is not None:
        rent *= (1 - vacancy_rate)
    return round(rent / carrying["total"], 3)
