from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from factorypulse.config import Settings
from factorypulse.data import FEATURE_COLUMNS, load_training_data
from factorypulse.evaluation import calculate_metrics, select_cost_aware_threshold
from factorypulse.features import (
    ENGINEERED_NUMERIC_COLUMNS,
    OperatingFeatureBuilder,
    build_reference_values,
)
from factorypulse.monitoring import build_reference_profile


def train(settings: Settings) -> dict[str, Any]:
    features, target = load_training_data(settings.paths.raw_data)
    (
        train_features,
        validation_features,
        test_features,
        train_target,
        validation_target,
        test_target,
    ) = _split_data(features, target, settings)
    candidates = _candidate_models(settings.project.random_seed)
    validation_scores: dict[str, float] = {}
    calibrated_models: dict[str, CalibratedClassifierCV] = {}

    for name, pipeline in candidates.items():
        calibrated = CalibratedClassifierCV(
            pipeline,
            method="sigmoid",
            cv=settings.training.calibration_folds,
            n_jobs=-1,
        )
        calibrated.fit(train_features, train_target)
        probabilities = calibrated.predict_proba(validation_features)[:, 1]
        validation_scores[name] = float(average_precision_score(validation_target, probabilities))
        calibrated_models[name] = calibrated

    selected_name = max(validation_scores, key=validation_scores.get)
    selected_model = calibrated_models[selected_name]
    validation_probabilities = selected_model.predict_proba(validation_features)[:, 1]
    threshold_result = select_cost_aware_threshold(
        validation_target.to_numpy(),
        validation_probabilities,
        settings.training.false_negative_cost,
        settings.training.false_positive_cost,
        settings.training.threshold_min,
        settings.training.threshold_max,
        settings.training.threshold_steps,
    )
    test_probabilities = selected_model.predict_proba(test_features)[:, 1]
    test_metrics = calculate_metrics(
        test_target.to_numpy(),
        test_probabilities,
        threshold_result.threshold,
        settings.training.false_negative_cost,
        settings.training.false_positive_cost,
    )
    importance = permutation_importance(
        selected_model,
        test_features,
        test_target,
        scoring="average_precision",
        n_repeats=settings.training.permutation_repeats,
        random_state=settings.project.random_seed,
        n_jobs=-1,
    )
    global_importance = sorted(
        [
            {
                "feature": feature,
                "mean": float(mean),
                "std": float(std),
            }
            for feature, mean, std in zip(
                FEATURE_COLUMNS,
                importance.importances_mean,
                importance.importances_std,
                strict=True,
            )
        ],
        key=lambda item: item["mean"],
        reverse=True,
    )
    trained_at = datetime.now(UTC).isoformat()
    metrics = {
        "model_version": settings.project.model_version,
        "trained_at": trained_at,
        "selected_model": selected_name,
        "selection_metric": "average_precision",
        "validation_scores": validation_scores,
        "threshold": threshold_result.threshold,
        "validation_expected_cost": threshold_result.expected_cost,
        "test": test_metrics,
        "global_importance": global_importance,
        "split": {
            "train": len(train_features),
            "validation": len(validation_features),
            "test": len(test_features),
        },
    }
    bundle = {
        "model": selected_model,
        "threshold": threshold_result.threshold,
        "reference_values": build_reference_values(train_features),
        "model_version": settings.project.model_version,
        "trained_at": trained_at,
        "metrics": metrics,
    }
    _write_artifacts(settings, bundle, metrics, build_reference_profile(train_features, settings))
    return metrics


def _split_data(
    features: pd.DataFrame, target: pd.Series, settings: Settings
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    train_validation_features, test_features, train_validation_target, test_target = (
        train_test_split(
            features,
            target,
            test_size=settings.training.test_size,
            stratify=target,
            random_state=settings.project.random_seed,
        )
    )
    relative_validation_size = settings.training.validation_size / (1 - settings.training.test_size)
    train_features, validation_features, train_target, validation_target = train_test_split(
        train_validation_features,
        train_validation_target,
        test_size=relative_validation_size,
        stratify=train_validation_target,
        random_state=settings.project.random_seed,
    )
    return (
        train_features,
        validation_features,
        test_features,
        train_target,
        validation_target,
        test_target,
    )


def _candidate_models(random_seed: int) -> dict[str, Pipeline]:
    return {
        "balanced_logistic_regression": _build_pipeline(
            LogisticRegression(
                class_weight="balanced",
                max_iter=2_000,
                random_state=random_seed,
            ),
            scale_numeric=True,
        ),
        "balanced_random_forest": _build_pipeline(
            RandomForestClassifier(
                n_estimators=350,
                min_samples_leaf=2,
                class_weight="balanced_subsample",
                random_state=random_seed,
                n_jobs=-1,
            ),
            scale_numeric=False,
        ),
    }


def _build_pipeline(estimator: object, scale_numeric: bool) -> Pipeline:
    numeric_transformer: object = StandardScaler() if scale_numeric else "passthrough"
    preprocessing = ColumnTransformer(
        [
            ("numeric", numeric_transformer, ENGINEERED_NUMERIC_COLUMNS),
            ("category", OneHotEncoder(handle_unknown="ignore"), ["product_type"]),
        ]
    )
    return Pipeline(
        [
            ("feature_builder", OperatingFeatureBuilder()),
            ("preprocessing", preprocessing),
            ("classifier", estimator),
        ]
    )


def _write_artifacts(
    settings: Settings,
    bundle: dict[str, Any],
    metrics: dict[str, Any],
    reference_profile: dict[str, Any],
) -> None:
    for path in [
        settings.paths.model_bundle,
        settings.paths.metrics,
        settings.paths.reference_profile,
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, settings.paths.model_bundle)
    _write_json(settings.paths.metrics, metrics)
    _write_json(settings.paths.reference_profile, reference_profile)


def _write_json(path: Path, content: dict[str, Any]) -> None:
    path.write_text(json.dumps(content, indent=2), encoding="utf-8")
