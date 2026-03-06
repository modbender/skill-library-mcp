#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


OWASP_MAP = {
    "A01 Broken Access Control": ["access control", "authorization", "mfa", "privilege"],
    "A02 Cryptographic Failures": ["crypto", "encryption", "tls", "plaintext"],
    "A03 Injection": ["sql injection", "xss", "command injection", "injection"],
    "A04 Insecure Design": ["insecure design", "threat model", "design flaw"],
    "A05 Security Misconfiguration": ["misconfiguration", "default password", "open bucket"],
    "A06 Vulnerable Components": ["outdated dependency", "vulnerable package", "cve"],
    "A07 Identification and Authentication Failures": ["authentication", "password reset", "session"],
    "A08 Software and Data Integrity Failures": ["integrity", "unsigned update", "supply chain"],
    "A09 Security Logging and Monitoring Failures": ["logging", "monitoring", "audit trail"],
    "A10 SSRF": ["ssrf", "server-side request forgery"],
}
MAX_INPUT_BYTES = 1_048_576


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map findings to OWASP Top 10 categories.")
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


def classify_finding(text: str) -> str:
    lowered = text.lower()
    for category, keywords in OWASP_MAP.items():
        if any(word in lowered for word in keywords):
            return category
    return "A04 Insecure Design"


def build_checklist(categories: list[str]) -> dict[str, list[str]]:
    checklist: dict[str, list[str]] = {}
    for category in categories:
        if category == "A03 Injection":
            checklist[category] = [
                "Use parameterized queries for data access paths.",
                "Apply strict input validation and output encoding.",
            ]
        elif category == "A01 Broken Access Control":
            checklist[category] = [
                "Enforce authorization checks server-side for every request.",
                "Review role permissions and least-privilege defaults.",
            ]
        else:
            checklist[category] = [
                "Add category-specific control checks to SDLC gates.",
                "Create follow-up tickets with remediation owners and due dates.",
            ]
    return checklist


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
            "## Findings By Category",
        ]
        for category, count in result["details"]["category_counts"].items():
            lines.append(f"- {category}: {count}")
        lines.extend(["", "## Remediation Checklist"])
        for category, actions in result["details"]["remediation_checklist"].items():
            lines.append(f"- {category}")
            for action in actions:
                lines.append(f"  - {action}")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "severity", "category", "title"],
        )
        writer.writeheader()
        writer.writerows(result["details"]["mapped_findings"])


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    mapped = []
    category_counts: dict[str, int] = {}

    for finding in findings:
        title = str(finding.get("title", "unlabeled finding"))
        category = classify_finding(title)
        severity = str(finding.get("severity", "unknown"))
        row = {
            "id": str(finding.get("id", "unknown")),
            "severity": severity,
            "category": category,
            "title": title,
        }
        mapped.append(row)
        category_counts[category] = category_counts.get(category, 0) + 1

    checklist = build_checklist(list(category_counts.keys()))
    status = "ok" if mapped else "warning"
    summary = (
        f"Mapped {len(mapped)} findings to OWASP categories"
        if mapped
        else "No findings supplied; produced empty OWASP mapping"
    )
    result = {
        "status": status,
        "summary": summary,
        "artifacts": [str(Path(args.output))],
        "details": {
            "mapped_findings": mapped,
            "category_counts": category_counts,
            "remediation_checklist": checklist,
            "dry_run": args.dry_run,
        },
    }

    render(result, Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
