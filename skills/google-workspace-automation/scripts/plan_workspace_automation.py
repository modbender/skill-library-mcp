#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


SERVICE_SCOPES = {
    "gmail": "https://www.googleapis.com/auth/gmail.modify",
    "drive": "https://www.googleapis.com/auth/drive",
    "sheets": "https://www.googleapis.com/auth/spreadsheets",
    "calendar": "https://www.googleapis.com/auth/calendar",
    "docs": "https://www.googleapis.com/auth/documents",
}
MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Google Workspace automation plan.")
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
            f"- automation_name: {details['automation_name']}",
            "",
            "## OAuth Scopes",
        ]
        for scope in details["oauth_scopes"]:
            lines.append(f"- {scope}")
        lines.extend(["", "## Actions"])
        for action in details["actions"]:
            lines.append(f"- {action['name']} ({action['service']})")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "service"])
        writer.writeheader()
        writer.writerows(result["details"]["actions"])


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    automation_name = str(payload.get("automation_name", "workspace-automation"))
    services = payload.get("services", [])
    actions = payload.get("actions", [])
    if not isinstance(services, list):
        services = []
    if not isinstance(actions, list):
        actions = []

    normalized_services = [str(item).lower() for item in services]
    scopes = []
    for service in normalized_services:
        scope = SERVICE_SCOPES.get(service)
        if scope:
            scopes.append(scope)
    scopes = sorted(set(scopes))

    normalized_actions = []
    for action in actions:
        normalized_actions.append(
            {
                "name": str(action.get("name", "unnamed-action")),
                "service": str(action.get("service", "unknown")).lower(),
            }
        )

    details = {
        "automation_name": automation_name,
        "oauth_scopes": scopes,
        "actions": normalized_actions,
        "schedule": str(payload.get("schedule", "manual")),
        "retry_policy": str(payload.get("retry_policy", "exponential-backoff")),
        "dry_run": args.dry_run,
    }

    result = {
        "status": "ok" if normalized_actions else "warning",
        "summary": (
            f"Planned workspace automation '{automation_name}'"
            if normalized_actions
            else f"No actions supplied for '{automation_name}'"
        ),
        "artifacts": [str(Path(args.output))],
        "details": details,
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
