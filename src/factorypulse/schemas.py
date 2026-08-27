from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MachineReading(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_type: Literal["L", "M", "H"]
    air_temperature_k: float = Field(ge=250, le=350)
    process_temperature_k: float = Field(ge=250, le=370)
    rotational_speed_rpm: int = Field(ge=500, le=4_000)
    torque_nm: float = Field(ge=0, le=120)
    tool_wear_min: int = Field(ge=0, le=500)


class RiskDriver(BaseModel):
    feature: str
    label: str
    value: str | float | int | bool | None
    reference: str | float
    impact: float
    direction: Literal["raises", "reduces"]


class PredictionResponse(BaseModel):
    failure_probability: float
    risk_level: Literal["nominal", "watch", "critical"]
    requires_inspection: bool
    decision_threshold: float
    drivers: list[RiskDriver]
    model_version: str


class HealthResponse(BaseModel):
    status: Literal["ready", "model_missing"]
    model_version: str | None = None
