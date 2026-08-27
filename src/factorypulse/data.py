from __future__ import annotations

from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = [
    "product_type",
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
]
TARGET_COLUMN = "machine_failure"
LEAKAGE_COLUMNS = ["twf", "hdf", "pwf", "osf", "rnf"]

RAW_COLUMN_MAP = {
    "Type": "product_type",
    "Air temperature [K]": "air_temperature_k",
    "Process temperature [K]": "process_temperature_k",
    "Rotational speed [rpm]": "rotational_speed_rpm",
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "tool_wear_min",
    "Machine failure": TARGET_COLUMN,
    "TWF": "twf",
    "HDF": "hdf",
    "PWF": "pwf",
    "OSF": "osf",
    "RNF": "rnf",
}


def load_training_data(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    frame = pd.read_csv(path).rename(columns=RAW_COLUMN_MAP)
    _validate_columns(frame, FEATURE_COLUMNS + [TARGET_COLUMN])
    features = normalize_features(frame[FEATURE_COLUMNS])
    target = frame[TARGET_COLUMN].astype(int)
    if not set(target.unique()).issubset({0, 1}):
        raise ValueError("machine_failure must contain only 0 and 1")
    return features, target


def load_prediction_csv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path).rename(columns=RAW_COLUMN_MAP)
    return normalize_features(frame)


def normalize_features(frame: pd.DataFrame) -> pd.DataFrame:
    _validate_columns(frame, FEATURE_COLUMNS)
    normalized = frame[FEATURE_COLUMNS].copy()
    normalized["product_type"] = normalized["product_type"].astype(str).str.upper()
    if not normalized["product_type"].isin(["L", "M", "H"]).all():
        raise ValueError("product_type values must be L, M, or H")
    numeric_columns = [column for column in FEATURE_COLUMNS if column != "product_type"]
    normalized[numeric_columns] = normalized[numeric_columns].apply(pd.to_numeric)
    if normalized.isna().any().any():
        raise ValueError("features cannot contain missing values")
    return normalized


def _validate_columns(frame: pd.DataFrame, expected: list[str]) -> None:
    missing = sorted(set(expected) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
