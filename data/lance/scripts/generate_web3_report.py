#!/usr/bin/env python3
"""
generate_web3_report.py
Generate platform-specific Web3 vulnerability reports from structured finding JSON.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PLATFORMS = {"immunefi", "hackenproof", "hackerone-web3", "bugcrowd-web3"}


def load_finding(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "findings" in raw and isinstance(raw["findings"], list):
        if not raw["findings"]:
            raise ValueError("No findings in input.")
        return raw["findings"][0]
    if isinstance(raw, dict):
        return raw
    raise ValueError("Expected finding object JSON.")


def to_lines(value: Any) -> str:
    if isinstance(value, list):
        if not value:
            return "- [none]"
        return "\n".join(f"- {x}" for x in value)
    if value is None:
        return "- [none]"
    return str(value)


def base_fields(f: dict[str, Any]) -> dict[str, str]:
    return {
        "title": str(f.get("title", "Untitled Finding")),
        "severity": str(f.get("severity", "Medium")),
        "confidence": str(f.get("confidence", "Probable")),
        "target": str(f.get("target", "unknown")),
        "chain": str(f.get("chain_environment", "unknown")),
        "components": to_lines(f.get("affected_components", [])),
        "prereq": str(f.get("attack_prerequisites", "unknown")),
        "path": str(f.get("exploit_path", "Not provided")),
        "state_change": str(f.get("expected_vs_actual_state_change", "Not provided")),
        "economic": str(f.get("economic_feasibility", "Not provided")),
        "impact": str(f.get("impact", "Not provided")),
        "evidence": to_lines(f.get("evidence", [])),
        "verify": str(f.get("suggested_verification", "Not provided")),
        "fix": str(f.get("recommended_fix", "Not provided")),
    }


def render(platform: str, f: dict[str, Any]) -> str:
    b = base_fields(f)

    if platform == "immunefi":
        return f"""# {b['title']}

## Summary
Severity: {b['severity']} ({b['confidence']})

## Affected Target
- Target: {b['target']}
- Chain: {b['chain']}
- Components:
{b['components']}

## Technical Root Cause
{b['path']}

## Reproduction Outline
Prerequisites: {b['prereq']}

State change:
{b['state_change']}

## Economic and Security Impact
Economic feasibility: {b['economic']}

Impact:
{b['impact']}

## Evidence
{b['evidence']}

## Remediation
{b['fix']}
"""

    if platform == "hackenproof":
        return f"""# {b['title']}

## Summary
Severity: {b['severity']} ({b['confidence']})

## Affected Component / Protocol Layer
- Target: {b['target']}
- Chain: {b['chain']}
- Components:
{b['components']}

## Root Cause Analysis
{b['path']}

## Exploit Scenario
Prerequisites: {b['prereq']}

State delta:
{b['state_change']}

## Impact (Integrity, Authorization, Asset Risk)
{b['impact']}

Economic feasibility: {b['economic']}

## Severity Justification
Mapped to {b['severity']} because exploit path and impact are technically reproducible.

## Evidence
{b['evidence']}

## Recommended Fix
{b['fix']}
"""

    if platform == "hackerone-web3":
        return f"""# {b['title']}

## Summary
Severity: {b['severity']} ({b['confidence']})

## Affected Components
{b['components']}

## Reproduction Steps
Target: {b['target']} ({b['chain']})

Prerequisites: {b['prereq']}

Exploit path:
{b['path']}

Expected vs actual:
{b['state_change']}

## Impact
{b['impact']}

Economic feasibility:
{b['economic']}

## Evidence
{b['evidence']}

## Suggested Verification
{b['verify']}

## Recommended Fix
{b['fix']}
"""

    if platform == "bugcrowd-web3":
        return f"""## Summary
{b['title']}

Severity: {b['severity']} ({b['confidence']})

## Affected Asset
- {b['target']} ({b['chain']})
- Components:
{b['components']}

## Technical Details
Exploit path:
{b['path']}

Prerequisites: {b['prereq']}

Expected vs actual:
{b['state_change']}

## Business Impact
{b['impact']}

Economic feasibility:
{b['economic']}

## Supporting Evidence
{b['evidence']}

## Remediation
{b['fix']}
"""

    raise ValueError(f"Unsupported platform: {platform}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate platform-specific Web3 report markdown.")
    parser.add_argument("--platform", required=True, choices=sorted(PLATFORMS))
    parser.add_argument("--input", required=True, help="Input finding JSON.")
    parser.add_argument("--output", "-o", help="Output markdown file.")
    args = parser.parse_args()

    finding = load_finding(Path(args.input))
    report = render(args.platform, finding)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
