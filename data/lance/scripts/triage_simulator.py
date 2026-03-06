#!/usr/bin/env python3
"""
triage_simulator.py
Simulate strict Web3 triage outcomes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_findings(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("findings"), list):
        return [x for x in raw["findings"] if isinstance(x, dict)]
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        return [raw]
    return []


def evaluate(finding: dict[str, Any]) -> dict[str, Any]:
    title = str(finding.get("title", "Untitled Finding"))
    sev = str(finding.get("severity", "Medium")).capitalize()
    conf = str(finding.get("confidence", "Theoretical")).capitalize()
    evidence = finding.get("evidence", [])
    impact = str(finding.get("impact", ""))
    exploit = str(finding.get("exploit_path", ""))
    economic = str(finding.get("economic_feasibility", "")).lower()

    reasons: list[str] = []
    missing: list[str] = []

    if conf == "Theoretical":
        reasons.append("confidence is theoretical")
        missing.append("deterministic exploit evidence")

    if not exploit or "not provided" in exploit.lower():
        reasons.append("exploit path is incomplete")
        missing.append("transaction-level exploit sequence")

    if not impact or len(impact.strip()) < 20:
        reasons.append("impact is under-specified")
        missing.append("quantified impact statement")

    if not evidence:
        reasons.append("evidence list is empty")
        missing.append("technical proof (trace/code path/state delta)")

    if "needs validation" in economic or "unknown" in economic:
        reasons.append("economic feasibility is unresolved")
        missing.append("capital/liquidity/profit analysis")

    verdict = "Accepted"
    if reasons:
        verdict = "Needs More Evidence"
    if len(reasons) >= 4 or sev == "Low":
        verdict = "Rejected"

    return {
        "title": title,
        "triage_verdict": verdict,
        "severity_recommendation": sev,
        "rationale": "; ".join(reasons) if reasons else "Reproducible exploitability and impact are adequately evidenced.",
        "missing_evidence": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate strict triage for Web3 findings.")
    parser.add_argument("input", help="Input JSON file with finding(s).")
    parser.add_argument("--output", "-o", help="Output JSON file for triage simulation results.")
    args = parser.parse_args()

    findings = load_findings(Path(args.input))
    results = [evaluate(f) for f in findings]

    summary = {
        "accepted": sum(1 for x in results if x["triage_verdict"] == "Accepted"),
        "needs_more_evidence": sum(1 for x in results if x["triage_verdict"] == "Needs More Evidence"),
        "rejected": sum(1 for x in results if x["triage_verdict"] == "Rejected"),
        "total": len(results),
    }

    payload = {"summary": summary, "results": results}
    content = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Triage simulation saved: {args.output}")
    else:
        print(content)


if __name__ == "__main__":
    main()
