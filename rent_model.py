"""
Trains a Random Forest rent estimator on rental listings, evaluates it on a
held-out 20% validation split, and persists the fitted model and metrics.

Hyperparameters are selected via RandomizedSearchCV (5-fold CV on train split)
before the final model is fit. Best params are recorded in the metrics file.

Outputs (per-POI):
    outputs/<slug>/rent_model.joblib        — fitted sklearn Pipeline
    outputs/<slug>/rent_model_metrics.json  — metrics + best hyperparams + config

Usage:
    uv run python rent_model.py
    uv run python rent_model.py --poi austin-tx
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline

from cli import add_poi_args, resolve_poi
from poi import POI
from rent_estimation_utils import (
    FEATURES,
    TARGET,
    build_transformer,
    load_listings,
    preprocess,
    print_metrics,
)

RANDOM_STATE = 42
CV_FOLDS = 5
N_ITER = 20

PARAM_DISTRIBUTIONS = {
    "model__n_estimators": [50, 75, 100, 150],
    "model__max_depth": [None, 10, 20, 30],
    "model__min_samples_leaf": [1, 2, 3, 5],
    "model__max_features": [0.6, 0.8, 1.0],
}


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


def train(rental_path: str | Path, model_path: str | Path, metrics_path: str | Path) -> None:
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
    print()
    raw = print_metrics("Validation", y_val, preds)
    metrics = {
        "mae": round(raw["mae"], 2),
        "rmse": round(raw["rmse"], 2),
        "mape": round(raw["mape"], 3),
        "r2": round(raw["r2"], 4),
    }

    rel_residuals = (y_val.to_numpy() - preds) / preds
    residuals = {
        "q10": round(float(np.quantile(rel_residuals, 0.10)), 4),
        "q50": round(float(np.quantile(rel_residuals, 0.50)), 4),
        "q90": round(float(np.quantile(rel_residuals, 0.90)), 4),
    }
    print(
        f"  Residual band (val):                "
        f"q10={residuals['q10']:+.3f}, q50={residuals['q50']:+.3f}, q90={residuals['q90']:+.3f}"
    )

    joblib.dump(pipeline, model_path)
    print(f"\nModel saved → {model_path}")

    record = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_data": str(rental_path),
        "train_size": len(X_train),
        "val_size": len(X_val),
        "random_state": RANDOM_STATE,
        "cv_folds": CV_FOLDS,
        "n_iter": N_ITER,
        "features": FEATURES,
        "target": TARGET,
        "best_params": best_params,
        "val_metrics": metrics,
        "residual_quantiles": residuals,
    }
    with open(metrics_path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"Metrics saved → {metrics_path}")


def train_for_poi(poi: POI) -> None:
    out_dir = poi.output_dir()
    train(
        rental_path=out_dir / "rental_listings.json",
        model_path=out_dir / "rent_model.joblib",
        metrics_path=out_dir / "rent_model_metrics.json",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_poi_args(parser)
    args = parser.parse_args()
    train_for_poi(resolve_poi(args))


if __name__ == "__main__":
    main()
