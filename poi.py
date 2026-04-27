"""Point-of-interest dataclass + loaders.

A POI is the geographic seam the whole pipeline rotates around: search
center, search radius, slug for filesystem layout, display name, and an
optional `cost_assumptions` block used by Stage 7's carrying-cost helper.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
POIS_DIR = REPO_ROOT / "pois"
OUTPUTS_DIR = REPO_ROOT / "outputs"

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


@dataclass(frozen=True)
class CostAssumptions:
    """User-supplied per-POI cost rates. All fields optional — missing values
    surface in costEstimateFlags rather than being silently defaulted."""

    property_tax_rate: float | None = None       # annual rate, fraction of price
    insurance_annual: float | None = None        # annual dollars
    hoa_monthly: float | None = None             # monthly dollars (listing.hoa.fee preferred)
    vacancy_rate: float | None = None            # fraction of rent
    maintenance_rate_of_price: float | None = None  # annual rate, fraction of price

    @classmethod
    def from_dict(cls, data: dict | None) -> "CostAssumptions":
        if not data:
            return cls()
        allowed = {f for f in cls.__dataclass_fields__}
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"Unknown cost_assumptions keys: {sorted(unknown)}")
        return cls(**{k: data[k] for k in data})

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass(frozen=True)
class POI:
    slug: str
    name: str
    latitude: float
    longitude: float
    radius_miles: float
    cost_assumptions: CostAssumptions = field(default_factory=CostAssumptions)

    def __post_init__(self) -> None:
        if not _SLUG_RE.fullmatch(self.slug):
            raise ValueError(
                f"slug must be lowercase alphanumeric / dashes / underscores, got {self.slug!r}"
            )
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"latitude out of range: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"longitude out of range: {self.longitude}")
        if not (0 < self.radius_miles <= 100):
            raise ValueError(f"radius_miles must be in (0, 100], got {self.radius_miles}")

    @classmethod
    def from_dict(cls, data: dict) -> "POI":
        return cls(
            slug=data["slug"],
            name=data["name"],
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            radius_miles=float(data["radius_miles"]),
            cost_assumptions=CostAssumptions.from_dict(data.get("cost_assumptions")),
        )

    @classmethod
    def from_json_file(cls, path: Path | str) -> "POI":
        path = Path(path)
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def output_dir(self) -> Path:
        d = OUTPUTS_DIR / self.slug
        d.mkdir(parents=True, exist_ok=True)
        return d


def slugify(text: str) -> str:
    """Filesystem-safe slug derived from a free-text name."""
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "custom-poi"


def load_named_poi(slug: str) -> POI:
    """Load a POI by slug from the pois/ directory."""
    path = POIS_DIR / f"{slug}.json"
    if not path.exists():
        raise FileNotFoundError(f"No POI definition at {path}")
    return POI.from_json_file(path)
