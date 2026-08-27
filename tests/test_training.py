from dataclasses import replace
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression

from factorypulse.config import load_settings
from factorypulse.inference import Predictor
from factorypulse.modeling import _build_pipeline, train


def test_training_pipeline_writes_reusable_artifacts(tmp_path: Path, monkeypatch) -> None:
    raw_subset = pd.read_csv("data/raw/ai4i2020.csv").head(1_000)
    raw_path = tmp_path / "ai4i.csv"
    raw_subset.to_csv(raw_path, index=False)
    base = load_settings()
    paths = replace(
        base.paths,
        raw_data=raw_path,
        model_bundle=tmp_path / "model.joblib",
        metrics=tmp_path / "metrics.json",
        reference_profile=tmp_path / "reference.json",
        predictions_log=tmp_path / "predictions.jsonl",
    )
    training = replace(base.training, calibration_folds=2, permutation_repeats=2)
    settings = replace(base, paths=paths, training=training)
    monkeypatch.setattr(
        "factorypulse.modeling._candidate_models",
        lambda random_seed: {
            "test_logistic": _build_pipeline(
                LogisticRegression(class_weight="balanced", max_iter=500, random_state=random_seed),
                scale_numeric=True,
            )
        },
    )

    metrics = train(settings)
    predictor = Predictor(paths.model_bundle)

    assert metrics["selected_model"] == "test_logistic"
    assert paths.metrics.exists()
    assert paths.reference_profile.exists()
    assert predictor.model_version == base.project.model_version
