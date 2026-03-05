#!/usr/bin/env python3
"""Generate a research plan from a topic query. Outputs structured search queries."""

import sys
import json

def generate_plan(topic: str) -> dict:
    """Break a research topic into search angles."""
    plan = {
        "topic": topic,
        "queries": [
            f"{topic}",
            f"{topic} latest news 2026",
            f"{topic} reviews comparison",
            f"{topic} pricing cost",
            f"{topic} alternatives competitors",
        ],
        "max_searches": 10,
        "max_fetches": 5,
        "strategy": "broad_then_deep"
    }
    return plan

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: research_plan.py <topic>", file=sys.stderr)
        sys.exit(1)
    topic = " ".join(sys.argv[1:])
    print(json.dumps(generate_plan(topic), indent=2))
