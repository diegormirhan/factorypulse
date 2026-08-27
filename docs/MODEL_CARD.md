# FactoryPulse Model Card

## Model details

- Version: 0.1.0
- Task: binary classification of machine failure
- Selected estimator: class-balanced random forest
- Probability calibration: five-fold sigmoid calibration
- Decision threshold: 0.204221
- Training date: 2026-08-24
- Runtime: scikit-learn 1.9 on Python 3.12

The saved bundle contains the calibrated estimator, inspection threshold, training reference values, model metadata, and evaluation summary.

## Intended use

The model demonstrates an auditable predictive-maintenance workflow for a portfolio, classroom, or technical interview. It may be used to explore model selection, imbalanced classification, calibration, threshold policy, explanations, API serving, and drift monitoring.

It is not intended for autonomous maintenance decisions, worker-safety controls, real equipment shutdown logic, or any production use without validation on representative local data and review by qualified reliability engineers.

## Training data

AI4I 2020 is a synthetic dataset containing 10,000 records and 339 machine-failure labels. See [DATA_CARD.md](DATA_CARD.md).

The split is stratified and deterministic: 7,000 training records, 1,500 validation records, and 1,500 test records.

UDI and Product ID are discarded. TWF, HDF, PWF, OSF, and RNF are failure-mode targets and are explicitly excluded to prevent target leakage.

## Features

The model uses product grade, air temperature, process temperature, rotational speed, torque, and tool wear. It derives temperature gap, mechanical power, and wear-load index within the serialized pipeline.

## Selection

Average precision on the validation partition selected the calibrated random forest:

| Candidate | Validation AP |
|---|---:|
| Balanced logistic regression | 0.3540 |
| Balanced random forest | 0.8426 |

## Holdout evaluation

| Metric | Value |
|---|---:|
| Average precision | 0.9314 |
| ROC AUC | 0.9772 |
| Brier score | 0.0048 |
| Precision | 0.8679 |
| Recall | 0.9020 |
| F1 | 0.8846 |
| Expected cost per record | 0.0880 |

Confusion matrix at the selected threshold: TN 1,442; FP 7; FN 5; TP 46.

## Threshold policy

The threshold is selected on the validation partition by assigning a cost of 25 to each false negative and 1 to each false positive. Those values encode a demonstration policy, not measured industrial economics. They must be re-estimated with domain stakeholders before any applied use.

## Explainability

Global importance uses average-precision permutation importance on the unseen test set. Single-record explanations replace one raw feature at a time with its training median or mode and report the change in predicted probability.

Neither method is causal. Correlated temperature and load features can dilute, share, or distort individual importance values.

## Limitations and risks

- Synthetic data can make decision boundaries cleaner than real sensor streams.
- Random splitting does not represent future equipment behavior or site transfer.
- Model performance is uncertain for values outside the dataset distribution.
- No subgroup represents protected human attributes; product grade is an equipment category, not a person.
- Drift alerts require adequate batch sizes and should trigger investigation, not automatic retraining.
- Calibration and threshold performance should be rechecked after retraining or data-source changes.

## Reproducibility

Run `uv run factorypulse train` from the repository root. The random seed and product-level training parameters are declared in `config.yaml`. Generated evidence is saved under `artifacts/`.

