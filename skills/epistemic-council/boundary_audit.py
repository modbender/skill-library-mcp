 #!/usr/bin/env python3
"""
openclaw_tasks/boundary_audit.py
Task 5 — Domain Boundary Enforcement Audit

Scans recent claims using the same regex forbidden-term logic as
BoundaryViolationAgent (existing adversarial layer) to detect boundary
leakage at the claim level — not just at the insight level.

Gap §5.5: boundary enforcement currently only occurs in the adversarial
layer after insight generation. This audit extends coverage to individual claims.

Does NOT write to substrate directly.
Violations logged as suggestions in memory/openclaw-runs/YYYY-MM-DD.json.
Human or next pipeline run must decide whether to escalate.

Usage:
  python boundary_audit.py [db_path] [--domain DOMAIN] [--recent N]
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(WORKSPACE))

from substrate import Substrate, EventType

# Default: audit last N claims per domain
DEFAULT_RECENT_N = 20

# Domain forbidden terms — mirrors BoundaryViolationAgent logic from adversarial.py.
# These are terms that should NOT appear in claims for the given domain.
# Extend this dict as more domain agents are added.
DOMAIN_FORBIDDEN_TERMS: dict = {
    "computer_science": [
        r"\bprotein fold",
        r"\bcell\b",
        r"\bneuron\b(?!.*network)",  # 'neuron' unless followed by 'network'
        r"\bDNA\b",
        r"\bgenome\b",
        r"\bspecies\b",
        r"\bmarket price\b",
        r"\bfiscal policy\b",
    ],
    "biology": [
        r"\bsort algorithm\b",
        r"\btime complexity\b",
        r"\bO\(n",
        r"\bhash table\b",
        r"\bcompiler\b",
        r"\bstock price\b",
        r"\bGDP\b",
        r"\binflation rate\b",
    ],
    "economics": [
        r"\bprotein\b",
        r"\bRNA\b",
        r"\bgraph traversal\b",
        r"\bbinary tree\b",
    ],
    # Add more domains here as agents are instantiated
}


def check_claim_boundary(claim_text: str, domain: str) -> list:
    """
    Returns list of boundary violations found in claim_text for the given domain.
    Each violation is a dict with pattern and match.
    """
    forbidden = DOMAIN_FORBIDDEN_TERMS.get(domain, [])
    violations = []
    for pattern in forbidden:
        match = re.search(pattern, claim_text, re.IGNORECASE)
        if match:
            violations.append({
                "pattern": pattern,
                "matched_text": match.group(0),
                "position": match.start(),
            })
    return violations


def run_boundary_audit(db_path: str, domain: str = None, recent_n: int = DEFAULT_RECENT_N) -> dict:
    substrate = Substrate(db_path)
    total = substrate.event_count()

    if total < 1:
        substrate.close()
        return {"status": "no_data", "timestamp": datetime.utcnow().isoformat()}

    # Get recent claims
    all_claims = substrate.get_events_by_type(EventType.CLAIM_CREATED, domain=domain)
    # Most recent N
    recent_claims = sorted(all_claims, key=lambda e: e.timestamp, reverse=True)[:recent_n]

    violations_found = []
    clean_count = 0

    for claim in recent_claims:
        claim_text = claim.content.get("claim", "")
        violations = check_claim_boundary(claim_text, claim.domain)

        if violations:
            violations_found.append({
                "claim_id": claim.event_id,
                "domain": claim.domain,
                "confidence": claim.confidence,
                "timestamp": claim.timestamp,
                "violations": violations,
                "claim_snippet": claim_text[:150],
                "suggested_action": "flag:boundary_violation",
            })
        else:
            clean_count += 1

    # Also check insights for missing cross_domain_flag
    insights = substrate.get_insights()
    missing_flag_insights = []
    for ins in insights:
        content = ins.content
        if "cross_domain_flag" not in content:
            missing_flag_insights.append({
                "insight_id": ins.event_id,
                "domain": ins.domain,
                "confidence": ins.confidence,
                "note": "cross_domain_flag field missing from content (Gap §4.2)",
            })

    substrate.close()

    result = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "claims_audited": len(recent_claims),
        "clean_claims": clean_count,
        "boundary_violations": violations_found,
        "violation_count": len(violations_found),
        "insights_missing_cross_domain_flag": missing_flag_insights[:10],
        "alert": "REVIEW_NEEDED" if violations_found else "OK",
    }

    return result


def write_audit_log(result: dict, workspace: Path):
    runs_dir = workspace / "memory" / "openclaw-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = runs_dir / f"{date_str}.json"
    existing = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text())
        except Exception:
            pass
    existing.append({"task": "boundary_audit", **result})
    log_file.write_text(json.dumps(existing, indent=2))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path", nargs="?", default=str(WORKSPACE / "epistemic.db"))
    parser.add_argument("--domain", default=None)
    parser.add_argument("--recent", type=int, default=DEFAULT_RECENT_N)
    args = parser.parse_args()

    result = run_boundary_audit(args.db_path, args.domain, args.recent)
    write_audit_log(result, WORKSPACE)
    print(json.dumps(result, indent=2))

    if result.get("alert") == "REVIEW_NEEDED":
        print(f"\n[boundary_audit] {result['violation_count']} violation(s) found. "
              "Logged to memory/openclaw-runs/. Review before next pipeline run.", file=sys.stderr)


if __name__ == "__main__":
    main()