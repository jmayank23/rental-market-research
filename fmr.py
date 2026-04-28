"""HUD Fair Market Rent lookup, used as a sanity check on model rent predictions.

The model is trained on the entire metro's rental listings, which can pull
predictions toward the average — but a property's actual achievable rent is a
neighborhood-level number. HUD FMRs (50th-percentile metro/county rents that
HUD uses to set Section 8 voucher caps) are a useful conservative anchor.

If the model's `predictedRent` is wildly above the county FMR — say more than
50% above — the model is likely overshooting, often because the listing sits
in a low-rent ZIP that the metro-wide average obscures. Such listings get
`fmrFlag = "high"`. Symmetric flag for predictions far below FMR.

Data source: data/hud_fmr.csv. Bundled with the repo. Refresh manually when
HUD publishes a new fiscal year (https://www.huduser.gov/portal/datasets/fmr.html).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "hud_fmr.csv"
DELTA_THRESHOLD = 0.50  # 50% delta in either direction generates a flag


@dataclass(frozen=True)
class FmrEntry:
    county: str
    state: str
    fmr_by_beds: dict[int, float]
    source: str


def _load_table() -> dict[tuple[str, str], FmrEntry]:
    table: dict[tuple[str, str], FmrEntry] = {}
    if not DATA_PATH.exists():
        return table
    with open(DATA_PATH) as f:
        for row in csv.DictReader(f):
            entry = FmrEntry(
                county=row["county"],
                state=row["state"],
                fmr_by_beds={
                    0: float(row["fmr_0"]),
                    1: float(row["fmr_1"]),
                    2: float(row["fmr_2"]),
                    3: float(row["fmr_3"]),
                    4: float(row["fmr_4"]),
                },
                source=row.get("source", ""),
            )
            table[(entry.county.lower(), entry.state.upper())] = entry
    return table


_TABLE = _load_table()


def lookup_fmr(county: str | None, state: str | None, bedrooms) -> float | None:
    """Return county FMR for the given bedroom count, or None if unavailable.

    Bedroom counts above 4 are clamped to FMR_4 (HUD doesn't publish higher tiers).
    Studios / unknown bedroom counts are clamped to 0.
    """
    if not county or not state:
        return None
    entry = _TABLE.get((county.lower(), state.upper()))
    if entry is None:
        return None
    try:
        beds = int(round(float(bedrooms)))
    except (TypeError, ValueError):
        beds = 2  # neutral fallback
    beds = max(0, min(4, beds))
    return entry.fmr_by_beds[beds]


def fmr_flag(predicted_rent: float | None, fmr: float | None, threshold: float = DELTA_THRESHOLD) -> tuple[str, float | None]:
    """Return (flag, signed_delta) given a predicted rent and a reference FMR.

    flag is "" when the prediction is within ±threshold of FMR or when FMR is
    unavailable; "high" if pred > fmr × (1+threshold); "low" if pred < fmr × (1-threshold).
    delta is (predicted - fmr) / fmr (None when fmr is unavailable).
    """
    if fmr is None or predicted_rent is None or fmr <= 0:
        return ("", None)
    delta = (predicted_rent - fmr) / fmr
    if delta > threshold:
        return ("high", round(delta, 3))
    if delta < -threshold:
        return ("low", round(delta, 3))
    return ("", round(delta, 3))


def coverage_universe() -> list[tuple[str, str]]:
    """List of (county, state) pairs we have FMRs for."""
    return sorted({(e.county, e.state) for e in _TABLE.values()})
