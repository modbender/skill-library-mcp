#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a transformer fine-tuning plan.")
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
            f"- model_name: {details['model_name']}",
            f"- task: {details['task']}",
            f"- dataset: {details['dataset']}",
            "",
            "## Training Config",
        ]
        for key, value in details["training_config"].items():
            lines.append(f"- {key}: {value}")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["field", "value"])
        details = result["details"]
        writer.writerow(["model_name", details["model_name"]])
        writer.writerow(["task", details["task"]])
        writer.writerow(["dataset", details["dataset"]])
        for key, value in details["training_config"].items():
            writer.writerow([f"train:{key}", value])


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)

    model_name = str(payload.get("model_name", "distilbert-base-uncased"))
    task = str(payload.get("task", "sequence-classification"))
    dataset = str(payload.get("dataset", "dataset-name"))
    training_config = {
        "num_epochs": int(payload.get("num_epochs", 3)),
        "learning_rate": float(payload.get("learning_rate", 2e-5)),
        "batch_size": int(payload.get("batch_size", 16)),
        "seed": int(payload.get("seed", 42)),
        "evaluation_strategy": str(payload.get("evaluation_strategy", "epoch")),
        "output_dir": str(payload.get("output_dir", "artifacts/finetune-run")),
    }
    model_card = {
        "base_model": model_name,
        "task": task,
        "dataset": dataset,
        "evaluation_metrics": payload.get("evaluation_metrics", ["accuracy", "f1"]),
        "risk_notes": [
            "Validate dataset licensing before release.",
            "Run bias and robustness checks for production usage.",
        ],
    }

    result = {
        "status": "ok",
        "summary": f"Built fine-tuning plan for '{model_name}'",
        "artifacts": [str(Path(args.output))],
        "details": {
            "model_name": model_name,
            "task": task,
            "dataset": dataset,
            "training_config": training_config,
            "model_card": model_card,
            "dry_run": args.dry_run,
        },
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
