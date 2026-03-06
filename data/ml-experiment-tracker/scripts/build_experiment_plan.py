#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a reproducible ML experiment plan.")
    parser.add_argument("--input", required=False, help="Path to JSON input.")
    parser.add_argument("--output", required=True, help="Path to output artifact.")
    parser.add_argument("--format", choices=["json", "md", "csv"], default="json")
    parser.add_argument("--dry-run", action="store_true", help="Run without side effects.")
    return parser.parse_args()


def load_payload(path: str | None, max_input_bytes: int = MAX_INPUT_BYTES) -> dict:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p}")
    if p.stat().st_size > max_input_bytes:
        raise ValueError(f"Input file exceeds {max_input_bytes} bytes: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def render(result: dict, output_path: Path, fmt: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return

    if fmt == "md":
        details = result["details"]
        lines = [
            f"# {result['summary']}",
            "",
            f"- status: {result['status']}",
            f"- experiment_name: {details['experiment_name']}",
            f"- dataset: {details['dataset']}",
            "",
            "## Metrics",
        ]
        for metric in details["metrics"]:
            lines.append(f"- {metric}")
        lines.extend(["", "## Parameters"])
        for key, value in details["parameters"].items():
            lines.append(f"- {key}: {value}")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    details = result["details"]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["field", "value"])
        writer.writerow(["experiment_name", details["experiment_name"]])
        writer.writerow(["dataset", details["dataset"]])
        writer.writerow(["metrics", ",".join(details["metrics"])])
        for key, value in details["parameters"].items():
            writer.writerow([f"param:{key}", value])


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)

    experiment_name = str(payload.get("experiment_name", "baseline-experiment"))
    dataset = str(payload.get("dataset", "data/dataset.csv"))
    parameters = payload.get("parameters", {})
    metrics = payload.get("metrics", ["accuracy", "f1"])

    if not isinstance(parameters, dict):
        parameters = {}
    if not isinstance(metrics, list):
        metrics = ["accuracy"]

    details = {
        "experiment_name": experiment_name,
        "dataset": dataset,
        "metrics": [str(metric) for metric in metrics],
        "parameters": {str(key): value for key, value in parameters.items()},
        "tracking_tags": {
            "owner": str(payload.get("owner", "ml-team")),
            "environment": str(payload.get("environment", "dev")),
        },
        "artifact_expectations": [
            "metrics.json",
            "model.pkl or model.bin",
            "feature_schema.json",
        ],
        "dry_run": args.dry_run,
    }

    result = {
        "status": "ok",
        "summary": f"Built experiment plan for '{experiment_name}'",
        "artifacts": [str(Path(args.output))],
        "details": details,
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
