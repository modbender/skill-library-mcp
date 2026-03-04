#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark model candidates using weighted metrics.")
    parser.add_argument("--input", required=False, help="Path to JSON input.")
    parser.add_argument("--output", required=True, help="Path to output artifact.")
    parser.add_argument("--format", choices=["json", "md", "csv"], default="json")
    parser.add_argument("--dry-run", action="store_true", help="Run without side effects.")
    return parser.parse_args()


def load_payload(path: str | None, max_input_bytes: int = MAX_INPUT_BYTES) -> dict:
    if not path:
        return {}
    input_path = Path(path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.stat().st_size > max_input_bytes:
        raise ValueError(f"Input file exceeds {max_input_bytes} bytes: {input_path}")
    return json.loads(input_path.read_text(encoding="utf-8"))


def weighted_score(metrics: dict, weights: dict) -> float:
    score = 0.0
    for metric, weight in weights.items():
        score += float(metrics.get(metric, 0.0)) * float(weight)
    return round(score, 6)


def render(result: dict, output_path: Path, fmt: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return

    if fmt == "md":
        lines = [
            f"# {result['summary']}",
            "",
            f"- status: {result['status']}",
            "",
            "## Leaderboard",
        ]
        for row in result["details"]["leaderboard"]:
            lines.append(f"- {row['rank']}. {row['name']} ({row['score']})")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["rank", "name", "score"])
        writer.writeheader()
        writer.writerows(result["details"]["leaderboard"])


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    weights = payload.get("weights", {"accuracy": 0.5, "f1": 0.5})
    models = payload.get("models", [])
    if not isinstance(weights, dict):
        weights = {"accuracy": 0.5, "f1": 0.5}
    if not isinstance(models, list):
        models = []

    scored = []
    for model in models:
        name = str(model.get("name", "unknown-model"))
        metrics = model.get("metrics", {})
        if not isinstance(metrics, dict):
            metrics = {}
        score = weighted_score(metrics, weights)
        scored.append({"name": name, "score": score})

    scored.sort(key=lambda item: item["score"], reverse=True)
    leaderboard = []
    for index, row in enumerate(scored, start=1):
        leaderboard.append({"rank": index, "name": row["name"], "score": row["score"]})

    status = "ok" if leaderboard else "warning"
    summary = (
        f"Ranked {len(leaderboard)} model candidates"
        if leaderboard
        else "No model candidates supplied; produced empty leaderboard"
    )
    result = {
        "status": status,
        "summary": summary,
        "artifacts": [str(Path(args.output))],
        "details": {
            "weights": {str(k): float(v) for k, v in weights.items()},
            "leaderboard": leaderboard,
            "recommended_model": leaderboard[0]["name"] if leaderboard else None,
            "dry_run": args.dry_run,
        },
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
