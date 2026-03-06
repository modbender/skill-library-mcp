#!/usr/bin/env python3
"""JurisFR — one-shot helper.

Goal: produce a ready-to-use SYSTEM + USER prompt (and optionally JSON) for any question.
This script does NOT call an LLM by itself; it prepares the prompt + sources.

Usage:
  python scripts/one_shot.py "<question>"
  python scripts/one_shot.py "<question>" --json
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ask import build_rag_prompt


def main():
    if len(sys.argv) < 2:
        print("Usage: one_shot.py <question> [--json]")
        raise SystemExit(1)

    args = sys.argv[1:]
    as_json = False
    if "--json" in args:
        as_json = True
        args.remove("--json")

    question = " ".join(args).strip()
    payload = build_rag_prompt(question)

    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return

    print("=" * 80)
    print("SYSTEM PROMPT")
    print("=" * 80)
    print(payload["system"].strip())
    print("\n" + "=" * 80)
    print(f"USER PROMPT (sources={payload['sources_count']})")
    print("=" * 80)
    print(payload["user"].strip())


if __name__ == "__main__":
    main()
