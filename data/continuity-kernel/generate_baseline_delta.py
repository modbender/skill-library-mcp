from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark import BaselineReport, ContinuityBenchmarkHarness, ContinuityRun


def main() -> None:
    harness = ContinuityBenchmarkHarness()

    previous = harness.evaluate(
        [
            ContinuityRun(True, False, False, False),
            ContinuityRun(True, False, True, False),
            ContinuityRun(False, True, True, True),
            ContinuityRun(True, False, False, False),
            ContinuityRun(True, False, False, False),
        ]
    )
    current = harness.evaluate(
        [
            ContinuityRun(True, False, False, False),
            ContinuityRun(True, False, False, False),
            ContinuityRun(True, False, True, False),
            ContinuityRun(True, False, False, False),
            ContinuityRun(False, True, True, False),
        ]
    )

    # Determinism proof: same KPI payload, different timestamps must hash equally.
    proof_a = BaselineReport(
        schema_version="v1",
        generated_at="2026-02-21T00:00:00+00:00",
        total_runs=5,
        resume_success_rate=80.0,
        reprompt_rate=20.0,
        off_goal_tool_call_rate=40.0,
        duplicate_work_rate=0.0,
    )
    proof_b = BaselineReport(
        schema_version="v1",
        generated_at="2026-02-21T23:59:59+00:00",
        total_runs=5,
        resume_success_rate=80.0,
        reprompt_rate=20.0,
        off_goal_tool_call_rate=40.0,
        duplicate_work_rate=0.0,
    )

    payload = {
        "schema_version": "v1",
        "note": "xhigh-only rebuild",
        "previous_report": harness.deterministic_payload(previous),
        "current_report": harness.deterministic_payload(current),
        "trend": harness.compare_trends_stub(previous, current),
        "deterministic_hashes": {
            "previous": harness.deterministic_hash(previous),
            "current": harness.deterministic_hash(current),
        },
        "deterministic_proof": {
            "hash_a": harness.deterministic_hash(proof_a),
            "hash_b": harness.deterministic_hash(proof_b),
            "timestamp_invariant": harness.deterministic_hash(proof_a)
            == harness.deterministic_hash(proof_b),
        },
    }

    out = Path.home() / ".cache" / "continuity-kernel" / "baseline" / "continuity_baseline_delta_v1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(out.as_posix())


if __name__ == "__main__":
    main()
