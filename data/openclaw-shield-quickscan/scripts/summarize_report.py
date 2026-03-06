#!/usr/bin/env python3
import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
    "unknown": 5,
}


def _normalize_severity(value: Any) -> str:
    text = str(value).strip().lower() if value is not None else ""
    aliases = {
        "crit": "critical",
        "warn": "medium",
        "warning": "medium",
        "informational": "info",
    }
    if text in aliases:
        return aliases[text]
    if text in SEVERITY_ORDER:
        return text
    return "unknown"


def _first_present(d: Dict[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        if key in d and d[key] not in (None, ""):
            return d[key]
    return default


def _extract_findings(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        return []

    for key in ("findings", "issues", "alerts", "results", "threats"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    for key in ("report", "data", "scan"):
        value = payload.get(key)
        if isinstance(value, dict):
            nested = _extract_findings(value)
            if nested:
                return nested

    collected: List[Dict[str, Any]] = []
    for value in payload.values():
        if isinstance(value, list):
            collected.extend([item for item in value if isinstance(item, dict)])
    return collected


def _finding_tuple(finding: Dict[str, Any]) -> Tuple[str, str, str, str]:
    severity = _normalize_severity(
        _first_present(finding, ("severity", "risk", "level"), "unknown")
    )
    path = str(_first_present(finding, ("file", "path", "filename", "target"), "unknown"))
    line = _first_present(finding, ("line", "line_no", "lineNumber", "start_line"), "?")
    rule = str(_first_present(finding, ("rule_id", "rule", "name", "check"), "unknown-rule"))
    message = str(
        _first_present(
            finding,
            ("message", "description", "reason", "detail", "summary"),
            "No description provided.",
        )
    )
    path_line = f"{path}:{line}"
    return severity, path_line, rule, message


def summarize(report_path: Path, top_n: int) -> int:
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Report file not found: {report_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON report ({report_path}): {exc}", file=sys.stderr)
        return 1

    findings = _extract_findings(payload)
    tuples = [_finding_tuple(item) for item in findings]
    counts = Counter(severity for severity, _, _, _ in tuples)

    print(f"Report: {report_path}")
    print(f"Total findings: {len(tuples)}")

    if counts:
        ordered = sorted(counts.items(), key=lambda x: SEVERITY_ORDER.get(x[0], 99))
        severity_text = ", ".join(f"{k}={v}" for k, v in ordered)
        print(f"Severity: {severity_text}")
    else:
        print("Severity: none")

    if not tuples:
        print("Top findings: none")
        return 0

    tuples.sort(key=lambda row: SEVERITY_ORDER.get(row[0], 99))
    print("Top findings:")
    for idx, (severity, path_line, rule, message) in enumerate(tuples[:top_n], start=1):
        print(f"{idx}. [{severity.upper()}] {path_line} | {rule} | {message}")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize an OpenClaw Shield JSON report.")
    parser.add_argument("report", type=Path, help="Path to scanner JSON report")
    parser.add_argument("--top", type=int, default=5, help="Number of findings to print")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return summarize(args.report, max(1, args.top))


if __name__ == "__main__":
    raise SystemExit(main())
