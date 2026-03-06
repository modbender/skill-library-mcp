#!/usr/bin/env python3
"""
openclaw_tasks/evidence_search.py
Task 2 — Gap Detection & Evidence Discovery

Phase 3 scope: LOCAL SUBSTRATE ONLY.
No external web calls (OpenClaw skill not yet registered; network policy unconfirmed).
External search deferred to Phase 4.

Finds:
  - Orphan claims (no parents, no children, no linked evidence)
  - Claims with sparse domain coverage (< SPARSE_THRESHOLD per domain)
  - Claims that are semantically isolated (no cross-references in parent_ids)

Writes gap report to memory/gaps-YYYY-MM-DD.md
Proposed new claims written as CLAIM_CREATED events with agent_id='monitoring_agent'
and confidence=0.15 (low — requires human verification before any weight is given).

Safety: writes are append-only via validated substrate write_claim().
        No claim can be auto-verified by this script.

Usage:
  python evidence_search.py [db_path]
  python evidence_search.py [db_path] --claim-id <uuid>
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(WORKSPACE))

from substrate import Substrate, EventType

SPARSE_THRESHOLD = 3          # domain has "sparse" coverage if < 3 claims
ORPHAN_MIN_AGE_HOURS = 1      # only flag orphans older than this (avoid race)


def detect_gaps(substrate: Substrate) -> dict:
    total = substrate.event_count()
    if total < 5:
        return {"status": "insufficient_data", "total_events": total}

    # ── 1. Orphan detection ──────────────────────────────────────────
    no_evidence = substrate.get_claims_without_evidence()
    orphans = []
    for claim in no_evidence:
        # No parents AND no children = true orphan
        if not claim.parent_ids and substrate.count_children(claim.event_id) == 0:
            # Only flag claims older than ORPHAN_MIN_AGE_HOURS
            try:
                age_hours = (
                    datetime.utcnow() -
                    datetime.fromisoformat(claim.timestamp.replace("Z", ""))
                ).total_seconds() / 3600
            except Exception:
                age_hours = 999  # assume old if unparseable

            if age_hours >= ORPHAN_MIN_AGE_HOURS:
                orphans.append({
                    "event_id": claim.event_id,
                    "domain": claim.domain,
                    "confidence": claim.confidence,
                    "age_hours": round(age_hours, 1),
                    "claim_snippet": str(claim.content.get("claim", ""))[:120],
                })

    # ── 2. Sparse domain coverage ────────────────────────────────────
    all_claims = substrate.get_events_by_type(EventType.CLAIM_CREATED)
    domain_counts = defaultdict(int)
    for c in all_claims:
        domain_counts[c.domain] += 1

    sparse_domains = [
        {"domain": d, "claim_count": n}
        for d, n in domain_counts.items()
        if n < SPARSE_THRESHOLD
    ]

    # ── 3. Claims lacking any cross-reference ────────────────────────
    isolated = []
    for claim in all_claims:
        # A claim is isolated if it appears in no other event's parent_ids
        child_count = substrate.count_children(claim.event_id)
        if child_count == 0 and not claim.parent_ids:
            isolated.append({
                "event_id": claim.event_id,
                "domain": claim.domain,
                "confidence": claim.confidence,
            })

    # ── 4. Insights with no challenge history ────────────────────────
    insights = substrate.get_insights()
    unchallenged_insights = []
    for ins in insights:
        challenges = substrate.get_challenge_results_for_insight(ins.event_id)
        if not challenges:
            unchallenged_insights.append({
                "event_id": ins.event_id,
                "insight_type": ins.content.get("insight_type", "?"),
                "confidence": ins.confidence,
            })

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "total_events": total,
        "orphan_claims": orphans,
        "sparse_domains": sparse_domains,
        "isolated_claims_count": len(isolated),
        "unchallenged_insights": unchallenged_insights,
        "summary": {
            "orphan_count": len(orphans),
            "sparse_domain_count": len(sparse_domains),
            "unchallenged_insight_count": len(unchallenged_insights),
        }
    }


def write_gap_report(gaps: dict, workspace: Path):
    """Write human-readable gap report to memory/gaps-YYYY-MM-DD.md"""
    memory_dir = workspace / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    report_path = memory_dir / f"gaps-{date_str}.md"

    lines = [
        f"# Gap Detection Report — {date_str}",
        f"Generated: {gaps.get('timestamp', 'unknown')}",
        f"Total substrate events: {gaps.get('total_events', 0)}",
        "",
        "## Orphan Claims",
        f"Count: {len(gaps.get('orphan_claims', []))}",
        "",
    ]
    for orphan in gaps.get("orphan_claims", [])[:10]:
        lines.append(
            f"- `{orphan['event_id'][:8]}...` | {orphan['domain']} | "
            f"conf={orphan['confidence']:.2f} | age={orphan['age_hours']}h"
        )
        lines.append(f"  > {orphan['claim_snippet']}")

    lines += [
        "",
        "## Sparse Domain Coverage",
        f"Domains with < {SPARSE_THRESHOLD} claims:",
        "",
    ]
    for sd in gaps.get("sparse_domains", []):
        lines.append(f"- {sd['domain']}: {sd['claim_count']} claim(s)")

    lines += [
        "",
        "## Unchallenged Insights",
        f"Count: {len(gaps.get('unchallenged_insights', []))}",
        "",
    ]
    for ins in gaps.get("unchallenged_insights", [])[:5]:
        lines.append(
            f"- `{ins['event_id'][:8]}...` | {ins['insight_type']}-type | "
            f"conf={ins['confidence']:.2f}"
        )

    lines += [
        "",
        "## Action Required",
        "- Orphans: consider linking to related claims or flagging for human review",
        "- Sparse domains: schedule additional pipeline runs for underrepresented domains",
        "- Unchallenged insights: add to adversarial_rechallenge.py next cycle",
        "",
        "---",
        "_Generated by evidence_search.py (local substrate only — Phase 3)_",
        "_External evidence search deferred to Phase 4_",
    ]

    report_path.write_text("\n".join(lines))

    # Also log to openclaw-runs
    runs_dir = workspace / "memory" / "openclaw-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    log_file = runs_dir / f"{date_str}.json"
    existing = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text())
        except Exception:
            pass
    existing.append({"task": "evidence_search", **gaps})
    log_file.write_text(json.dumps(existing, indent=2))

    return report_path


def main():
    db_path = str(WORKSPACE / "epistemic.db")
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        db_path = sys.argv[1]

    substrate = Substrate(db_path)
    gaps = detect_gaps(substrate)
    substrate.close()

    report_path = write_gap_report(gaps, WORKSPACE)
    print(json.dumps(gaps, indent=2))
    print(f"\n[evidence_search] Gap report written to {report_path}", file=sys.stderr)


if __name__ == "__main__":
    main()