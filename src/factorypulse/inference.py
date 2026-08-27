from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from factorypulse.data import FEATURE_COLUMNS, normalize_features

FEATURE_LABELS = {
    "product_type": "Product grade",
    "air_temperature_k": "Air temperature",
    "process_temperature_k": "Process temperature",
    "rotational_speed_rpm": "Rotational speed",
    "torque_nm": "Torque",
    "tool_wear_min": "Tool wear",
}


class Predictor:
    def __init__(self, bundle_path: Path, log_path: Path | None = None) -> None:
        if not bundle_path.exists():
            raise FileNotFoundError(f"Model bundle not found: {bundle_path}. Run training first.")
        bundle = joblib.load(bundle_path)
        self.model = bundle["model"]
        self.threshold = float(bundle["threshold"])
        self.reference_values = bundle["reference_values"]
        self.model_version = str(bundle["model_version"])
        self.trained_at = str(bundle["trained_at"])
        self.metrics = bundle["metrics"]
        self.log_path = log_path

    def predict_one(self, reading: dict[str, Any], write_log: bool = True) -> dict[str, Any]:
        frame = normalize_features(pd.DataFrame([reading]))
        probability = float(self.model.predict_proba(frame)[:, 1][0])
        result = {
            "failure_probability": probability,
            "risk_level": self._risk_level(probability),
            "requires_inspection": probability >= self.threshold,
            "decision_threshold": self.threshold,
            "drivers": self._explain(frame, probability),
            "model_version": self.model_version,
        }
        if write_log and self.log_path is not None:
            self._write_log(frame.iloc[0].to_dict(), result)
        return result

    def predict_batch(self, features: pd.DataFrame) -> pd.DataFrame:
        normalized = normalize_features(features)
        probabilities = self.model.predict_proba(normalized)[:, 1]
        scored = normalized.copy()
        scored["failure_probability"] = probabilities
        scored["requires_inspection"] = probabilities >= self.threshold
        scored["risk_level"] = [self._risk_level(value) for value in probabilities]
        return scored

    def model_summary(self) -> dict[str, Any]:
        return {
            "model_version": self.model_version,
            "trained_at": self.trained_at,
            "selected_model": self.metrics["selected_model"],
            "threshold": self.threshold,
            "test_metrics": self.metrics["test"],
            "global_importance": self.metrics["global_importance"],
        }

    def _explain(self, frame: pd.DataFrame, probability: float) -> list[dict[str, Any]]:
        impacts = []
        for feature in FEATURE_COLUMNS:
            counterfactual = frame.copy()
            counterfactual.loc[counterfactual.index[0], feature] = self.reference_values[feature]
            reference_probability = float(self.model.predict_proba(counterfactual)[:, 1][0])
            impact = probability - reference_probability
            impacts.append(
                {
                    "feature": feature,
                    "label": FEATURE_LABELS[feature],
                    "value": _native_value(frame.iloc[0][feature]),
                    "reference": self.reference_values[feature],
                    "impact": impact,
                    "direction": "raises" if impact > 0 else "reduces",
                }
            )
        return sorted(impacts, key=lambda item: abs(item["impact"]), reverse=True)[:3]

    def _risk_level(self, probability: float) -> str:
        if probability >= self.threshold:
            return "critical"
        if probability >= self.threshold * 0.5:
            return "watch"
        return "nominal"

    def _write_log(self, reading: dict[str, Any], result: dict[str, Any]) -> None:
        assert self.log_path is not None
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "reading": {key: _native_value(value) for key, value in reading.items()},
            "prediction": result,
        }
        with self.log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry) + "\n")


def _native_value(value: Any) -> str | float | int | bool | None:
    if hasattr(value, "item"):
        return value.item()
    return value
