#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from kagi_client import KagiError, search


def main() -> int:
    ap = argparse.ArgumentParser(description="Kagi Search API wrapper")
    ap.add_argument("query", help="Search query")
    ap.add_argument("--limit", type=int, default=10, help="Max results to print (default: 10)")
    ap.add_argument("--json", action="store_true", help="Print raw JSON")
    args = ap.parse_args()

    try:
        out = search(args.query)
    except KagiError as e:
        print(str(e), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    meta = out.get("meta", {})
    data = out.get("data", []) or []

    print(f"Kagi Search: {args.query}")
    if meta:
        ms = meta.get("ms")
        bal = meta.get("api_balance")
        node = meta.get("node")
        extras = []
        if ms is not None:
            extras.append(f"{ms}ms")
        if node:
            extras.append(str(node))
        if bal is not None:
            extras.append(f"balance={bal}")
        if extras:
            print("(" + ", ".join(extras) + ")")
    print()

    for i, r in enumerate(data[: args.limit], start=1):
        title = r.get("title") or "(no title)"
        url = r.get("url") or ""
        snippet = (r.get("snippet") or "").strip().replace("\n", " ")
        print(f"{i}. {title}")
        if url:
            print(f"   {url}")
        if snippet:
            print(f"   {snippet}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
