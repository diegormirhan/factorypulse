from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

ENGINEERED_NUMERIC_COLUMNS = [
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
    "temperature_gap_k",
    "mechanical_power_w",
    "wear_load_index",
]


class OperatingFeatureBuilder(TransformerMixin, BaseEstimator):
    def fit(self, features: pd.DataFrame, target: object = None) -> OperatingFeatureBuilder:
        return self

    def transform(self, features: pd.DataFrame) -> pd.DataFrame:
        transformed = features.copy()
        transformed["temperature_gap_k"] = (
            transformed["process_temperature_k"] - transformed["air_temperature_k"]
        )
        transformed["mechanical_power_w"] = (
            transformed["torque_nm"] * transformed["rotational_speed_rpm"] * 2 * np.pi / 60
        )
        transformed["wear_load_index"] = transformed["tool_wear_min"] * transformed["torque_nm"]
        return transformed


def build_reference_values(features: pd.DataFrame) -> dict[str, str | float]:
    values: dict[str, str | float] = {"product_type": str(features["product_type"].mode().iloc[0])}
    for column in features.columns:
        if column != "product_type":
            values[column] = float(features[column].median())
    return values
