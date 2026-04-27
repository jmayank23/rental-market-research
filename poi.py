"""Point-of-interest dataclass + loaders.

A POI is the geographic seam the whole pipeline rotates around: search
center, search radius, slug for filesystem layout, display name. Built
to be resolved once at CLI entry and passed down — no module-level
globals, so swapping the POI swaps the whole run.

Future: a `cost_assumptions` block on the POI is reserved for Stage 7.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
POIS_DIR = REPO_ROOT / "pois"
OUTPUTS_DIR = REPO_ROOT / "outputs"

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


@dataclass(frozen=True)
class POI:
    slug: str
    name: str
    latitude: float
    longitude: float
    radius_miles: float

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
