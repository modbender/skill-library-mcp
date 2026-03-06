#!/usr/bin/env python3
"""
🐾 Query OEE's Second Brain.

Usage:
    python query.py "What did I save about transformers?"
    python query.py --search "RAG systems"  # just retrieve, no LLM
"""

import argparse
import sys
from kb import ask, retrieve


def main():
    parser = argparse.ArgumentParser(description="🐾 Query OEE's Second Brain")
    parser.add_argument("query", help="Question or search query")
    parser.add_argument("--search", action="store_true", help="Search only (no LLM answer)")
    parser.add_argument("--top", type=int, default=10, help="Number of results")
    args = parser.parse_args()

    if args.search:
        results = retrieve(args.query, top_k=args.top)
        if not results:
            print("No results found.")
            return
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r['title']} (sim={r['similarity']:.3f})")
            print(f"    {r['url']}")
            print(f"    {r['content'][:200]}...")
    else:
        answer = ask(args.query, top_k=args.top)
        print(answer)


if __name__ == "__main__":
    main()
