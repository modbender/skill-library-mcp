#!/usr/bin/env python3
"""
List agent votes for a hypothesis.

Usage:
  python list_votes.py --hypothesis-id 1
  python list_votes.py --hypothesis-id 1 --agent-id "anthropic/claude-opus"
  python list_votes.py --hypothesis-id 1 --direction support
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="List agent votes for a hypothesis"
    )
    parser.add_argument("--hypothesis-id", type=int, required=True, help="Hypothesis ID")
    parser.add_argument("--agent-id", help="Filter by agent ID")
    parser.add_argument("--direction", choices=["support", "oppose", "neutral"], help="Filter by direction")
    parser.add_argument("--format", choices=["json", "summary"], default="json", help="Output format")

    args = parser.parse_args()

    params = {}
    if args.agent_id:
        params["agent_id"] = args.agent_id
    if args.direction:
        params["direction"] = args.direction

    result = api_get(f"/hypotheses/{args.hypothesis_id}/votes", params=params)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        summary = result.get("summary", {})
        print(f"Votes for Hypothesis {args.hypothesis_id}")
        print("=" * 60)
        print(f"  Support: {summary.get('support', 0)} ({summary.get('support_pct', 0)}%)")
        print(f"  Neutral: {summary.get('neutral', 0)} ({summary.get('neutral_pct', 0)}%)")
        print(f"  Oppose:  {summary.get('oppose', 0)} ({summary.get('oppose_pct', 0)}%)")
        print(f"  Total:   {summary.get('total', 0)}")
        print()

        votes = result.get("votes", [])
        if not votes:
            print("No votes found matching filters.")
            return

        for v in votes:
            print(f"[{v['direction'].upper()}] {v['agent_id']}")
            if v.get('confidence'):
                print(f"  Confidence: {v['confidence']}")
            if v.get('reasoning'):
                print(f"  Reasoning: {v['reasoning'][:200]}")
            print(f"  Created: {v['created_at']}")
            print()


if __name__ == "__main__":
    main()
