#!/usr/bin/env python3
"""
openclaw_tasks/substrate_health.py
Task 1 — Substrate Health Monitoring

Runs every heartbeat cycle (Cycle 1).
Scans for:
  - Unverified high-risk claims (risk proxy: (1 - confidence) × 1.2 for cross-domain)
  - Claims with no evidence linked (weak evidence)
  - Orphan claims (no parents, no children)
  - Divergence clusters (>= N competing forks from same parent)

Writes results to memory/openclaw-runs/YYYY-MM-DD.json
Prints JSON to stdout for heartbeat capture.

Safety: read-only. No substrate writes.
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

# Resolve workspace root (this file lives in openclaw_tasks/)
WORKSPACE = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(WORKSPACE))

from substrate import Substrate, EventType

# Thresholds (aligned with RFC-0006 and monitoring proposal)
RISK_THRESHOLD = 0.7           # computed: (1 - confidence) × 1.2 ≥ 0.7
HIGH_CONFIDENCE_THRESHOLD = 0.75
DIVERGENCE_CLUSTER_MIN = 3     # ≥ 3 forks from same parent = cluster
MIN_EVENTS_FOR_HEALTH_CHECK = 10


def compute_risk_proxy(confidence: float, cross_domain: bool = False) -> float:
    """
    Proxy for risk_score (field not yet in schema).
    cross-domain claims get a 1.3× multiplier to reflect higher epistemic risk.
    """
    base = (1.0 - confidence) * 1.2
    if cross_domain:
        base *= 1.3
    return round(min(base, 1.0), 4)


def check_substrate_health(db_path: str) -> dict:
    substrate = Substrate(db_path)
    total = substrate.event_count()

    if total < MIN_EVENTS_FOR_HEALTH_CHECK:
        return {
            "alert": "SKIP",
            "reason": f"Insufficient data: {total} events (min {MIN_EVENTS_FOR_HEALTH_CHECK})",
            "total_events": total,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ── 1. High-risk unverified claims ──────────────────────────────
    all_claims = substrate.get_events_by_type(EventType.CLAIM_CREATED)
    high_risk_unverified = []
    for claim in all_claims:
        cross = claim.content.get("cross_domain_flag", False)
        risk = compute_risk_proxy(claim.confidence, cross)
        if risk >= RISK_THRESHOLD:
            reviews = substrate.get_human_review_decisions(claim.event_id)
            approved = any(
                r.content.get("decision") == "approved" for r in reviews
            )
            if not approved:
                high_risk_unverified.append({
                    "event_id": claim.event_id,
                    "domain": claim.domain,
                    "confidence": claim.confidence,
                    "risk_proxy": risk,
                    "timestamp": claim.timestamp,
                })

    # ── 2. Weak evidence claims ──────────────────────────────────────
    weak_evidence = []
    for claim in all_claims:
        children_count = substrate.count_children(claim.event_id)
        # count_children includes all child events; we want evidence-specific
        # Use get_claims_without_evidence for domain-agnostic check
        if children_count == 0:
            weak_evidence.append({
                "event_id": claim.event_id,
                "domain": claim.domain,
                "confidence": claim.confidence,
            })

    # ── 3. Orphan claims (no parents AND no children) ────────────────
    orphans = []
    no_evidence_claims = substrate.get_claims_without_evidence()
    for claim in no_evidence_claims:
        if not claim.parent_ids and substrate.count_children(claim.event_id) == 0:
            orphans.append({
                "event_id": claim.event_id,
                "domain": claim.domain,
                "confidence": claim.confidence,
            })

    # ── 4. Divergence clusters ────────────────────────────────────────
    divergence_clusters = []
    fork_events = substrate.get_events_by_type(EventType.HYPOTHESIS_FORKED)
    # Group by parent
    forks_by_parent: dict = {}
    for fe in fork_events:
        for pid in fe.parent_ids:
            forks_by_parent.setdefault(pid, []).append(fe.event_id)
    for parent_id, fork_ids in forks_by_parent.items():
        if len(fork_ids) >= DIVERGENCE_CLUSTER_MIN:
            divergence_clusters.append({
                "parent_id": parent_id,
                "fork_count": len(fork_ids),
            })

    # ── 5. High-confidence insights flagged for re-challenge ─────────
    high_conf_insights = substrate.get_insights_above_confidence(HIGH_CONFIDENCE_THRESHOLD)

    # ── Alert level ───────────────────────────────────────────────────
    critical = len(high_risk_unverified) > 10 or len(divergence_clusters) > 5
    alert = "CRITICAL" if critical else "OK"

    report = {
        "alert": alert,
        "timestamp": datetime.utcnow().isoformat(),
        "total_events": total,
        "high_risk_unverified": {
            "count": len(high_risk_unverified),
            "items": high_risk_unverified[:5],  # top 5 for brevity
        },
        "weak_evidence": {
            "count": len(weak_evidence),
        },
        "orphan_claims": {
            "count": len(orphans),
            "items": orphans[:5],
        },
        "divergence_clusters": {
            "count": len(divergence_clusters),
            "items": divergence_clusters,
        },
        "high_confidence_insights_pending_rechallenge": {
            "count": len(high_conf_insights),
            "ids": [i.event_id for i in high_conf_insights[:3]],
        },
    }

    substrate.close()
    return report


def write_run_log(report: dict, workspace: Path):
    """Append report to daily openclaw-runs log."""
    runs_dir = workspace / "memory" / "openclaw-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    log_file = runs_dir / f"{datetime.utcnow().strftime('%Y-%m-%d')}.json"

    existing = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text())
        except Exception:
            existing = []

    existing.append({"task": "substrate_health", **report})
    log_file.write_text(json.dumps(existing, indent=2))

    # Also update latest snapshot
    snapshot = workspace / "memory" / "substrate-health.json"
    snapshot.write_text(json.dumps(report, indent=2))


def main():
    db_path = str(WORKSPACE / "epistemic.db")
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    report = check_substrate_health(db_path)
    write_run_log(report, WORKSPACE)
    print(json.dumps(report, indent=2))

    # Exit 2 on CRITICAL so heartbeat can detect it
    if report.get("alert") == "CRITICAL":
        sys.exit(2)


if __name__ == "__main__":
    main()