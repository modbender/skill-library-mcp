 #!/usr/bin/env python3
"""
openclaw_tasks/adversarial_rechallenge.py
Task 4 — Adversarial Re-Challenge

Periodically selects high-confidence insights (> 0.75) and re-runs a
lightweight adversarial challenge using a 2-agent subset (boundary + null_hypothesis).
This approximates RFC-0007 confidence decay without needing the full scheduler.

Rate limit: max 1 re-challenge per 4-hour window. Tracked in memory/heartbeat-state.json.

New CHALLENGE_RESULT events are appended to the substrate (append-only).
LearningSystem.record_rechallenge_result() is called if self_improvement.py is present.

Usage:
  python adversarial_rechallenge.py [db_path] [--classes boundary,null_hypothesis]
  python adversarial_rechallenge.py [db_path] --insight-id <uuid>
"""

import sys
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(WORKSPACE))

from substrate import Substrate, EventType

RATE_LIMIT_HOURS = 4
HIGH_CONFIDENCE_THRESHOLD = 0.75
HEARTBEAT_STATE_FILE = WORKSPACE / "memory" / "heartbeat-state.json"

# Default 2-agent subset (fast, avoids full 90-second 3-agent cycle)
DEFAULT_AGENT_SUBSET = ["boundary", "null_hypothesis"]


