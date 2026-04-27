import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from constants import PRICE_RANGE, SQUAREFOOTAGE_RANGE
from geo import haversine_miles
from poi import POI

FEATURES = [
    "bedrooms",
    "bathrooms",
    "squareFootage",
    "lotSize",
    "yearBuilt",
    "latitude",
    "longitude",
    "distanceToPoi",
    "propertyType",
]
TARGET = "price"

NUM_FEATURES = [
    "bedrooms",
    "bathrooms",
    "squareFootage",
    "lotSize",
    "yearBuilt",
    "latitude",
    "longitude",
    "distanceToPoi",
]
CAT_FEATURES = ["propertyType"]
REQUIRED_FEATURES = ["bedrooms", "bathrooms", "squareFootage", "latitude", "longitude"]


def load_listings(path: str) -> pd.DataFrame:
    with open(path) as f:
        return pd.DataFrame(json.load(f))


def add_distance_to_poi(df: pd.DataFrame, poi: POI) -> pd.DataFrame:
    """Append a distanceToPoi column (miles) to the DataFrame in place-safe fashion."""
    df = df.copy()
    df["distanceToPoi"] = [
        haversine_miles(lat, lon, poi.latitude, poi.longitude)
        if pd.notna(lat) and pd.notna(lon)
        else np.nan
        for lat, lon in zip(df.get("latitude"), df.get("longitude"))
    ]
    return df


def _filter_outliers(df: pd.DataFrame) -> pd.DataFrame:
    price_lo, price_hi = PRICE_RANGE
    sqft_lo, sqft_hi = SQUAREFOOTAGE_RANGE
    before = len(df)
    df = df[df[TARGET].between(price_lo, price_hi)]
    df = df[df["squareFootage"].between(sqft_lo, sqft_hi)]
    dropped = before - len(df)
    if dropped:
        print(f"  Outlier filter dropped {dropped:,} rows (price∉[{price_lo},{price_hi}] or sqft∉[{sqft_lo},{sqft_hi}])")
    return df


def preprocess(df: pd.DataFrame, poi: POI) -> pd.DataFrame:
    """Row-filter + distance feature + outlier clip.

    Returns the full DataFrame (all original columns preserved) with:
    - rows missing target / required features dropped,
    - rows outside the rental price / squareFootage outlier clip dropped,
    - a `distanceToPoi` column appended.

    Imputation of optional features (lotSize, yearBuilt, propertyType,
    distanceToPoi for rows with missing coords) happens inside the sklearn
    Pipeline so train and inference share the same fitted statistics.
    """
    df = df.copy()
    df = add_distance_to_poi(df, poi)
    df = df.dropna(subset=[TARGET] + REQUIRED_FEATURES)
    df = _filter_outliers(df)
    return df.reset_index(drop=True)


def build_transformer() -> ColumnTransformer:
    numeric_pipeline = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", numeric_pipeline, NUM_FEATURES),
        ("cat", categorical_pipeline, CAT_FEATURES),
    ])


def print_metrics(name: str, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    print(f"  {name:35s} | MAE: ${mae:>8,.0f} | RMSE: ${rmse:>8,.0f} | MAPE: {mape:>5.1f}% | R²: {r2:.3f}")
    return {"mae": mae, "rmse": rmse, "mape": mape, "r2": r2}
