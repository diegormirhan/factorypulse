from pathlib import Path

import pandas as pd

from factorypulse.inference import Predictor


def test_predictor_scores_explains_and_logs_stress_reading(tmp_path: Path) -> None:
    log_path = tmp_path / "predictions.jsonl"
    predictor = Predictor(Path("artifacts/model_bundle.joblib"), log_path)

    result = predictor.predict_one(
        {
            "product_type": "L",
            "air_temperature_k": 303.9,
            "process_temperature_k": 312.9,
            "rotational_speed_rpm": 1_342,
            "torque_nm": 62.4,
            "tool_wear_min": 214,
        }
    )

    assert result["risk_level"] == "critical"
    assert result["failure_probability"] > 0.95
    assert len(result["drivers"]) == 3
    assert log_path.read_text(encoding="utf-8").count("\n") == 1


def test_predictor_scores_batch_and_exposes_model_summary() -> None:
    predictor = Predictor(Path("artifacts/model_bundle.joblib"))
    readings = pd.DataFrame(
        [
            {
                "product_type": "M",
                "air_temperature_k": 300.1,
                "process_temperature_k": 309.8,
                "rotational_speed_rpm": 1_450,
                "torque_nm": 41.2,
                "tool_wear_min": 92,
            },
            {
                "product_type": "L",
                "air_temperature_k": 303.9,
                "process_temperature_k": 312.9,
                "rotational_speed_rpm": 1_342,
                "torque_nm": 62.4,
                "tool_wear_min": 214,
            },
        ]
    )

    scored = predictor.predict_batch(readings)
    summary = predictor.model_summary()

    assert scored["risk_level"].tolist() == ["nominal", "critical"]
    assert summary["selected_model"] == "balanced_random_forest"
