"""
Trains a rent estimator on rental listings, evaluates it on a held-out 20%
group-aware validation split, and persists the fitted model and metrics.

Two estimators are available via --model:
  * rf   — RandomForestRegressor (default, simple baseline)
  * lgbm — LGBMRegressor (gradient-boosted trees, usually stronger)

The target is log-transformed via TransformedTargetRegressor so the inner
model fits log(rent + 1) but .predict still returns dollars. The split is
grouped on formattedAddress so re-listed properties cannot leak across
train/val. Hyperparameters are tuned via RandomizedSearchCV with GroupKFold.

After training, SHAP feature importance is computed on the val split and
recorded in the metrics file (mean absolute SHAP per original feature,
normalized to a relative ranking). Importances are in log-rent space —
relative ordering is meaningful, absolute magnitude is not.

Outputs (per-POI):
    outputs/<slug>/rent_model.joblib        — fitted estimator
    outputs/<slug>/rent_model_metrics.json  — metrics + best hyperparams + config

Usage:
    uv run python rent_model.py
    uv run python rent_model.py --poi austin-tx --model lgbm
"""

import argparse
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from lightgbm import LGBMRegressor
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, RandomizedSearchCV
from sklearn.pipeline import Pipeline

from cli import add_poi_args, resolve_poi
from poi import POI
from rent_estimation_utils import (
    CAT_FEATURES,
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
    "rf": {
        "regressor__model__n_estimators": [50, 75, 100, 150],
        "regressor__model__max_depth": [None, 10, 20, 30],
        "regressor__model__min_samples_leaf": [1, 2, 3, 5],
        "regressor__model__max_features": [0.6, 0.8, 1.0],
    },
    "lgbm": {
        "regressor__model__n_estimators": [200, 400, 800],
        "regressor__model__learning_rate": [0.01, 0.03, 0.05, 0.1],
        "regressor__model__num_leaves": [15, 31, 63],
        "regressor__model__min_child_samples": [5, 10, 20],
        "regressor__model__feature_fraction": [0.7, 0.85, 1.0],
    },
}


def _make_model(name: str, **params):
    if name == "rf":
        # RF parallelizes via joblib; safe to use all cores when running solo.
        # During RandomizedSearchCV (which sets n_jobs=-1 outer), the inner
        # parallelism is suppressed by joblib's worker hand-off.
        return RandomForestRegressor(**params, random_state=RANDOM_STATE, n_jobs=-1)
    if name == "lgbm":
        # LightGBM uses OpenMP threads internally. Stacking that under joblib's
        # process-level parallelism (n_jobs=-1 in RandomizedSearchCV) causes
        # oversubscription / deadlocks. Pin LGBM to single-threaded; let the
        # outer search parallelize across CV candidates.
        return LGBMRegressor(**params, random_state=RANDOM_STATE, n_jobs=1, verbose=-1)
    raise ValueError(f"Unknown model {name!r}; expected one of {list(PARAM_DISTRIBUTIONS)}")


def _build_estimator(name: str, params: dict) -> TransformedTargetRegressor:
    inner = Pipeline([
        ("preprocessor", build_transformer()),
        ("model", _make_model(name, **params)),
    ])
    return TransformedTargetRegressor(
        regressor=inner,
        func=np.log1p,
        inverse_func=np.expm1,
    )


def tune_hyperparams(name: str, X_train, y_train, groups_train) -> dict:
    base_estimator = _build_estimator(name, {})
    search = RandomizedSearchCV(
        estimator=base_estimator,
        param_distributions=PARAM_DISTRIBUTIONS[name],
        n_iter=N_ITER,
        cv=GroupKFold(n_splits=CV_FOLDS),
        scoring="neg_mean_absolute_percentage_error",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
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


def _shap_feature_importance(estimator: TransformedTargetRegressor, X_val: pd.DataFrame) -> dict:
    """Mean absolute SHAP per original feature, normalized so values sum to 1.

    Computed on the inner (log-target) model. Relative ordering is meaningful;
    raw magnitudes are in log-rent space and not directly interpretable as
    dollar contributions.
    """
    inner: Pipeline = estimator.regressor_
    preprocessor = inner.named_steps["preprocessor"]
    model = inner.named_steps["model"]

    X_transformed = preprocessor.transform(X_val)
    transformed_names = preprocessor.get_feature_names_out()

    explainer = shap.TreeExplainer(model)
    raw = explainer.shap_values(X_transformed)
    if isinstance(raw, list):
        raw = raw[0]
    shap_values = np.asarray(raw)
    mean_abs = np.abs(shap_values).mean(axis=0)

    grouped: dict[str, float] = {}
    for tname, val in zip(transformed_names, mean_abs):
        key = tname.split("__", 1)[1] if "__" in tname else tname
        for orig in CAT_FEATURES:
            if key.startswith(f"{orig}_"):
                key = orig
                break
        grouped[key] = grouped.get(key, 0.0) + float(val)

    total = sum(grouped.values()) or 1.0
    return {
        k: round(v / total, 4)
        for k, v in sorted(grouped.items(), key=lambda x: -x[1])
    }


def train(
    rental_path: str | Path,
    model_path: str | Path,
    metrics_path: str | Path,
    poi: POI,
    model_name: str = "rf",
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
    print(f"Model: {model_name}")

    print(f"\nTuning hyperparameters ({CV_FOLDS}-fold GroupKFold, {N_ITER} candidates)...")
    best_params = tune_hyperparams(model_name, X_train, y_train, groups_train)

    estimator = _build_estimator(model_name, best_params)
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

    print("\nComputing SHAP feature importance...")
    feature_importance = _shap_feature_importance(estimator, X_val)
    top = list(feature_importance.items())[:5]
    print("  Top features: " + ", ".join(f"{k}={v:.2f}" for k, v in top))

    joblib.dump(estimator, model_path)
    print(f"\nModel saved → {model_path}")

    record = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_data": str(rental_path),
        "model_name": model_name,
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
        "feature_importance": feature_importance,
    }
    with open(metrics_path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"Metrics saved → {metrics_path}")


def train_for_poi(poi: POI, model_name: str = "rf") -> None:
    out_dir = poi.output_dir()
    train(
        rental_path=out_dir / "rental_listings.json",
        model_path=out_dir / "rent_model.joblib",
        metrics_path=out_dir / "rent_model_metrics.json",
        poi=poi,
        model_name=model_name,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_poi_args(parser)
    parser.add_argument(
        "--model",
        choices=list(PARAM_DISTRIBUTIONS),
        default="rf",
        help="Estimator family. Default: rf",
    )
    args = parser.parse_args()
    train_for_poi(resolve_poi(args), model_name=args.model)


if __name__ == "__main__":
    main()
