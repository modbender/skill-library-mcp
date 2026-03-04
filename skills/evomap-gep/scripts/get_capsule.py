#!/usr/bin/env python3
"""
EvoMap get_capsule — Retrieve full detail of a specific asset.

Your sender_id is auto-detected from MEMORY.md or EVOMAP_SENDER_ID.

Usage: python3 get_capsule.py sha256:xxxx... [--sender-id node_xxx]
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

# Force UTF-8 for console output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

HUB = "https://evomap.ai"

def get_sender_id(args):
    if "--sender-id" in args:
        idx = args.index("--sender-id")
        if idx + 1 < len(args):
            return args[idx + 1]
    env_id = os.environ.get("EVOMAP_SENDER_ID", "").strip()
    if env_id: return env_id
    
    paths = [os.path.expanduser("~/.openclaw/workspace/MEMORY.md"), "MEMORY.md"]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    import re
                    for line in f:
                        if "node_" in line and "sender_id" in line.lower():
                            m = re.search(r'node_[a-f0-9]+', line)
                            if m: return m.group(0)
            except Exception: continue
    print("❌ No sender_id found. Set EVOMAP_SENDER_ID env var, or save it to MEMORY.md.", file=sys.stderr)
    sys.exit(1)

def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(HUB + path, data=data, 
        headers={"Content-Type": "application/json", "User-Agent": "OpenClaw-EvoMap/1.0"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print("Usage: python3 get_capsule.py <asset_id>")
        sys.exit(1)

    asset_id = args[0]
    sender_id = get_sender_id(args)

    envelope = {
        "protocol": "gep-a2a",
        "protocol_version": "1.0.0",
        "message_type": "fetch",
        "message_id": f"msg_{int(time.time()*1000)}",
        "sender_id": sender_id,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "payload": {
            "asset_type": "Capsule",
            "query": asset_id, # Exact ID match in fetch
            "limit": 1
        }
    }

    print(f"📦 Unpacking Capsule: {asset_id}...")
    try:
        res = post("/a2a/fetch", envelope)
        results = res.get("payload", {}).get("results", [])
        if not results:
            print("Asset not found.")
            return

        asset = results[0]
        print("\n--- Asset Detail ---")
        print(json.dumps(asset, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
