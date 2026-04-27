"""Tests for finance.monthly_carrying_cost — listing-first / POI-fallback / null-flag."""

import pytest

from finance import coverage_ratio, monthly_carrying_cost, monthly_mortgage
from poi import POI, CostAssumptions


def _poi(**ca_kwargs):
    return POI(
        slug="test",
        name="Test",
        latitude=33.0,
        longitude=-112.0,
        radius_miles=10,
        cost_assumptions=CostAssumptions(**ca_kwargs),
    )


def test_monthly_mortgage_basic():
    # $100k @ 6% / 30y ≈ $599.55
    payment = monthly_mortgage(100_000, annual_rate=0.06)
    assert 595 < payment < 605


def test_principal_interest_always_present_when_price_exists():
    listing = {"price": 250_000}
    out = monthly_carrying_cost(listing, _poi())
    assert out["principal_interest"] is not None
    assert out["principal_interest"] > 0


def test_no_price_returns_total_none_with_flag():
    out = monthly_carrying_cost({}, _poi())
    assert out["total"] is None
    assert "price" in out["missing"]


def test_uses_listing_hoa_when_present():
    listing = {"price": 250_000, "hoa": {"fee": 350}}
    out = monthly_carrying_cost(listing, _poi(hoa_monthly=100))
    assert out["hoa"] == 350.0  # listing wins over POI fallback
    assert "hoa" not in out["missing"]


def test_falls_back_to_poi_hoa():
    listing = {"price": 250_000}
    out = monthly_carrying_cost(listing, _poi(hoa_monthly=125))
    assert out["hoa"] == 125.0
    assert "hoa" not in out["missing"]


def test_hoa_missing_when_neither_source_provides_it():
    out = monthly_carrying_cost({"price": 250_000}, _poi())
    assert out["hoa"] is None
    assert "hoa" in out["missing"]


def test_property_tax_uses_poi_rate():
    out = monthly_carrying_cost({"price": 240_000}, _poi(property_tax_rate=0.0072))
    # 240000 * 0.0072 / 12 = 144
    assert out["property_tax"] == 144.0
    assert "property_tax" not in out["missing"]


def test_property_tax_missing_when_poi_lacks_rate():
    out = monthly_carrying_cost({"price": 240_000}, _poi())
    assert out["property_tax"] is None
    assert "property_tax" in out["missing"]


def test_insurance_uses_poi_annual():
    out = monthly_carrying_cost({"price": 240_000}, _poi(insurance_annual=1200))
    assert out["insurance"] == 100.0


def test_maintenance_uses_poi_rate():
    out = monthly_carrying_cost({"price": 240_000}, _poi(maintenance_rate_of_price=0.012))
    # 240000 * 0.012 / 12 = 240
    assert out["maintenance"] == 240.0


def test_vacancy_rate_is_recorded_for_rent_adjustment():
    out = monthly_carrying_cost({"price": 240_000}, _poi(vacancy_rate=0.06))
    assert out["vacancy_rate"] == 0.06
    assert "vacancy_rate" not in out["missing"]


def test_vacancy_rate_missing_when_poi_lacks_it():
    out = monthly_carrying_cost({"price": 240_000}, _poi())
    assert out["vacancy_rate"] is None
    assert "vacancy_rate" in out["missing"]


def test_total_excludes_null_components():
    """Total = principal_interest only when nothing else is available."""
    out = monthly_carrying_cost({"price": 240_000}, _poi())
    assert out["total"] == out["principal_interest"]


def test_total_sums_provided_components():
    listing = {"price": 240_000, "hoa": {"fee": 100}}
    out = monthly_carrying_cost(listing, _poi(
        property_tax_rate=0.01,
        insurance_annual=1200,
        maintenance_rate_of_price=0.012,
    ))
    expected = (
        out["principal_interest"]
        + out["property_tax"]
        + out["insurance"]
        + out["hoa"]
        + out["maintenance"]
    )
    assert out["total"] == round(expected, 2)
    assert out["missing"] == ["vacancy_rate"]  # only vacancy missing


def test_coverage_ratio_applies_vacancy():
    carrying = {"total": 2000, "vacancy_rate": 0.10}
    # Rent net of vacancy / total: 1500 * 0.9 / 2000 = 0.675
    assert coverage_ratio(1500, carrying) == 0.675


def test_coverage_ratio_skips_vacancy_when_rate_missing():
    carrying = {"total": 2000, "vacancy_rate": None}
    assert coverage_ratio(1500, carrying) == 0.75  # 1500 / 2000


def test_coverage_ratio_returns_none_when_inputs_missing():
    assert coverage_ratio(None, {"total": 2000}) is None
    assert coverage_ratio(1500, {"total": None}) is None
    assert coverage_ratio(1500, {"total": 0}) is None


def test_unknown_cost_assumption_key_rejected():
    with pytest.raises(ValueError):
        CostAssumptions.from_dict({"property_tax_rate": 0.01, "made_up": 42})


def test_cost_assumptions_to_dict_omits_nulls():
    ca = CostAssumptions(property_tax_rate=0.01, hoa_monthly=None)
    assert ca.to_dict() == {"property_tax_rate": 0.01}
