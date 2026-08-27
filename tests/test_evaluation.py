import numpy as np

from factorypulse.evaluation import calculate_metrics, select_cost_aware_threshold


def test_cost_aware_threshold_favors_recall_when_failures_are_expensive() -> None:
    target = np.array([0, 0, 0, 1, 1])
    probabilities = np.array([0.05, 0.15, 0.25, 0.35, 0.90])

    result = select_cost_aware_threshold(
        target,
        probabilities,
        false_negative_cost=25,
        false_positive_cost=1,
        minimum=0.1,
        maximum=0.8,
        steps=8,
    )

    assert result.threshold <= 0.35


def test_metrics_report_confusion_matrix_in_negative_positive_order() -> None:
    metrics = calculate_metrics(
        np.array([0, 0, 1, 1]),
        np.array([0.1, 0.8, 0.7, 0.9]),
        threshold=0.5,
        false_negative_cost=25,
        false_positive_cost=1,
    )

    assert metrics["confusion_matrix"] == [[1, 1], [0, 2]]
    assert metrics["recall"] == 1.0
