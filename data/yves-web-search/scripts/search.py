#!/usr/bin/env python3
"""
Web search using ddgs (DuckDuckGo) Python package.
Usage: python search.py "search query" [max_results]
"""
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='DuckDuckGo Search')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max', '-n', type=int, default=5, help='Max results')
    parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    try:
        from ddgs import DDGS
    except ImportError:
        print("Error: ddgs not installed. Run: pip install ddgs", file=sys.stderr)
        sys.exit(1)
    
    ddgs = DDGS()
    results = ddgs.text(args.query, max_results=args.max)
    
    if args.json:
        import json
        print(json.dumps(list(results), indent=2))
    else:
        for i, r in enumerate(results, 1):
            print(f"{i}. {r.get('title', 'No title')}")
            print(f"   {r.get('url', 'No URL')}")
            if r.get('body'):
                print(f"   {r.get('body', '')[:200]}...")
            print()

if __name__ == '__main__':
    main()
