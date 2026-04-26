"""
Trains a Random Forest rent estimator on rental listings, evaluates it on a
held-out 20% validation split, and persists the fitted model and metrics.

Hyperparameters are selected via RandomizedSearchCV (5-fold CV on train split)
before the final model is fit. Best params are recorded in the metrics file.

Outputs:
    rent_model.joblib        — fitted sklearn Pipeline (transformer + RF)
    rent_model_metrics.json  — validation metrics + best hyperparams + model config

Usage:
    uv run python rent_model.py
"""

import json
from datetime import datetime, timezone

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline

from rent_estimation_utils import (
    FEATURES,
    TARGET,
    build_transformer,
    load_listings,
    preprocess,
)

RANDOM_STATE = 42
CV_FOLDS = 5
N_ITER = 20

# Previous fixed params: n_estimators=75, min_samples_leaf=2, max_features=0.6, max_depth=None
PARAM_DISTRIBUTIONS = {
    "model__n_estimators": [50, 75, 100, 150],
    "model__max_depth": [None, 10, 20, 30],
    "model__min_samples_leaf": [1, 2, 3, 5],
    "model__max_features": [0.6, 0.8, 1.0],
}

MODEL_PATH = "rent_model.joblib"
METRICS_PATH = "rent_model_metrics.json"


def _build_pipeline(params: dict) -> Pipeline:
    return Pipeline([
        ("preprocessor", build_transformer()),
        ("model", RandomForestRegressor(**params, random_state=RANDOM_STATE, n_jobs=-1)),
    ])


def tune_hyperparams(X_train, y_train) -> dict:
    base_pipeline = _build_pipeline({})
    search = RandomizedSearchCV(
        estimator=base_pipeline,
        param_distributions=PARAM_DISTRIBUTIONS,
        n_iter=N_ITER,
        cv=CV_FOLDS,
        scoring="neg_mean_absolute_percentage_error",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    search.fit(X_train, y_train)

    best_params = {k.replace("model__", ""): v for k, v in search.best_params_.items()}
    best_cv_mape = -search.best_score_ * 100
    print(f"  Best CV MAPE : {best_cv_mape:.1f}%")
    print(f"  Best params  : {best_params}")
    return best_params


def train(rental_path: str = "rental_listings.json") -> None:
    df = preprocess(load_listings(rental_path))
    X, y = df[FEATURES], df[TARGET]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )
    print(f"Train: {len(X_train):,}  |  Val: {len(X_val):,}")

    print(f"\nTuning hyperparameters ({CV_FOLDS}-fold CV, {N_ITER} candidates)...")
    best_params = tune_hyperparams(X_train, y_train)

    pipeline = _build_pipeline(best_params)
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_val)
    metrics = {
        "mae": round(float(mean_absolute_error(y_val, preds)), 2),
        "rmse": round(float(np.sqrt(mean_squared_error(y_val, preds))), 2),
        "mape": round(float(mean_absolute_percentage_error(y_val, preds)) * 100, 3),
        "r2": round(float(r2_score(y_val, preds)), 4),
    }

    print(f"\n  MAE:  ${metrics['mae']:>8,.2f}")
    print(f"  RMSE: ${metrics['rmse']:>8,.2f}")
    print(f"  MAPE:  {metrics['mape']:>7.1f}%")
    print(f"  R²:    {metrics['r2']:>7.4f}")

    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nModel saved → {MODEL_PATH}")

    record = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_data": rental_path,
        "train_size": len(X_train),
        "val_size": len(X_val),
        "random_state": RANDOM_STATE,
        "cv_folds": CV_FOLDS,
        "n_iter": N_ITER,
        "features": FEATURES,
        "target": TARGET,
        "best_params": best_params,
        "val_metrics": metrics,
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(record, f, indent=2)
    print(f"Metrics saved → {METRICS_PATH}")


if __name__ == "__main__":
    train()
