"""
metrics.py — Epistemic Council v2.0
Pipeline metrics reporting.

FIX (Gap Analysis §3.4):
  Changed all event_type string comparisons to use EventType enum values.
  Previously: e.event_type == 'insight_generated'  → silently matched nothing
  Fixed:      e.event_type == EventType.INSIGHT_GENERATED
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from substrate import Substrate, EventType, SubstrateEvent


@dataclass
class PipelineMetrics:
    total_events: int = 0
    claims_created: int = 0
    insights_generated: int = 0
    challenge_results: int = 0
    adversarial_challenges: int = 0
    evidence_linked: int = 0
    human_reviews: int = 0
    hypothesis_forks: int = 0
    integrity_check: Dict[str, Any] = field(default_factory=dict)
    domain_breakdown: Dict[str, int] = field(default_factory=dict)
    insight_type_breakdown: Dict[str, int] = field(default_factory=dict)
    avg_confidence: float = 0.0
    high_confidence_insights: int = 0  # > 0.75
    low_confidence_claims: int = 0    # < 0.45
    challenged_zone_claims: int = 0   # 0.45–0.55


def compute_metrics(substrate: Substrate) -> PipelineMetrics:
    """
    Compute full pipeline metrics from substrate.
    All comparisons use EventType enum (Gap §3.4 fix).
    """
    events = substrate.get_all_events()
    m = PipelineMetrics()
    m.total_events = len(events)

    confidence_sum = 0.0
    confidence_count = 0

    for e in events:
        # --- FIX: use EventType enum, not strings ---
        if e.event_type == EventType.CLAIM_CREATED:
            m.claims_created += 1
            m.domain_breakdown[e.domain] = m.domain_breakdown.get(e.domain, 0) + 1
            confidence_sum += e.confidence
            confidence_count += 1
            if e.confidence < 0.45:
                m.low_confidence_claims += 1
            if 0.45 <= e.confidence <= 0.55:
                m.challenged_zone_claims += 1

        elif e.event_type == EventType.INSIGHT_GENERATED:
            m.insights_generated += 1
            insight_type = e.content.get("insight_type", "unknown")
            m.insight_type_breakdown[insight_type] = (
                m.insight_type_breakdown.get(insight_type, 0) + 1
            )
            confidence_sum += e.confidence
            confidence_count += 1
            if e.confidence > 0.75:
                m.high_confidence_insights += 1

        elif e.event_type == EventType.CHALLENGE_RESULT:
            m.challenge_results += 1

        elif e.event_type == EventType.ADVERSARIAL_CHALLENGE:
            m.adversarial_challenges += 1

        elif e.event_type == EventType.EVIDENCE_LINKED:
            m.evidence_linked += 1

        elif e.event_type == EventType.HUMAN_REVIEW:
            m.human_reviews += 1

        elif e.event_type == EventType.HYPOTHESIS_FORKED:
            m.hypothesis_forks += 1

    m.avg_confidence = (
        round(confidence_sum / confidence_count, 4) if confidence_count > 0 else 0.0
    )
    m.integrity_check = substrate.verify_all()
    return m


def print_metrics(m: PipelineMetrics):
    print("\n" + "=" * 55)
    print("  EPISTEMIC COUNCIL — PIPELINE METRICS")
    print("=" * 55)
    print(f"  Total events         : {m.total_events}")
    print(f"  Claims created       : {m.claims_created}")
    print(f"  Insights generated   : {m.insights_generated}")
    print(f"  Challenge results    : {m.challenge_results}")
    print(f"  Evidence linked      : {m.evidence_linked}")
    print(f"  Human reviews        : {m.human_reviews}")
    print(f"  Hypothesis forks     : {m.hypothesis_forks}")
    print(f"  Avg confidence       : {m.avg_confidence}")
    print(f"  High-confidence (>0.75): {m.high_confidence_insights}")
    print(f"  Challenged zone claims : {m.challenged_zone_claims}")
    print(f"  Low-confidence (<0.45) : {m.low_confidence_claims}")
    print()
    print("  Domain breakdown:")
    for domain, count in m.domain_breakdown.items():
        print(f"    {domain}: {count}")
    print()
    print("  Insight type breakdown:")
    for itype, count in m.insight_type_breakdown.items():
        print(f"    {itype}-type: {count}")
    print()
    integrity = m.integrity_check
    print(f"  Integrity: {integrity.get('passed', 0)}/{integrity.get('total', 0)} passed")
    if integrity.get("failed"):
        print(f"  FAILED event IDs: {integrity['failed']}")
    print("=" * 55 + "\n")