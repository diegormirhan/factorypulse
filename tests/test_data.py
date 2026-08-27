from pathlib import Path

import pandas as pd
import pytest

from factorypulse.data import FEATURE_COLUMNS, load_training_data, normalize_features


def test_training_data_excludes_identifiers_and_failure_modes() -> None:
    features, target = load_training_data(Path("data/raw/ai4i2020.csv"))

    assert list(features.columns) == FEATURE_COLUMNS
    assert len(features) == len(target) == 10_000
    assert target.sum() == 339


def test_normalize_features_rejects_unknown_product_type() -> None:
    invalid = pd.DataFrame(
        [
            {
                "product_type": "X",
                "air_temperature_k": 300,
                "process_temperature_k": 310,
                "rotational_speed_rpm": 1_500,
                "torque_nm": 40,
                "tool_wear_min": 100,
            }
        ]
    )

    with pytest.raises(ValueError, match="product_type"):
        normalize_features(invalid)
