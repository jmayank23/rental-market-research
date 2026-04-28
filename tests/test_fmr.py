"""Tests for HUD FMR lookup + flag thresholds."""

import pytest

from fmr import DELTA_THRESHOLD, fmr_flag, lookup_fmr


def test_lookup_known_county_returns_dollar_value():
    fmr = lookup_fmr("Jefferson", "AL", 3)
    assert fmr is not None
    assert 1000 < fmr < 2500  # FY2025 range for AL counties


def test_lookup_state_is_case_insensitive():
    a = lookup_fmr("Jefferson", "al", 3)
    b = lookup_fmr("Jefferson", "AL", 3)
    assert a == b


def test_lookup_county_is_case_insensitive():
    a = lookup_fmr("jefferson", "AL", 3)
    b = lookup_fmr("Jefferson", "AL", 3)
    assert a == b


def test_lookup_unknown_county_returns_none():
    assert lookup_fmr("Atlantis", "AA", 3) is None


def test_lookup_missing_county_or_state_returns_none():
    assert lookup_fmr(None, "AL", 3) is None
    assert lookup_fmr("Jefferson", None, 3) is None


def test_bedrooms_are_clamped_to_4():
    """5-bedroom and larger get FMR_4 — HUD doesn't publish higher tiers."""
    four_br = lookup_fmr("Jefferson", "AL", 4)
    five_br = lookup_fmr("Jefferson", "AL", 5)
    eight_br = lookup_fmr("Jefferson", "AL", 8)
    assert four_br == five_br == eight_br


def test_bedrooms_zero_uses_studio_fmr():
    studio = lookup_fmr("Jefferson", "AL", 0)
    one_br = lookup_fmr("Jefferson", "AL", 1)
    assert studio is not None
    assert studio < one_br  # studios are cheaper than 1BRs


def test_bedrooms_unparseable_falls_back_to_2br():
    fallback = lookup_fmr("Jefferson", "AL", "many")
    expected = lookup_fmr("Jefferson", "AL", 2)
    assert fallback == expected


def test_flag_high_when_prediction_far_above_fmr():
    flag, delta = fmr_flag(2200, 1300)
    assert flag == "high"
    assert delta == pytest.approx((2200 - 1300) / 1300, abs=1e-3)


def test_flag_low_when_prediction_far_below_fmr():
    flag, delta = fmr_flag(500, 1300)
    assert flag == "low"


def test_flag_empty_when_within_band():
    flag, delta = fmr_flag(1400, 1300)  # ~7.7% above — within ±50%
    assert flag == ""
    assert abs(delta) < 0.1


def test_flag_empty_when_fmr_unavailable():
    flag, delta = fmr_flag(1500, None)
    assert flag == ""
    assert delta is None


def test_flag_empty_when_predicted_rent_unavailable():
    flag, _ = fmr_flag(None, 1300)
    assert flag == ""


def test_flag_threshold_is_50_pct_by_default():
    assert DELTA_THRESHOLD == 0.50


def test_threshold_boundary_is_inclusive_below_strict_above():
    """At exactly +50%, no flag (≤ threshold). Slightly above, flag fires."""
    flag_at_threshold, _ = fmr_flag(1500, 1000)  # exactly +50%
    flag_just_above, _ = fmr_flag(1501, 1000)
    assert flag_at_threshold == ""
    assert flag_just_above == "high"
