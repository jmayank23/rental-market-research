"""POI-agnostic project constants.

Geographic location lives on the resolved POI (see poi.py); this module only
holds modeling and filtering knobs that don't change between regions.
"""

INTEREST_RATE = 0.07  # annual, 30-year fixed
LOAN_TERM_MONTHS = 360

# Training-time outlier clip (rentals only — sale-side filtering is BUDGET).
PRICE_RANGE = (200, 20_000)             # monthly rent
SQUAREFOOTAGE_RANGE = (200, 10_000)

# Output filters
BUDGET = 500_000
PROPERTY_TYPES = ["Single Family", "Townhouse"]
BEDROOMS = [3]
MORTGAGE_COVERAGE_RANGE = [0.7, 1.5]  # helps to filter out outliers
YEAR_MIN = 1980
