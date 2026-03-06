#!/usr/bin/env python3
"""
openclaw_tasks/validate_claim.py
Task 3 — Claim Validation & Strengthening

Targets claims in the 'challenged zone' (confidence 0.45–0.55).
These are claims that passed initial generation but sit below the epistemic
confidence needed for reinforcement. Re-validating them is highest ROI.

For each candidate claim:
  1. Retrieves its full content and reasoning_trace from substrate
  2. Calls local Ollama to re-evaluate whether the claim still holds
  3. Checks if prior adversarial challenges exist (prior challenge history)
  4. Suggests confidence adjustment (up/down/unchanged)
  5. Logs result to memory/openclaw-runs/ for human review

Does NOT modify the substrate. Suggestions are logged only.
Human or next pipeline run must act on suggestions.

Usage:
  python validate_claim.py [db_path] [--domain DOMAIN] [--low 0.45] [--high 0.55]
"""

import sys
import json
import re
import os
import http.client
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(WORKSPACE))

from substrate import Substrate, EventType

# Defaults
DEFAULT_LOW = 0.45
DEFAULT_HIGH = 0.55
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
OLLAMA_MODEL = "glm-4.7-flash"  # from monitoring spec
MAX_CLAIMS_PER_RUN = 5          # prevent token burn (monitoring proposal §8)


VALIDATION_PROMPT = """You are an epistemic validation agent. A claim was previously generated with moderate confidence and must be re-evaluated.

CLAIM: {claim}

DOMAIN: {domain}

REASONING TRACE (original): {reasoning_trace}

PRIOR ADVERSARIAL CHALLENGES: {challenges}

Your task:
1. Evaluate whether this claim is still epistemically justified given the reasoning trace.
2. Identify any weaknesses or gaps in the reasoning.
3. Recommend a confidence adjustment: INCREASE, DECREASE, or UNCHANGED.
4. If DECREASE or INCREASE, estimate the magnitude (e.g. -0.10, +0.08).

Respond in this exact format:
VERDICT: [PASS|FAIL|UNCERTAIN]
ADJUSTMENT: [INCREASE|DECREASE|UNCHANGED]
MAGNITUDE: [float between -0.5 and +0.5, or 0.0 if UNCHANGED]
REASONING: [one to three sentences explaining your evaluation]
"""


def call_ollama(prompt: str) -> str:
    """Call local Ollama HTTP API. Returns raw text response."""
    try:
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }).encode()
        conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=30)
        conn.request("POST", "/api/generate", payload, {"Content-Type": "application/json"})
        resp = conn.getresponse()
        if resp.status != 200:
            return f"Ollama error: HTTP {resp.status}"
        data = json.loads(resp.read())
        return data.get("response", "").strip()
    except Exception as e:
        return f"Ollama unavailable: {e}"


def parse_validation_response(text: str) -> dict:
    """Extract structured fields from Ollama validation response."""
    result = {
        "verdict": "UNCERTAIN",
        "adjustment": "UNCHANGED",
        "magnitude": 0.0,
        "reasoning": "",
    }
    lines = text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("VERDICT:"):
            result["verdict"] = line.split(":", 1)[1].strip().upper()
        elif line.startswith("ADJUSTMENT:"):
            result["adjustment"] = line.split(":", 1)[1].strip().upper()
        elif line.startswith("MAGNITUDE:"):
            try:
                result["magnitude"] = float(line.split(":", 1)[1].strip())
            except ValueError:
                result["magnitude"] = 0.0
        elif line.startswith("REASONING:"):
            result["reasoning"] = line.split(":", 1)[1].strip()
    return result


def validate_claim(claim_event, substrate: Substrate) -> dict:
    """Run validation on a single claim event. Returns result dict."""
    content = claim_event.content
    claim_text = content.get("claim", "")
    reasoning_trace = content.get("reasoning_trace", "No reasoning trace stored.")

    # Get prior challenge history for this claim
    challenges = substrate.get_challenge_results_for_insight(claim_event.event_id)
    challenge_summary = "None" if not challenges else (
        f"{len(challenges)} prior challenge(s). "
        "Last verdict: " + str(challenges[-1].content.get("verdict", {}).get("category", "unknown"))
    )

    prompt = VALIDATION_PROMPT.format(
        claim=claim_text[:500],
        domain=claim_event.domain,
        reasoning_trace=reasoning_trace[:400],
        challenges=challenge_summary,
    )

    raw_response = call_ollama(prompt)
    parsed = parse_validation_response(raw_response)

    return {
        "claim_id": claim_event.event_id,
        "domain": claim_event.domain,
        "current_confidence": claim_event.confidence,
        "claim_snippet": claim_text[:150],
        "verdict": parsed["verdict"],
        "suggested_adjustment": parsed["adjustment"],
        "suggested_magnitude": parsed["magnitude"],
        "suggested_new_confidence": round(
            claim_event.confidence + parsed["magnitude"], 4
        ),
        "reasoning": parsed["reasoning"],
        "prior_challenges": len(challenges),
        "validated_at": datetime.utcnow().isoformat(),
        "status": "needs_human_review" if parsed["verdict"] == "FAIL" else "suggestion",
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path", nargs="?", default=str(WORKSPACE / "epistemic.db"))
    parser.add_argument("--domain", default=None)
    parser.add_argument("--low", type=float, default=DEFAULT_LOW)
    parser.add_argument("--high", type=float, default=DEFAULT_HIGH)
    parser.add_argument("--claim-id", default=None,
                        help="Validate a specific claim by ID instead of range scan")
    args = parser.parse_args()

    substrate = Substrate(args.db_path)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    if args.claim_id:
        claim_event = substrate.get_event(args.claim_id)
        if not claim_event:
            print(json.dumps({"error": f"Claim {args.claim_id} not found"}))
            sys.exit(1)
        candidates = [claim_event]
    else:
        candidates = substrate.get_claims_in_confidence_range(
            args.low, args.high, domain=args.domain
        )

    candidates = candidates[:MAX_CLAIMS_PER_RUN]

    if not candidates:
        result = {
            "status": "no_candidates",
            "range": [args.low, args.high],
            "domain": args.domain,
            "timestamp": datetime.utcnow().isoformat(),
        }
        print(json.dumps(result, indent=2))
        substrate.close()
        return

    results = []
    for claim in candidates:
        print(f"[validate_claim] Evaluating {claim.event_id[:8]}... (conf={claim.confidence:.2f})",
              file=sys.stderr)
        result = validate_claim(claim, substrate)
        results.append(result)

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
    existing.append({
        "task": "validate_claim",
        "timestamp": datetime.utcnow().isoformat(),
        "results": results,
    })
    log_file.write_text(json.dumps(existing, indent=2))

    substrate.close()

    output = {
        "status": "ok",
        "validated_count": len(results),
        "range": [args.low, args.high],
        "results": results,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()