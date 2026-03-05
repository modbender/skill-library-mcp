#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

REQUIRED_TOP = [
    "timestamp",
    "workspace",
    "scores",
    "deltas_vs_previous",
    "key_findings",
    "risk_flags",
    "recommendations",
]

SCORE_KEYS = ["overall", "memory", "retrieval", "productive", "quality", "focus"]


def fail(errors, json_out=False):
    if json_out:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
    else:
        for err in errors:
            print(f"- {err}")
    return 1


def main():
    parser = argparse.ArgumentParser(description="Validate Clawditor latest_report.json structure.")
    parser.add_argument("path", nargs="?", default="eval/latest_report.json", help="Path to latest_report.json")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        return fail([f"missing file: {path}"], args.json)

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        return fail([f"invalid json: {exc}"], args.json)

    errors = []
    if not isinstance(data, dict):
        return fail(["top-level JSON must be an object"], args.json)

    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"missing key: {key}")

    workspace = data.get("workspace", {})
    if not isinstance(workspace, dict):
        errors.append("workspace must be an object")
    else:
        if not isinstance(workspace.get("path"), str):
            errors.append("workspace.path must be a string")
        if not isinstance(workspace.get("hash_or_git_head"), str):
            errors.append("workspace.hash_or_git_head must be a string")

    for section in ["scores", "deltas_vs_previous"]:
        block = data.get(section, {})
        if not isinstance(block, dict):
            errors.append(f"{section} must be an object")
            continue
        for key in SCORE_KEYS:
            if key not in block:
                errors.append(f"{section} missing {key}")
            elif not isinstance(block.get(key), (int, float)):
                errors.append(f"{section}.{key} must be a number")

    if not isinstance(data.get("key_findings", []), list):
        errors.append("key_findings must be an array")
    if not isinstance(data.get("risk_flags", []), list):
        errors.append("risk_flags must be an array")

    recs = data.get("recommendations", [])
    if not isinstance(recs, list):
        errors.append("recommendations must be an array")
    else:
        for i, rec in enumerate(recs):
            if not isinstance(rec, dict):
                errors.append(f"recommendations[{i}] must be an object")
                continue
            if not isinstance(rec.get("title"), str):
                errors.append(f"recommendations[{i}].title must be a string")
            if rec.get("impact") not in {"high", "med", "low"}:
                errors.append(f"recommendations[{i}].impact must be high|med|low")
            if rec.get("effort") not in {"high", "med", "low"}:
                errors.append(f"recommendations[{i}].effort must be high|med|low")
            steps = rec.get("steps")
            if not isinstance(steps, list):
                errors.append(f"recommendations[{i}].steps must be an array")

    if errors:
        return fail(errors, args.json)

    if args.json:
        print(json.dumps({"ok": True}, indent=2))
    else:
        print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
