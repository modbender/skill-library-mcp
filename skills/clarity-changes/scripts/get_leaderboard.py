#!/usr/bin/env python3
"""
View the agent contribution leaderboard.

Usage:
  python get_leaderboard.py
  python get_leaderboard.py --format summary
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="View the agent contribution leaderboard"
    )
    parser.add_argument("--format", choices=["json", "summary"], default="json", help="Output format")

    args = parser.parse_args()

    result = api_get("/agents/leaderboard")

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        agents = result.get("agents", [])
        total = result.get("total_agents", 0)
        print(f"Agent Leaderboard ({total} agents)")
        print("=" * 60)

        if not agents:
            print("No agent contributions yet.")
            return

        for i, agent in enumerate(agents, 1):
            print(f"\n  #{i} {agent['agent_id']}")
            print(f"     Total: {agent['total_contributions']} contributions")
            print(f"     Annotations: {agent['annotation_count']}")
            print(f"     Votes: {agent['vote_count']}")
            if agent.get("annotation_types"):
                types = ", ".join(f"{k}: {v}" for k, v in agent["annotation_types"].items())
                print(f"     Types: {types}")


if __name__ == "__main__":
    main()
