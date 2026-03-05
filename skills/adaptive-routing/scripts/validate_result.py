#!/usr/bin/env python3
"""Validate a local LLM response and decide whether to escalate to cloud.

Ports the heuristic scoring logic from adaptive-routing.ts (PR #30185) to Python,
giving the skill a post-outcome quality gate instead of only a pre-flight router.

Usage:
  python3 validate_result.py --response "..." [--exit-code N] [--timed-out]
    [--tool-error TOOLNAME] [--min-score FLOAT]

Output (JSON):
  { "passed": bool, "score": float, "reason": str,
    "should_escalate": bool, "validation_mode": "heuristic" }

Scoring (mirrors adaptive-routing.ts validateHeuristic):
  Base score: 1.0
  Provider/process error (exit-code != 0)  → -1.0
  Request timed out                        → -0.3
  Tool execution error                     → -0.6
  Empty response                           → -0.4
  Score < min-score (default 0.75)         → fail

should_escalate: true when passed=false — caller should re-run with cloud model.
"""
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--response", default="", help="Response text from the local model")
parser.add_argument("--exit-code", type=int, default=0, dest="exit_code",
                    help="Exit/status code of the LLM call (0 = ok)")
parser.add_argument("--timed-out", action="store_true", dest="timed_out",
                    help="Request timed out before completion")
parser.add_argument("--tool-error", default="", dest="tool_error",
                    help="Name of the tool that errored, if any")
parser.add_argument("--min-score", type=float, default=0.75, dest="min_score",
                    help="Minimum score to pass (default 0.75, matches PR default)")
args = parser.parse_args()

score = 1.0
fail_reasons: list[str] = []

# 1. Provider / process error
if args.exit_code != 0:
    score -= 1.0
    fail_reasons.append("provider_error")

# 2. Timeout — treat as truncation, not hard failure
if args.timed_out:
    score -= 0.3
    fail_reasons.append("timed_out")

# 3. Tool execution error
if args.tool_error.strip():
    score -= 0.6
    fail_reasons.append(f"tool_error:{args.tool_error.strip()}")

# 4. Empty assistant output
if not args.response.strip():
    score -= 0.4
    fail_reasons.append("empty_assistant_output")

score = max(0.0, min(1.0, score))
passed = score >= args.min_score and len(fail_reasons) == 0

print(json.dumps({
    "passed": passed,
    "score": round(score, 2),
    "reason": "ok" if passed else ", ".join(fail_reasons),
    "should_escalate": not passed,
    "validation_mode": "heuristic",
    "min_score": args.min_score,
}))
