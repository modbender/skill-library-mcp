#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path


PHASE_RULES = [
    ("detect", ["alert", "detect", "triage"]),
    ("contain", ["contain", "isolate", "block"]),
    ("eradicate", ["eradicate", "remove", "clean"]),
    ("recover", ["recover", "restore", "validate"]),
    ("post-incident", ["lessons", "postmortem", "review"]),
]
MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an incident response timeline report.")
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


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def classify_phase(event_name: str) -> str:
    lower = event_name.lower()
    for phase, keywords in PHASE_RULES:
        if any(keyword in lower for keyword in keywords):
            return phase
    return "detect"


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
            f"- incident_id: {result['details']['incident_id']}",
            "",
            "## Timeline",
        ]
        for item in result["details"]["timeline"]:
            lines.append(f"- {item['time']} | {item['phase']} | {item['event']}")
        lines.extend(["", "## Phase Counts"])
        for phase, count in result["details"]["phase_counts"].items():
            lines.append(f"- {phase}: {count}")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "event", "phase", "severity"])
        writer.writeheader()
        writer.writerows(result["details"]["timeline"])


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    incident_id = str(payload.get("incident_id", "INC-UNKNOWN"))
    events = payload.get("events", [])
    if not isinstance(events, list):
        events = []

    normalized = []
    for entry in events:
        raw_time = str(entry.get("time", "1970-01-01T00:00:00Z"))
        raw_event = str(entry.get("event", "unknown_event"))
        severity = str(entry.get("severity", "unknown"))
        normalized.append(
            {
                "time": raw_time,
                "event": raw_event,
                "phase": classify_phase(raw_event),
                "severity": severity,
                "_sort": parse_time(raw_time),
            }
        )

    normalized.sort(key=lambda row: row["_sort"])
    for row in normalized:
        row.pop("_sort", None)

    phase_counts: dict[str, int] = {}
    for row in normalized:
        phase_counts[row["phase"]] = phase_counts.get(row["phase"], 0) + 1

    status = "ok" if normalized else "warning"
    summary = (
        f"Generated IR timeline with {len(normalized)} events"
        if normalized
        else "No events supplied; generated empty IR timeline"
    )
    result = {
        "status": status,
        "summary": summary,
        "artifacts": [str(Path(args.output))],
        "details": {
            "incident_id": incident_id,
            "timeline": normalized,
            "phase_counts": phase_counts,
            "dry_run": args.dry_run,
        },
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
