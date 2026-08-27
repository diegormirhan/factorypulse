from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ProjectConfig:
    random_seed: int
    model_version: str


@dataclass(frozen=True)
class DatasetConfig:
    source_url: str


@dataclass(frozen=True)
class PathConfig:
    raw_data: Path
    model_bundle: Path
    metrics: Path
    reference_profile: Path
    predictions_log: Path


@dataclass(frozen=True)
class TrainingConfig:
    test_size: float
    validation_size: float
    calibration_folds: int
    false_negative_cost: float
    false_positive_cost: float
    threshold_min: float
    threshold_max: float
    threshold_steps: int
    permutation_repeats: int


@dataclass(frozen=True)
class MonitoringConfig:
    psi_bins: int
    minimum_batch_size: int
    warning_threshold: float
    critical_threshold: float


@dataclass(frozen=True)
class ApiConfig:
    host: str
    port: int


@dataclass(frozen=True)
class Settings:
    project: ProjectConfig
    dataset: DatasetConfig
    paths: PathConfig
    training: TrainingConfig
    monitoring: MonitoringConfig
    api: ApiConfig
    root: Path


def load_settings(config_path: str | Path = "config.yaml") -> Settings:
    resolved_config = Path(config_path).resolve()
    raw = _read_yaml(resolved_config)
    root = resolved_config.parent
    paths = {name: _resolve(root, value) for name, value in raw["paths"].items()}
    settings = Settings(
        project=ProjectConfig(**raw["project"]),
        dataset=DatasetConfig(**raw["dataset"]),
        paths=PathConfig(**paths),
        training=TrainingConfig(**raw["training"]),
        monitoring=MonitoringConfig(**raw["monitoring"]),
        api=ApiConfig(**raw["api"]),
        root=root,
    )
    _validate(settings)
    return settings


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open(encoding="utf-8") as stream:
        content = yaml.safe_load(stream)
    if not isinstance(content, dict):
        raise ValueError(f"Configuration must be a mapping: {path}")
    return content


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _validate(settings: Settings) -> None:
    training = settings.training
    if training.test_size + training.validation_size >= 1:
        raise ValueError("test_size + validation_size must be smaller than 1")
    if training.false_negative_cost <= training.false_positive_cost:
        raise ValueError("false_negative_cost must exceed false_positive_cost")
    monitoring = settings.monitoring
    if monitoring.warning_threshold >= monitoring.critical_threshold:
        raise ValueError("warning_threshold must be smaller than critical_threshold")
