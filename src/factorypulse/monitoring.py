from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from factorypulse.config import Settings
from factorypulse.data import FEATURE_COLUMNS

EPSILON = 1e-6


def build_reference_profile(features: pd.DataFrame, settings: Settings) -> dict[str, Any]:
    profile: dict[str, Any] = {"features": {}}
    for column in FEATURE_COLUMNS:
        if column == "product_type":
            proportions = features[column].value_counts(normalize=True).to_dict()
            profile["features"][column] = {
                "kind": "categorical",
                "proportions": {str(key): float(value) for key, value in proportions.items()},
            }
            continue
        values = features[column].to_numpy(dtype=float)
        edges = np.unique(np.quantile(values, np.linspace(0, 1, settings.monitoring.psi_bins + 1)))
        edges[0], edges[-1] = -np.inf, np.inf
        proportions = _bin_proportions(values, edges)
        profile["features"][column] = {
            "kind": "numeric",
            "edges": [None if np.isinf(edge) else float(edge) for edge in edges],
            "proportions": proportions.tolist(),
        }
    return profile


def calculate_drift(
    current: pd.DataFrame, profile_path: Path, settings: Settings
) -> dict[str, Any]:
    if len(current) < settings.monitoring.minimum_batch_size:
        raise ValueError(
            f"Drift requires at least {settings.monitoring.minimum_batch_size} readings; "
            f"received {len(current)}."
        )
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    results = []
    for column in FEATURE_COLUMNS:
        reference = profile["features"][column]
        if reference["kind"] == "numeric":
            edges = np.array(
                [
                    -np.inf if value is None and index == 0 else np.inf if value is None else value
                    for index, value in enumerate(reference["edges"])
                ],
                dtype=float,
            )
            actual = _bin_proportions(current[column].to_numpy(dtype=float), edges)
            expected = np.array(reference["proportions"], dtype=float)
        else:
            categories = sorted(set(reference["proportions"]) | set(current[column].astype(str)))
            expected = np.array([reference["proportions"].get(value, 0) for value in categories])
            actual_counts = current[column].astype(str).value_counts(normalize=True)
            actual = np.array([actual_counts.get(value, 0) for value in categories])
        psi = population_stability_index(expected, actual)
        results.append({"feature": column, "psi": psi, "status": _drift_status(psi, settings)})
    overall = max((item["psi"] for item in results), default=0.0)
    return {"overall_status": _drift_status(overall, settings), "features": results}


def population_stability_index(expected: np.ndarray, actual: np.ndarray) -> float:
    expected_safe = np.clip(expected, EPSILON, None)
    actual_safe = np.clip(actual, EPSILON, None)
    return float(np.sum((actual_safe - expected_safe) * np.log(actual_safe / expected_safe)))


def _bin_proportions(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    counts, _ = np.histogram(values, bins=edges)
    return counts / max(counts.sum(), 1)


def _drift_status(psi: float, settings: Settings) -> str:
    if psi >= settings.monitoring.critical_threshold:
        return "critical"
    if psi >= settings.monitoring.warning_threshold:
        return "warning"
    return "stable"
