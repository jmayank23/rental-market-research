"""
Trains a Random Forest rent estimator on rental listings, evaluates it on a
held-out 20% validation split, and persists the fitted model and metrics.

Hyperparameters are selected via RandomizedSearchCV (5-fold GroupKFold on the
training split) before the final model is fit. The target is log-transformed
via TransformedTargetRegressor so the inner model fits log(price + 1) but
.predict still returns dollars. The split is grouped on formattedAddress so
re-listed properties cannot leak across train/val.

Outputs (per-POI):
    outputs/<slug>/rent_model.joblib        — fitted estimator
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
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, RandomizedSearchCV
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
GROUP_KEY = "formattedAddress"

PARAM_DISTRIBUTIONS = {
    "regressor__model__n_estimators": [50, 75, 100, 150],
    "regressor__model__max_depth": [None, 10, 20, 30],
    "regressor__model__min_samples_leaf": [1, 2, 3, 5],
    "regressor__model__max_features": [0.6, 0.8, 1.0],
}


def _build_estimator(params: dict) -> TransformedTargetRegressor:
    inner = Pipeline([
        ("preprocessor", build_transformer()),
        ("model", RandomForestRegressor(**params, random_state=RANDOM_STATE, n_jobs=-1)),
    ])
    return TransformedTargetRegressor(
        regressor=inner,
        func=np.log1p,
        inverse_func=np.expm1,
    )


def tune_hyperparams(X_train, y_train, groups_train) -> dict:
    base_estimator = _build_estimator({})
    search = RandomizedSearchCV(
        estimator=base_estimator,
        param_distributions=PARAM_DISTRIBUTIONS,
        n_iter=N_ITER,
        cv=GroupKFold(n_splits=CV_FOLDS),
        scoring="neg_mean_absolute_percentage_error",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    search.fit(X_train, y_train, groups=groups_train)

    best_params = {
        k.replace("regressor__model__", ""): v for k, v in search.best_params_.items()
    }
    best_cv_mape = -search.best_score_ * 100
    print(f"  Best CV MAPE : {best_cv_mape:.1f}%")
    print(f"  Best params  : {best_params}")
    return best_params


def _group_train_val_split(df, groups, test_size=0.2):
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=RANDOM_STATE)
    train_idx, val_idx = next(splitter.split(df, groups=groups))
    return train_idx, val_idx


def train(
    rental_path: str | Path,
    model_path: str | Path,
    metrics_path: str | Path,
    poi: POI,
) -> None:
    df = preprocess(load_listings(rental_path), poi)
    if GROUP_KEY not in df.columns:
        raise ValueError(f"Rental listings must include {GROUP_KEY!r} for group-aware splitting")

    X, y = df[FEATURES], df[TARGET]
    groups = df[GROUP_KEY].fillna("__unknown__").to_numpy()

    train_idx, val_idx = _group_train_val_split(df, groups)
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
    groups_train = groups[train_idx]

    overlap = set(groups_train.tolist()) & set(groups[val_idx].tolist())
    print(f"Train: {len(X_train):,}  |  Val: {len(X_val):,}  |  group overlap: {len(overlap)}")

    print(f"\nTuning hyperparameters ({CV_FOLDS}-fold GroupKFold, {N_ITER} candidates)...")
    best_params = tune_hyperparams(X_train, y_train, groups_train)

    estimator = _build_estimator(best_params)
    estimator.fit(X_train, y_train)

    preds = estimator.predict(X_val)
    print()
    raw_metrics = print_metrics("Validation", y_val, preds)
    metrics = {
        "mae": round(raw_metrics["mae"], 2),
        "rmse": round(raw_metrics["rmse"], 2),
        "mape": round(raw_metrics["mape"], 3),
        "r2": round(raw_metrics["r2"], 4),
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

    joblib.dump(estimator, model_path)
    print(f"\nModel saved → {model_path}")

    record = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_data": str(rental_path),
        "poi": {
            "slug": poi.slug,
            "name": poi.name,
            "latitude": poi.latitude,
            "longitude": poi.longitude,
            "radius_miles": poi.radius_miles,
        },
        "train_size": len(X_train),
        "val_size": len(X_val),
        "group_overlap": len(overlap),
        "random_state": RANDOM_STATE,
        "cv_folds": CV_FOLDS,
        "n_iter": N_ITER,
        "features": FEATURES,
        "target": TARGET,
        "target_transform": "log1p",
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
        poi=poi,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_poi_args(parser)
    args = parser.parse_args()
    train_for_poi(resolve_poi(args))


if __name__ == "__main__":
    main()
