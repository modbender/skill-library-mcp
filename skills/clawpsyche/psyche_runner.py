#!/usr/bin/env python3
"""
Psyche Runner — OpenClaw CLI wrapper for psyche_engine.
Loads state from JSON, runs one step, saves state, prints snapshot.
"""

import argparse
import json
import os
import sys

# Import engine from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psyche_engine import create_agent, step, snapshot, request, dream_report_prompt


def main():
    p = argparse.ArgumentParser(description="Psyche Engine — one step")
    p.add_argument("--state", required=True, help="Path to psyche_state.json")
    p.add_argument("--tags", default="", help="Comma-separated event tags")
    p.add_argument("--valence", type=float, default=0.0, help="-1.0 to 1.0")
    p.add_argument("--arousal", type=float, default=0.5, help="0.0 to 1.0")
    p.add_argument("--user", default=None, help="User ID")
    p.add_argument("--request-weight", type=float, default=0.0,
                    help="If >0, also run decision gate")
    p.add_argument("--init", action="store_true", help="Create fresh state")
    args = p.parse_args()

    # Load or create state
    if args.init or not os.path.exists(args.state):
        state = create_agent()
    else:
        with open(args.state, "r", encoding="utf-8") as f:
            state = json.load(f)

    # Parse tags
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    # Run step
    result = step(state, tags, args.valence, args.arousal, args.user)

    # Decision gate
    if args.request_weight > 0 and args.user:
        decision = request(state, tags, args.user, args.request_weight)
        result["decision"] = decision

    # Save state
    os.makedirs(os.path.dirname(os.path.abspath(args.state)), exist_ok=True)
    with open(args.state, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=None)

    # Output - compact
    print(result["snapshot"])

    if result.get("dream"):
        dp = dream_report_prompt(result["dream"])
        if dp:
            print(f"DREAM: {dp}")

    if result.get("decision"):
        print(f"DECISION: {result['decision']}")


if __name__ == "__main__":
    main()
