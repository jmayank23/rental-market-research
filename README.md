# Rental Finder

Downloads active property sale and rental listings within a configurable radius of any user-supplied point of interest (POI), trains a rent estimator on the local rental market, and shortlists for-sale properties whose predicted rent comfortably covers the mortgage. Defaults to the TSMC manufacturing plant in Arizona; switch POIs via a single CLI flag.

## Project Structure

```
rental_finder/
├── poi.py                         # POI dataclass + JSON loader
├── cli.py                         # Shared --poi CLI surface
├── pois/
│   └── tsmc-az.json               # Default POI definition
├── constants.py                   # Modeling + filter knobs (POI-agnostic)
├── fetch_listings.py              # Downloads sale + rental listings
├── rent_estimation_utils.py       # Pipeline + preprocessing
├── rent_model.py                  # Trains rent estimator (RF + RandomizedSearchCV)
├── process_listings.py            # Scores sale listings, exports selected_properties.csv
├── validation/
│   └── validate_rent_estimates.py # Compares our predictions vs RentCast AVM
├── outputs/<slug>/                # Per-POI generated artifacts (gitignored)
│   ├── sale_listings.json
│   ├── rental_listings.json
│   ├── rent_model.joblib
│   ├── rent_model_metrics.json
│   ├── sale_listings_processed.json
│   ├── selected_properties.csv
│   └── validation/
├── tests/                         # pytest suite
├── scripts/build_test_fixtures.py # One-shot real-data fixture builder
├── rentcast_api_docs/             # Local copy of RentCast API docs
└── .env                           # API key (not committed)
```

## Setup

**1. Install dependencies**

```bash
uv sync
```

**2. Configure your API key**

Add your RentCast API key to `.env`:

```
RENTCAST_API_KEY=your_api_key_here
```

Get an API key from the [RentCast API Dashboard](https://app.rentcast.io/app/api).

## Tests

```bash
uv run pytest
```

Tests run against committed fixtures in `tests/fixtures/` — no API key required for CI. The fixtures are real RentCast listings, refreshed by running `uv run python scripts/build_test_fixtures.py` (consumes a small number of API credits).

## Usage

The default POI is `tsmc-az`. Every script accepts the same `--poi` family of flags.

### 1. Fetch listings

```bash
uv run python fetch_listings.py                    # default: tsmc-az
uv run python fetch_listings.py --poi austin-tx    # named POI from pois/austin-tx.json
uv run python fetch_listings.py \                  # ad-hoc POI
    --poi-name "Austin TX" \
    --poi-lat 30.27 --poi-lon -97.74 --poi-radius 20
```

Writes to `outputs/<slug>/sale_listings.json` and `outputs/<slug>/rental_listings.json`. Pagination is automatic (up to 500 per request); transient 5xx / 429 / connection errors are retried with exponential backoff.

### 2. Train the rent estimator

```bash
uv run python rent_model.py [--poi <slug>]
```

Uses the rentals fetched for the given POI with an 80/20 train/val split. Tunes Random Forest hyperparameters via `RandomizedSearchCV` (5-fold CV, 20 candidates), then prints validation metrics. Writes:
- `outputs/<slug>/rent_model.joblib` — fitted sklearn Pipeline (imputers + scaler + OHE + RF)
- `outputs/<slug>/rent_model_metrics.json` — best hyperparams, val metrics, residual quantiles, training metadata

### 3. Process sale listings

```bash
uv run python process_listings.py [--poi <slug>]
```

Enriches each listing with:
- `monthlyMortgage` — 30-year fixed payment at the configured `INTEREST_RATE`
- `predictedRent` — RF prediction
- `predictedRentMin / Max` — bounds derived from the val-set residual quantiles (q10 / q90); falls back to ±MAPE for legacy metrics files
- `distanceToPoi` — haversine miles to the POI center
- `mortgageCoverageRatio` — `predictedRentMin / monthlyMortgage` (higher = better cash flow)

Exports `outputs/<slug>/selected_properties.csv` with listings passing all filters in `constants.py`, sorted by `mortgageCoverageRatio` descending.

### 4. Validate against RentCast's AVM (optional)

```bash
uv run python validation/validate_rent_estimates.py [--poi <slug>]
```

Samples 5 Single Family listings under budget and compares our rent prediction against RentCast's `/avm/rent/long-term` estimate, side by side.

## POI Configuration

A POI is just JSON in `pois/<slug>.json`:

```json
{
  "slug": "tsmc-az",
  "name": "TSMC Arizona Plant",
  "latitude": 33.775196,
  "longitude": -112.160449,
  "radius_miles": 15
}
```

Slugs must be lowercase alphanumeric / dashes / underscores. Latitude in [-90, 90], longitude in [-180, 180], radius in (0, 100].

## Configuration

| File | Variable | Description |
|------|----------|-------------|
| `pois/<slug>.json` | `latitude`, `longitude`, `radius_miles` | Center + radius of the search area |
| `constants.py` | `INTEREST_RATE` | Annual mortgage interest rate (default: 0.07) |
| `constants.py` | `LOAN_TERM_MONTHS` | Mortgage term in months (default: 360) |
| `constants.py` | `BUDGET` | Max purchase price (default: $500,000) |
| `constants.py` | `PROPERTY_TYPES` | Allowed property types (default: Single Family, Townhouse) |
| `constants.py` | `BEDROOMS` | Allowed bedroom counts (default: [3]) |
| `constants.py` | `MORTGAGE_COVERAGE_RANGE` | Min/max coverage ratio (default: [0.7, 1.5]) |
| `constants.py` | `YEAR_MIN` | Minimum year built (default: 1980) |
| `.env` | `RENTCAST_API_KEY` | Your RentCast API key |

## Output Format

Both fetched files are JSON arrays. Each listing record includes:

- **Location**: full address, city, state, zip, county, lat/lon
- **Property attributes**: type, bedrooms, bathrooms, square footage, lot size, year built
- **Listing details**: status, price/rent, listing type, listed date, days on market
- **MLS info**: MLS name and number
- **Agent/office contacts**: name, phone, email, website
- **Listing history**: price and status changes over time
