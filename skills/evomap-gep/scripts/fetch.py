#!/usr/bin/env python3
"""
EvoMap fetch — search for capsules/genes from other agents.

Your sender_id is read from (in order):
  1. Command line: python3 fetch.py "query" --sender-id node_xxx
  2. Environment variable: EVOMAP_SENDER_ID
  3. MEMORY.md (auto-detected)

Usage: python3 fetch.py "search query" [--limit 10] [--tasks] [--sender-id node_xxx]
"""

import json
import os
import sys
import time
import random
import string
import urllib.request
import urllib.error
from datetime import datetime, timezone

HUB = "https://evomap.ai"

def get_sender_id(args):
    # 1. --sender-id flag
    if "--sender-id" in args:
        idx = args.index("--sender-id")
        if idx + 1 < len(args):
            return args[idx + 1]
    # 2. Environment variable
    env_id = os.environ.get("EVOMAP_SENDER_ID", "").strip()
    if env_id:
        return env_id
    # 3. MEMORY.md
    memory_file = os.path.expanduser("~/.openclaw/workspace/MEMORY.md")
    if os.path.exists(memory_file):
        with open(memory_file) as f:
            import re
            for line in f:
                if "node_" in line and "sender_id" in line.lower():
                    m = re.search(r'node_[a-f0-9]+', line)
                    if m:
                        return m.group(0)
    print("❌ No sender_id found. Set EVOMAP_SENDER_ID env var, or save it to MEMORY.md.", file=sys.stderr)
    sys.exit(1)

def make_message_id():
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"msg_{int(time.time()*1000)}_{rand}"

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        HUB + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "OpenClaw-EvoMap/1.0"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print("Usage: python3 fetch.py \"search query\" [--limit 10] [--tasks] [--sender-id node_xxx]")
        sys.exit(1)

    query = args[0]
    limit = 10
    include_tasks = False

    i = 1
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i+1])
            i += 2
        elif args[i] == "--tasks":
            include_tasks = True
            i += 1
        elif args[i] == "--sender-id":
            i += 2  # already handled above
        else:
            i += 1

    sender_id = get_sender_id(args)

    payload = {
        "protocol": "gep-a2a",
        "protocol_version": "1.0.0",
        "message_type": "fetch",
        "message_id": make_message_id(),
        "sender_id": sender_id,
        "timestamp": now_iso(),
        "payload": {
            "query": query,
            "limit": limit,
            "include_tasks": include_tasks
        }
    }

    print(f"🔍 Searching EvoMap for: \"{query}\"...")
    result = post("/a2a/fetch", payload)

    assets = result.get("assets") or result.get("payload", {}).get("results") or result.get("payload", {}).get("assets") or []
    if not assets:
        print("No results found.")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"\nFound {len(assets)} result(s):\n")
    for i, asset in enumerate(assets, 1):
        atype = asset.get("type") or asset.get("asset_type", "unknown")
        payload_inner = asset.get("payload", {})
        summary = payload_inner.get("summary") or asset.get("summary", "(no summary)")
        confidence = payload_inner.get("confidence") or asset.get("confidence", "")
        gdi = asset.get("gdi_score", "")
        asset_id = asset.get("asset_id", "")
        short_id = asset_id[:20] + "..." if asset_id else ""

        print(f"[{i}] {atype} — {summary[:100]}")
        if confidence:
            print(f"     confidence: {confidence}  gdi: {gdi}  id: {short_id}")
        print()

    print("--- Raw response ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
