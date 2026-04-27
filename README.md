# Rental Finder

Downloads active property sale and rental listings within a configurable radius of the TSMC manufacturing plant in Arizona (lat: 33.775196, lon: -112.160449) using the [RentCast API](https://developers.rentcast.io).

## Project Structure

```
rental_finder/
├── constants.py                   # Search coordinates, interest rate, budget
├── fetch_listings.py              # Downloads sale + rental listings from RentCast API
├── process_listings.py            # Transforms sale listings and filters to selected_properties.csv
├── rent_estimation_utils.py       # Shared preprocessing for rent model
├── rent_model.py                  # Tunes RF hyperparams via CV, trains estimator, saves model + metrics
├── rent_model.joblib              # Fitted model pipeline (generated)
├── rent_model_metrics.json        # Validation metrics, best hyperparams + model config (generated)
├── sale_listings.json             # Output: active sale listings (generated)
├── sale_listings_processed.json   # Output: sale listings enriched with mortgage + rent fields
├── selected_properties.csv        # Output: filtered listings meeting all criteria (generated)
├── rental_listings.json           # Output: active rental listings (generated)
├── .env                           # API key (not committed)
├── validation/                    # RentCast API vs model comparison
│   ├── validate_rent_estimates.py # Samples 5 properties and compares estimates
│   ├── sample_properties.json     # The 5 sampled sale listings (generated)
│   └── rent_estimate_comparison.json # Side-by-side comparison (generated)
└── rentcast_api_docs/             # Local copy of RentCast API documentation
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

### 1. Fetch listings

```bash
uv run python fetch_listings.py
```

This will:
- Fetch all **active sale listings** within 15 miles of the TSMC plant → saved to `sale_listings.json`
- Fetch all **active rental listings** within 15 miles of the TSMC plant → saved to `rental_listings.json`

Results are paginated automatically (up to 500 per request) until all listings are retrieved.

### 2. Train the rent estimator

```bash
uv run python rent_model.py
```

Uses `rental_listings.json` with an 80/20 train/val split. Tunes Random Forest hyperparameters via `RandomizedSearchCV` (5-fold CV, 20 candidates) on the training split, then trains the final model with the best params and prints validation metrics (MAE, RMSE, MAPE, R²). Writes:
- `rent_model.joblib` — fitted sklearn Pipeline ready for inference
- `rent_model_metrics.json` — best hyperparams, validation metrics, model config, and training metadata

### 3. Process sale listings

```bash
uv run python process_listings.py
```

Enriches `sale_listings.json` with the following fields per listing (using the trained `rent_model.joblib`):
- `monthlyMortgage` — estimated monthly payment on a 30-year fixed mortgage
- `predictedRent` — Random Forest rent estimate
- `predictedRentMin` — lower bound: `predictedRent × (1 − MAPE)`
- `predictedRentMax` — upper bound: `predictedRent × (1 + MAPE)`
- `mortgageCoverageRatio` — `predictedRentMin / monthlyMortgage` (higher = better cash flow)

Also exports `selected_properties.csv` — listings passing all filters in `constants.py`, sorted by `mortgageCoverageRatio` descending.

## Configuration

| File | Variable | Description |
|------|----------|-------------|
| `constants.py` | `LATITUDE`, `LONGITUDE` | Center of the search area |
| `constants.py` | `RADIUS` | Search radius in miles (default: 15, max: 100) |
| `constants.py` | `INTEREST_RATE` | Annual mortgage interest rate (default: 0.07) |
| `constants.py` | `BUDGET` | Max purchase price (default: $500,000) |
| `constants.py` | `PROPERTY_TYPES` | Allowed property types (default: Single Family, Townhouse) |
| `constants.py` | `BEDROOMS` | Allowed bedroom counts (default: [3]) |
| `constants.py` | `MORTGAGE_COVERAGE_RANGE` | Min/max mortgage coverage ratio (default: [0.7, 1.5]) |
| `constants.py` | `YEAR_MIN` | Minimum year built (default: 1980) |
| `.env` | `RENTCAST_API_KEY` | Your RentCast API key |

## Output Format

Both output files are JSON arrays. Each listing record includes:

- **Location**: full address, city, state, zip, county, lat/lon
- **Property attributes**: type, bedrooms, bathrooms, square footage, lot size, year built
- **Listing details**: status, price/rent, listing type, listed date, days on market
- **MLS info**: MLS name and number
- **Agent/office contacts**: name, phone, email, website
- **Listing history**: price and status changes over time
