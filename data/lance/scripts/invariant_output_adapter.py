#!/usr/bin/env python3
"""
invariant_output_adapter.py
Convert invariant scanner output into Lance finding schema.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SEVERITY_MAP = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "info": "Low",
    "informational": "Low",
}


def normalize_severity(s: str) -> str:
    if not s:
        return "Medium"
    return SEVERITY_MAP.get(s.lower(), "Medium")


def normalize_confidence(raw: Any) -> str:
    if isinstance(raw, (int, float)):
        v = float(raw)
        if v >= 0.85:
            return "Confirmed"
        if v >= 0.65:
            return "Probable"
        return "Theoretical"
    if isinstance(raw, str):
        low = raw.lower()
        if low in {"confirmed", "probable", "theoretical"}:
            return low.capitalize()
    return "Probable"


def collect_raw_findings(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []

    for key in ("findings", "Findings", "vulnerabilities", "Vulnerabilities"):
        val = payload.get(key)
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]

    # Some outputs are one finding object.
    keys = {"title", "severity", "description", "rule_id"}
    if keys.intersection(payload.keys()):
        return [payload]
    return []


def adapt_finding(raw: dict[str, Any], chain: str) -> dict[str, Any]:
    title = raw.get("title") or raw.get("Title") or raw.get("rule_id") or "Untitled Finding"
    desc = raw.get("description") or raw.get("Description") or ""
    file_path = raw.get("file") or raw.get("File") or ""
    line = raw.get("line") or raw.get("Line") or ""
    context = raw.get("context") or raw.get("Context") or ""
    confidence = raw.get("confidence", raw.get("Confidence"))
    severity = raw.get("severity", raw.get("Severity", "medium"))
    rule_id = raw.get("rule_id") or raw.get("RuleID") or raw.get("id") or ""
    category = raw.get("category") or raw.get("Category") or ""

    evidence = []
    if file_path:
        evidence.append(f"Source: {file_path}:{line}".rstrip(":"))
    if context:
        evidence.append(f"Context: {context}")

    return {
        "title": title,
        "severity": normalize_severity(str(severity)),
        "confidence": normalize_confidence(confidence),
        "target": raw.get("contract") or raw.get("contract_address") or "unknown",
        "chain_environment": chain,
        "affected_components": [x for x in [file_path, category, rule_id] if x],
        "attack_prerequisites": raw.get("prerequisites", "Untrusted caller access"),
        "exploit_path": raw.get("attack_path", "See technical evidence and context."),
        "expected_vs_actual_state_change": raw.get("state_change", "Not provided"),
        "economic_feasibility": raw.get("economic", "Needs validation"),
        "impact": raw.get("impact", desc or "Potential security impact."),
        "evidence": evidence,
        "suggested_verification": raw.get("verification", "Validate on test/fork with transaction sequence."),
        "recommended_fix": raw.get("remediation", raw.get("fix", "Apply least-privilege and invariant-safe controls.")),
        "source_tool": "invariant",
        "source_rule_id": rule_id,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Adapt invariant output to Lance finding schema.")
    parser.add_argument("input", help="Invariant output JSON file.")
    parser.add_argument("--chain", default="ethereum", help="Chain/environment label.")
    parser.add_argument("--output", "-o", help="Output file for Lance-compatible findings.")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    raw_findings = collect_raw_findings(payload)
    adapted = [adapt_finding(f, args.chain) for f in raw_findings]

    out = {
        "schema_version": "1.0",
        "source": "invariant",
        "finding_count": len(adapted),
        "findings": adapted,
    }
    content = json.dumps(out, indent=2)

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Adapted findings saved: {args.output}")
    else:
        print(content)


if __name__ == "__main__":
    main()
