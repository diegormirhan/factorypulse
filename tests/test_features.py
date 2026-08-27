import pandas as pd
import pytest

from factorypulse.features import OperatingFeatureBuilder


def test_feature_builder_derives_operating_physics() -> None:
    source = pd.DataFrame(
        [
            {
                "product_type": "M",
                "air_temperature_k": 300.0,
                "process_temperature_k": 311.0,
                "rotational_speed_rpm": 1_500,
                "torque_nm": 40.0,
                "tool_wear_min": 100,
            }
        ]
    )

    transformed = OperatingFeatureBuilder().fit_transform(source)

    assert transformed.loc[0, "temperature_gap_k"] == 11.0
    assert transformed.loc[0, "mechanical_power_w"] == pytest.approx(6_283.185, rel=1e-5)
    assert transformed.loc[0, "wear_load_index"] == 4_000.0
