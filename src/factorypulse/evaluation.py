from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass(frozen=True)
class ThresholdResult:
    threshold: float
    expected_cost: float


def select_cost_aware_threshold(
    target: np.ndarray,
    probabilities: np.ndarray,
    false_negative_cost: float,
    false_positive_cost: float,
    minimum: float,
    maximum: float,
    steps: int,
) -> ThresholdResult:
    thresholds = np.linspace(minimum, maximum, steps)
    costs = [
        _classification_cost(
            target,
            probabilities >= threshold,
            false_negative_cost,
            false_positive_cost,
        )
        for threshold in thresholds
    ]
    index = int(np.argmin(costs))
    return ThresholdResult(threshold=float(thresholds[index]), expected_cost=float(costs[index]))


def calculate_metrics(
    target: np.ndarray,
    probabilities: np.ndarray,
    threshold: float,
    false_negative_cost: float,
    false_positive_cost: float,
) -> dict[str, float | int | list[list[int]]]:
    predicted = probabilities >= threshold
    matrix = confusion_matrix(target, predicted, labels=[0, 1])
    return {
        "average_precision": float(average_precision_score(target, probabilities)),
        "roc_auc": float(roc_auc_score(target, probabilities)),
        "brier_score": float(brier_score_loss(target, probabilities)),
        "precision": float(precision_score(target, predicted, zero_division=0)),
        "recall": float(recall_score(target, predicted, zero_division=0)),
        "f1": float(f1_score(target, predicted, zero_division=0)),
        "expected_cost": float(
            _classification_cost(target, predicted, false_negative_cost, false_positive_cost)
        ),
        "confusion_matrix": matrix.tolist(),
        "samples": int(len(target)),
        "failures": int(np.sum(target)),
    }


def _classification_cost(
    target: np.ndarray,
    predicted: np.ndarray,
    false_negative_cost: float,
    false_positive_cost: float,
) -> float:
    tn, fp, fn, tp = confusion_matrix(target, predicted, labels=[0, 1]).ravel()
    del tn, tp
    return (fn * false_negative_cost + fp * false_positive_cost) / len(target)
