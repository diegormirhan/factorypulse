from fastapi.testclient import TestClient

from factorypulse.api import app, get_predictor


class FakePredictor:
    def predict_one(self, reading: dict) -> dict:
        return {
            "failure_probability": 0.72,
            "risk_level": "critical",
            "requires_inspection": True,
            "decision_threshold": 0.2,
            "drivers": [
                {
                    "feature": "torque_nm",
                    "label": "Torque",
                    "value": reading["torque_nm"],
                    "reference": 40.2,
                    "impact": 0.4,
                    "direction": "raises",
                }
            ],
            "model_version": "test",
        }


def test_prediction_endpoint_validates_and_scores_reading() -> None:
    app.dependency_overrides[get_predictor] = lambda: FakePredictor()
    client = TestClient(app)

    response = client.post(
        "/api/predict",
        json={
            "product_type": "L",
            "air_temperature_k": 303.9,
            "process_temperature_k": 312.9,
            "rotational_speed_rpm": 1_342,
            "torque_nm": 62.4,
            "tool_wear_min": 214,
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["requires_inspection"] is True


def test_prediction_endpoint_rejects_out_of_range_reading() -> None:
    app.dependency_overrides[get_predictor] = lambda: FakePredictor()
    client = TestClient(app)
    response = client.post(
        "/api/predict",
        json={
            "product_type": "L",
            "air_temperature_k": 900,
            "process_temperature_k": 312.9,
            "rotational_speed_rpm": 1_342,
            "torque_nm": 62.4,
            "tool_wear_min": 214,
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 422
