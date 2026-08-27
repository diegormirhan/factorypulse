from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn

from factorypulse.acquisition import download_dataset
from factorypulse.config import load_settings
from factorypulse.data import load_prediction_csv
from factorypulse.inference import Predictor
from factorypulse.modeling import train
from factorypulse.monitoring import calculate_drift


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    settings = load_settings(args.config)

    if args.command == "download":
        path = download_dataset(settings.dataset.source_url, settings.paths.raw_data)
        print(f"Downloaded AI4I 2020 dataset -> {path}")
        return
    if args.command == "train":
        print(json.dumps(train(settings), indent=2))
        return
    if args.command == "predict":
        reading = {
            "product_type": args.product_type,
            "air_temperature_k": args.air_temperature_k,
            "process_temperature_k": args.process_temperature_k,
            "rotational_speed_rpm": args.rotational_speed_rpm,
            "torque_nm": args.torque_nm,
            "tool_wear_min": args.tool_wear_min,
        }
        predictor = Predictor(settings.paths.model_bundle, settings.paths.predictions_log)
        print(json.dumps(predictor.predict_one(reading), indent=2))
        return
    if args.command == "batch":
        predictor = Predictor(settings.paths.model_bundle, settings.paths.predictions_log)
        scored = predictor.predict_batch(load_prediction_csv(Path(args.input)))
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        scored.to_csv(output, index=False)
        print(f"Scored {len(scored)} readings -> {output}")
        return
    if args.command == "drift":
        current = load_prediction_csv(Path(args.input))
        report = calculate_drift(current, settings.paths.reference_profile, settings)
        print(json.dumps(report, indent=2))
        return
    if args.command == "serve":
        uvicorn.run(
            "factorypulse.api:app",
            host=settings.api.host,
            port=settings.api.port,
            reload=args.reload,
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="factorypulse")
    parser.add_argument("--config", default="config.yaml")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("download", help="Download the AI4I dataset from UCI.")
    subparsers.add_parser("train", help="Train, calibrate, evaluate, and save the model.")

    predict_parser = subparsers.add_parser("predict", help="Score one machine reading.")
    predict_parser.add_argument("--product-type", choices=["L", "M", "H"], required=True)
    predict_parser.add_argument("--air-temperature-k", type=float, required=True)
    predict_parser.add_argument("--process-temperature-k", type=float, required=True)
    predict_parser.add_argument("--rotational-speed-rpm", type=int, required=True)
    predict_parser.add_argument("--torque-nm", type=float, required=True)
    predict_parser.add_argument("--tool-wear-min", type=int, required=True)

    batch_parser = subparsers.add_parser("batch", help="Score a CSV file.")
    batch_parser.add_argument("--input", required=True)
    batch_parser.add_argument("--output", default="artifacts/scored_machines.csv")

    drift_parser = subparsers.add_parser("drift", help="Compare a CSV to the training reference.")
    drift_parser.add_argument("--input", required=True)

    serve_parser = subparsers.add_parser("serve", help="Start the API and dashboard.")
    serve_parser.add_argument("--reload", action="store_true")
    return parser


if __name__ == "__main__":
    main()
