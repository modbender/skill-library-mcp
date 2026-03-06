#!/usr/bin/env python3
"""
scoring_engine.py
Score findings for triage readiness using exploitability, evidence, and economic viability.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SEVERITY_VALUE = {"critical": 1.0, "high": 0.85, "medium": 0.65, "low": 0.35}
CONFIDENCE_VALUE = {"confirmed": 1.0, "probable": 0.75, "theoretical": 0.45}


def clamp(v: float) -> float:
    return max(0.0, min(1.0, v))


def severity_weight(severity: str) -> float:
    return SEVERITY_VALUE.get((severity or "").lower(), 0.45)


def confidence_weight(confidence: str) -> float:
    return CONFIDENCE_VALUE.get((confidence or "").lower(), 0.5)


def field_score(finding: dict[str, Any], key: str, default: float) -> float:
    val = finding.get(key, default)
    if isinstance(val, (int, float)):
        return clamp(float(val))
    if isinstance(val, str):
        low = val.lower().strip()
        if low in {"high", "strong", "yes", "true"}:
            return 0.9
        if low in {"medium", "partial"}:
            return 0.6
        if low in {"low", "weak", "no", "false"}:
            return 0.25
    return clamp(default)


def score_finding(finding: dict[str, Any]) -> dict[str, Any]:
    sev = severity_weight(str(finding.get("severity", "")))
    conf = confidence_weight(str(finding.get("confidence", "")))
    exploit = field_score(finding, "exploitability_score", conf)
    economic = field_score(finding, "economic_score", 0.6)
    evidence = field_score(finding, "evidence_score", conf)
    impact = field_score(finding, "impact_score", sev)

    # Weights tuned for precision-first triage.
    score = (
        exploit * 0.30
        + evidence * 0.25
        + economic * 0.20
        + impact * 0.15
        + conf * 0.10
    ) * 100.0

    score = round(score, 2)
    verdict = "needs-more-evidence"
    if score >= 80 and sev >= 0.65 and exploit >= 0.7 and evidence >= 0.7:
        verdict = "triage-ready"
    elif score < 55:
        verdict = "reject"

    out = dict(finding)
    out["lance_score"] = score
    out["lance_verdict"] = verdict
    out["score_breakdown"] = {
        "exploitability": round(exploit, 3),
        "evidence": round(evidence, 3),
        "economic": round(economic, 3),
        "impact": round(impact, 3),
        "confidence": round(conf, 3),
    }
    return out


def load_findings(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "findings" in raw and isinstance(raw["findings"], list):
        return [x for x in raw["findings"] if isinstance(x, dict)]
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        return [raw]
    raise ValueError("Unsupported findings payload format.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score Web3 findings for triage readiness.")
    parser.add_argument("input", help="Input JSON file containing finding(s).")
    parser.add_argument("--output", "-o", help="Output file for scored findings.")
    args = parser.parse_args()

    findings = load_findings(Path(args.input))
    scored = [score_finding(f) for f in findings]

    summary = {
        "total": len(scored),
        "triage_ready": sum(1 for f in scored if f["lance_verdict"] == "triage-ready"),
        "needs_more_evidence": sum(1 for f in scored if f["lance_verdict"] == "needs-more-evidence"),
        "rejected": sum(1 for f in scored if f["lance_verdict"] == "reject"),
    }

    payload = {"summary": summary, "findings": scored}
    content = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Scored findings saved: {args.output}")
    else:
        print(content)


if __name__ == "__main__":
    main()
