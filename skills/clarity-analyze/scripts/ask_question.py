#!/usr/bin/env python3
"""
Submit a research question for AI-powered analysis.

Usage:
  python ask_question.py --question "What is the clinical significance of SOD1 A4V?"
  python ask_question.py --question "How does this mutation affect stability?" --variant-id 1
  python ask_question.py --question "..." --focus clinical literature --format text
"""

import argparse
import json
from api_client import api_post


def main():
    parser = argparse.ArgumentParser(
        description="Submit a research question for AI analysis"
    )
    parser.add_argument("--question", required=True, help="Research question (10-2000 chars)")
    parser.add_argument("--variant-id", type=int, help="Fold ID to enrich with specific variant data")
    parser.add_argument("--focus", nargs="+", help="Prioritize data sources (e.g., clinical literature)")
    parser.add_argument("--context", help="Additional context for the question (max 1000 chars)")
    parser.add_argument("--format", choices=["json", "summary", "text"], default="json", help="Output format")

    args = parser.parse_args()

    data = {"question": args.question}
    if args.variant_id:
        data["variant_id"] = args.variant_id
    if args.focus:
        data["focus"] = args.focus
    if args.context:
        data["additional_context"] = args.context

    result = api_post("/analysis", data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    elif args.format == "text":
        print(result["answer"])
    else:
        print("Analysis Result")
        print("=" * 60)
        print(result["answer"])
        print()
        print("-" * 60)
        print(f"Data sources used: {', '.join(result.get('data_sources_used', []))}")
        print(f"Data completeness: {result.get('data_completeness', 'N/A')}")
        if result.get("sources_cited"):
            print(f"Sources cited: {', '.join(result['sources_cited'])}")
        print(f"Cached: {result.get('cached', False)}")


if __name__ == "__main__":
    main()
