#!/usr/bin/env python3
"""DuckDuckGo web search. Usage: search.py "query" [count]"""
import sys
from ddgs import DDGS

query = sys.argv[1] if len(sys.argv) > 1 else ""
count = int(sys.argv[2]) if len(sys.argv) > 2 else 5

if not query:
    print("Usage: search.py 'query' [count]", file=sys.stderr)
    sys.exit(1)

try:
    results = list(DDGS().text(query, max_results=count))
    if not results:
        print("No results found.")
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r.get('title','')}")
        print(f"    {r.get('href','')}")
        print(f"    {r.get('body','')}")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
