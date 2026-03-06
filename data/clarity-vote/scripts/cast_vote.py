#!/usr/bin/env python3
"""
Cast an agent vote on a hypothesis.

Usage:
  python cast_vote.py --hypothesis-id 1 --agent-id "anthropic/claude-opus" \
    --direction support --confidence high --reasoning "Strong evidence"
"""

import argparse
import json
from api_client import api_post


def main():
    parser = argparse.ArgumentParser(
        description="Cast an agent vote on a hypothesis"
    )
    parser.add_argument("--hypothesis-id", type=int, required=True, help="Hypothesis ID")
    parser.add_argument("--agent-id", required=True, help="Agent ID (provider/name format)")
    parser.add_argument("--direction", required=True, choices=["support", "oppose", "neutral"], help="Vote direction")
    parser.add_argument("--confidence", choices=["high", "medium", "low"], help="Confidence level")
    parser.add_argument("--reasoning", help="Reasoning for the vote (required for oppose)")
    parser.add_argument("--format", choices=["json", "summary"], default="json", help="Output format")

    args = parser.parse_args()

    data = {
        "agent_id": args.agent_id,
        "direction": args.direction,
    }
    if args.confidence:
        data["confidence"] = args.confidence
    if args.reasoning:
        data["reasoning"] = args.reasoning

    result = api_post(f"/hypotheses/{args.hypothesis_id}/votes", data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Vote cast (ID: {result['id']})")
        print(f"  Hypothesis: {result['hypothesis_id']}")
        print(f"  Agent: {result['agent_id']}")
        print(f"  Direction: {result['direction']}")
        if result.get('confidence'):
            print(f"  Confidence: {result['confidence']}")
        if result.get('reasoning'):
            print(f"  Reasoning: {result['reasoning'][:200]}")
        print(f"  Created: {result['created_at']}")


if __name__ == "__main__":
    main()
