import numpy as np
import pandas as pd
import pytest

from factorypulse.config import load_settings
from factorypulse.data import load_prediction_csv
from factorypulse.monitoring import calculate_drift, population_stability_index


def test_identical_distributions_have_no_drift() -> None:
    distribution = np.array([0.2, 0.3, 0.5])
    assert population_stability_index(distribution, distribution) == 0.0


def test_shifted_distributions_have_positive_drift() -> None:
    expected = np.array([0.2, 0.3, 0.5])
    shifted = np.array([0.6, 0.2, 0.2])
    assert population_stability_index(expected, shifted) > 0.25


def test_drift_report_uses_saved_reference_profile() -> None:
    settings = load_settings()
    current = load_prediction_csv(settings.root / "data/sample/drift_batch.csv")

    report = calculate_drift(current, settings.paths.reference_profile, settings)

    assert report["overall_status"] == "critical"
    assert len(report["features"]) == 6


def test_drift_rejects_tiny_batches() -> None:
    settings = load_settings()
    current = pd.DataFrame(columns=["unused"])

    with pytest.raises(ValueError, match="at least 100"):
        calculate_drift(current, settings.paths.reference_profile, settings)
