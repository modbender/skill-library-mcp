#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose a Docs pipeline specification.")
    parser.add_argument("--input", required=False, help="Path to JSON input.")
    parser.add_argument("--output", required=True, help="Path to output artifact.")
    parser.add_argument("--format", choices=["json", "md", "csv"], default="json")
    parser.add_argument("--dry-run", action="store_true", help="Run without side effects.")
    return parser.parse_args()


def load_payload(path: str | None, max_input_bytes: int = MAX_INPUT_BYTES) -> dict:
    if not path:
        return {}
    payload_path = Path(path)
    if not payload_path.exists():
        raise FileNotFoundError(f"Input file not found: {payload_path}")
    if payload_path.stat().st_size > max_input_bytes:
        raise ValueError(f"Input file exceeds {max_input_bytes} bytes: {payload_path}")
    return json.loads(payload_path.read_text(encoding="utf-8"))


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
            f"- pipeline_name: {details['pipeline_name']}",
            "",
            "## Sources",
        ]
        for src in details["sources"]:
            lines.append(f"- {src}")
        lines.extend(["", "## Steps"])
        for step in details["steps"]:
            lines.append(f"- {step['order']}. {step['name']}")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["order", "name"])
        writer.writeheader()
        writer.writerows(result["details"]["steps"])


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)

    pipeline_name = str(payload.get("pipeline_name", "docs-pipeline"))
    sources = payload.get("sources", [])
    if not isinstance(sources, list):
        sources = []

    template_doc = str(payload.get("template_doc", "docs://template"))
    destination_doc = str(payload.get("destination_doc", "docs://destination"))

    steps = [
        {"order": 1, "name": "extract_sources"},
        {"order": 2, "name": "normalize_data"},
        {"order": 3, "name": "render_template"},
        {"order": 4, "name": "publish_document"},
    ]

    result = {
        "status": "ok" if sources else "warning",
        "summary": (
            f"Composed docs pipeline '{pipeline_name}'"
            if sources
            else f"No sources supplied for pipeline '{pipeline_name}'"
        ),
        "artifacts": [str(Path(args.output))],
        "details": {
            "pipeline_name": pipeline_name,
            "sources": [str(source) for source in sources],
            "template_doc": template_doc,
            "destination_doc": destination_doc,
            "steps": steps,
            "dry_run": args.dry_run,
        },
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