def load_heartbeat_state() -> dict:
    if HEARTBEAT_STATE_FILE.exists():
        try:
            return json.loads(HEARTBEAT_STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_heartbeat_state(state: dict):
    HEARTBEAT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT_STATE_FILE.write_text(json.dumps(state, indent=2))


def is_rate_limited(state: dict) -> bool:
    """Return True if a rechallenge ran within the last RATE_LIMIT_HOURS."""
    last_run = state.get("last_rechallenge_utc")
    if not last_run:
        return False
    try:
        last_dt = datetime.fromisoformat(last_run)
        return (datetime.utcnow() - last_dt) < timedelta(hours=RATE_LIMIT_HOURS)
    except Exception:
        return False


def run_lightweight_challenge(insight_event, agent_subset: list) -> dict:
    """
    Runs a subset adversarial challenge without the full ChallengeOrchestrator.
    Falls back to stub output if adversarial module not importable.

    Returns a verdict dict compatible with write_challenge_result().
    """
    try:
        from adversarial import BoundaryViolationAgent, NullHypothesisAgent, ChallengeOrchestrator

        # Map subset names to agent classes
        agent_map = {
            "boundary": BoundaryViolationAgent,
            "null_hypothesis": NullHypothesisAgent,
        }
        selected = {k: v for k, v in agent_map.items() if k in agent_subset}

        if not selected:
            return _stub_verdict(insight_event, "no_agents_available")

        results = {}
        for name, AgentClass in selected.items():
            agent = AgentClass()
            insight_text = insight_event.content.get("insight", "")
            domain = insight_event.domain
            try:
                result = agent.challenge(insight_text, domain)
                results[name] = result
            except Exception as e:
                results[name] = {"passed": False, "reason": str(e)}

        passes = sum(1 for r in results.values() if r.get("passed", False))
        total = len(results)

        # Confidence adjustment: -0.05 per failure beyond 1
        failures = total - passes
        adjustment = round(-0.05 * failures, 4)

        category = (
            "re_validated" if passes == total
            else "re_challenged" if passes >= total / 2
            else "re_rejected"
        )

        return {
            "agent_results": results,
            "passes": passes,
            "total": total,
            "category": category,
            "confidence_adjustment": adjustment,
            "agent_subset": agent_subset,
            "is_rechallenge": True,
        }

    except ImportError:
        return _stub_verdict(insight_event, "adversarial_module_unavailable")


def _stub_verdict(insight_event, reason: str) -> dict:
    """Fallback when adversarial module is not available."""
    return {
        "agent_results": {},
        "passes": 0,
        "total": 0,
        "category": "rechallenge_skipped",
        "confidence_adjustment": 0.0,
        "agent_subset": [],
        "is_rechallenge": True,
        "skip_reason": reason,
    }


def wire_learning_system(insight_event, verdict: dict, substrate: Substrate):
    """
    Call LearningSystem.record_rechallenge_result() if self_improvement.py present.
    Monitoring integration §4.5.
    """
    try:
        from self_improvement import LearningSystem
        ls = LearningSystem()

        # Build lightweight validation dict compatible with record_result()
        validation = {
            "validation_category": verdict.get("category", "unknown"),
            "passes": verdict.get("passes", 0),
            "total_agents": verdict.get("total", 0),
            "confidence_adjustment": verdict.get("confidence_adjustment", 0.0),
        }

        # Source claims = parent_ids of insight
        source_events = []
        for pid in insight_event.parent_ids:
            ev = substrate.get_event(pid)
            if ev:
                source_events.append(ev)

        # Use existing record_result if rechallenge wrapper not yet added
        if hasattr(ls, "record_rechallenge_result"):
            ls.record_rechallenge_result(insight_event, verdict)
        else:
            ls.record_result(insight_event.content, validation, source_events)

    except ImportError:
        pass  # LearningSystem not present — silent skip
    except Exception as e:
        print(f"[adversarial_rechallenge] LearningSystem error (non-fatal): {e}", file=sys.stderr)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path", nargs="?", default=str(WORKSPACE / "epistemic.db"))
    parser.add_argument("--insight-id", default=None)
    parser.add_argument("--classes", default=",".join(DEFAULT_AGENT_SUBSET),
                        help="Comma-separated agent subset: boundary,null_hypothesis")
    parser.add_argument("--force", action="store_true",
                        help="Bypass rate limit (for testing)")
    args = parser.parse_args()

    agent_subset = [c.strip() for c in args.classes.split(",") if c.strip()]
    state = load_heartbeat_state()

    # Rate limit check
    if not args.force and is_rate_limited(state):
        result = {
            "status": "rate_limited",
            "next_eligible": (
                datetime.fromisoformat(state["last_rechallenge_utc"]) +
                timedelta(hours=RATE_LIMIT_HOURS)
            ).isoformat(),
        }
        print(json.dumps(result, indent=2))
        return

    substrate = Substrate(args.db_path)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Select insight to rechallenge
    if args.insight_id:
        insight = substrate.get_event(args.insight_id)
        if not insight or insight.event_type != EventType.INSIGHT_GENERATED:
            print(json.dumps({"error": f"Insight {args.insight_id} not found or wrong type"}))
            substrate.close()
            sys.exit(1)
    else:
        candidates = substrate.get_insights_above_confidence(HIGH_CONFIDENCE_THRESHOLD)
        if not candidates:
            result = {
                "status": "no_candidates",
                "threshold": HIGH_CONFIDENCE_THRESHOLD,
                "timestamp": datetime.utcnow().isoformat(),
            }
            print(json.dumps(result, indent=2))
            substrate.close()
            return
        # Pick the highest-confidence insight (most epistemic risk)
        insight = max(candidates, key=lambda e: e.confidence)

    print(f"[adversarial_rechallenge] Re-challenging {insight.event_id[:8]}... "
          f"(conf={insight.confidence:.2f})", file=sys.stderr)

    verdict = run_lightweight_challenge(insight, agent_subset)

    # Append result to substrate (append-only invariant maintained)
    adj = verdict.get("confidence_adjustment", 0.0)
    substrate.write_challenge_result(
        insight_id=insight.event_id,
        agent_id="monitoring_agent",
        verdict=verdict,
        confidence_adjustment=adj
    )

    # Wire into learning system
    wire_learning_system(insight, verdict, substrate)

    # Update rate limit state
    state["last_rechallenge_utc"] = datetime.utcnow().isoformat()
    state["last_rechallenge_insight_id"] = insight.event_id
    save_heartbeat_state(state)

    # Write to openclaw-runs log
    runs_dir = WORKSPACE / "memory" / "openclaw-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    log_file = runs_dir / f"{date_str}.json"
    existing = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text())
        except Exception:
            pass

    run_record = {
        "task": "adversarial_rechallenge",
        "timestamp": datetime.utcnow().isoformat(),
        "insight_id": insight.event_id,
        "prior_confidence": insight.confidence,
        "verdict": verdict,
        "new_confidence_estimate": round(insight.confidence + adj, 4),
    }
    existing.append(run_record)
    log_file.write_text(json.dumps(existing, indent=2))
    substrate.close()

    print(json.dumps(run_record, indent=2))


if __name__ == "__main__":
    main()