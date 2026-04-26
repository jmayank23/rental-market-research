import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

FEATURES = [
    "bedrooms",
    "bathrooms",
    "squareFootage",
    "lotSize",
    "yearBuilt",
    "latitude",
    "longitude",
    "propertyType",
]
TARGET = "price"

NUM_FEATURES = ["bedrooms", "bathrooms", "squareFootage", "lotSize", "yearBuilt", "latitude", "longitude"]
CAT_FEATURES = ["propertyType"]


def load_listings(path: str) -> pd.DataFrame:
    with open(path) as f:
        return pd.DataFrame(json.load(f))


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df[FEATURES + [TARGET]].copy()
    df = df.dropna(subset=[TARGET, "bedrooms", "bathrooms", "squareFootage", "latitude", "longitude"])
    df["lotSize"] = df["lotSize"].fillna(df["lotSize"].median())
    df["yearBuilt"] = df["yearBuilt"].fillna(df["yearBuilt"].median())
    df["propertyType"] = df["propertyType"].fillna("Unknown")
    return df.reset_index(drop=True)


def build_transformer() -> ColumnTransformer:
    return ColumnTransformer([
        ("num", StandardScaler(), NUM_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATURES),
    ])


def print_metrics(name: str, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    print(f"  {name:35s} | MAE: ${mae:>8,.0f} | RMSE: ${rmse:>8,.0f} | MAPE: {mape:>5.1f}% | R²: {r2:.3f}")
    return {"mae": mae, "rmse": rmse, "mape": mape, "r2": r2}
