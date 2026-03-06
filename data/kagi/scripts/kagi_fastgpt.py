#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from kagi_client import KagiError, fastgpt


def main() -> int:
    ap = argparse.ArgumentParser(description="Kagi FastGPT API wrapper")
    ap.add_argument("query", help="Question/prompt")
    ap.add_argument("--cache", default="true", choices=["true", "false"], help="Allow cached responses (default: true)")
    ap.add_argument("--json", action="store_true", help="Print raw JSON")
    args = ap.parse_args()

    try:
        out = fastgpt(args.query, cache=(args.cache == "true"))
    except KagiError as e:
        print(str(e), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    data = (out.get("data") or {})
    output = (data.get("output") or "").strip()
    refs = data.get("references") or []

    print(output)
    if refs:
        print("\nReferences:")
        for r in refs:
            title = r.get("title") or "(no title)"
            url = r.get("url") or ""
            print(f"- {title} — {url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
