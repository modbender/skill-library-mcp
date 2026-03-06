#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a workflow automation blueprint.")
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
            f"- workflow_name: {details['workflow_name']}",
            f"- trigger: {details['trigger']}",
            "",
            "## Steps",
        ]
        for step in details["steps"]:
            lines.append(f"- {step['order']}. {step['name']} ({step['type']})")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["order", "name", "type", "on_failure"])
        writer.writeheader()
        writer.writerows(result["details"]["steps"])


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    workflow_name = str(payload.get("workflow_name", "workflow-blueprint"))
    trigger = str(payload.get("trigger", "manual"))
    steps = payload.get("steps", [])
    if not isinstance(steps, list):
        steps = []

    normalized_steps = []
    for idx, step in enumerate(steps, start=1):
        normalized_steps.append(
            {
                "order": idx,
                "name": str(step.get("name", f"step-{idx}")),
                "type": str(step.get("type", "task")),
                "on_failure": str(step.get("on_failure", "stop")),
            }
        )

    blueprint = {
        "name": workflow_name,
        "trigger": trigger,
        "steps": normalized_steps,
    }

    result = {
        "status": "ok" if normalized_steps else "warning",
        "summary": (
            f"Generated workflow blueprint with {len(normalized_steps)} steps"
            if normalized_steps
            else "No steps supplied; generated empty workflow blueprint"
        ),
        "artifacts": [str(Path(args.output))],
        "details": {
            "workflow_name": workflow_name,
            "trigger": trigger,
            "steps": normalized_steps,
            "n8n_blueprint": blueprint,
            "dry_run": args.dry_run,
        },
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
