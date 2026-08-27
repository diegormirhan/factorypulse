from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from factorypulse.config import Settings, load_settings
from factorypulse.inference import Predictor
from factorypulse.schemas import HealthResponse, MachineReading, PredictionResponse


@lru_cache
def get_settings() -> Settings:
    return load_settings()


@lru_cache
def get_predictor() -> Predictor:
    settings = get_settings()
    try:
        return Predictor(settings.paths.model_bundle, settings.paths.predictions_log)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


api_router = APIRouter(prefix="/api", tags=["prediction"])
SettingsDependency = Annotated[Settings, Depends(get_settings)]
PredictorDependency = Annotated[Predictor, Depends(get_predictor)]


@api_router.get("/health")
def health(settings: SettingsDependency) -> HealthResponse:
    if not settings.paths.model_bundle.exists():
        return HealthResponse(status="model_missing")
    predictor = Predictor(settings.paths.model_bundle)
    return HealthResponse(status="ready", model_version=predictor.model_version)


@api_router.post("/predict")
def predict(reading: MachineReading, predictor: PredictorDependency) -> PredictionResponse:
    return PredictionResponse.model_validate(predictor.predict_one(reading.model_dump()))


@api_router.post("/predict/batch")
def predict_batch(
    readings: list[MachineReading], predictor: PredictorDependency
) -> list[PredictionResponse]:
    if not readings:
        raise HTTPException(status_code=422, detail="At least one machine reading is required.")
    if len(readings) > 1_000:
        raise HTTPException(status_code=413, detail="Batch limit is 1,000 readings.")
    return [
        PredictionResponse.model_validate(predictor.predict_one(reading.model_dump()))
        for reading in readings
    ]


@api_router.get("/model")
def model_summary(predictor: PredictorDependency) -> dict:
    return predictor.model_summary()


def create_app() -> FastAPI:
    application = FastAPI(
        title="FactoryPulse API",
        version="0.1.0",
        description="Local, explainable machine-failure risk scoring.",
    )
    application.include_router(api_router)
    web_directory = Path(__file__).parent / "web"
    application.mount("/assets", StaticFiles(directory=web_directory), name="assets")

    @application.get("/", include_in_schema=False)
    def dashboard() -> FileResponse:
        return FileResponse(web_directory / "index.html")

    return application


app = create_app()
