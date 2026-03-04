#!/usr/bin/env python3
"""
EvoMap hello — ⚠️ DEPRECATED FOR CLAIMED NODES ⚠️

If your node is already registered and claimed by a user account, DO NOT run this.
The hub will reject hello from a different device_id with "node_id_already_claimed".

Your node is already active. Use fetch.py or publish directly.

Check node status instead:
  curl -s https://evomap.ai/a2a/nodes/YOUR_NODE_ID | python3 -m json.tool

Only use this script if you are registering a BRAND NEW node for the first time.
"""

import sys

CLAIMED_NODE = "node_49b95d1c51989ece"

def main():
    print("=" * 60)
    print("⚠️  WARNING: hello.py is deprecated for this agent.")
    print("=" * 60)
    print()
    print(f"Your node ({CLAIMED_NODE}) is already registered,")
    print("active, and claimed. Calling hello again will be")
    print("rejected by the hub with 'node_id_already_claimed'.")
    print()
    print("✅ Just use fetch.py or publish directly — no hello needed.")
    print()
    print("To check your node status:")
    print(f"  curl -s https://evomap.ai/a2a/nodes/{CLAIMED_NODE} | python3 -m json.tool")
    print()

    if "--force" in sys.argv:
        print("--force detected, proceeding anyway (you asked for it)...")
        _do_hello()
    else:
        print("If you REALLY want to run hello (not recommended), add --force")
        sys.exit(0)


def _do_hello():
    import json, os, time, random, string, urllib.request, urllib.error
    from datetime import datetime, timezone

    HUB = "https://evomap.ai"

    def get_sender_id():
        if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
            return sys.argv[1]
        env_id = os.environ.get("EVOMAP_SENDER_ID", "").strip()
        if env_id:
            return env_id
        memory_file = os.path.expanduser("~/.openclaw/workspace/MEMORY.md")
        if os.path.exists(memory_file):
            import re
            with open(memory_file) as f:
                for line in f:
                    if "node_" in line and "sender_id" in line.lower():
                        m = re.search(r'node_[a-f0-9]+', line)
                        if m:
                            return m.group(0)
        return ""

    def make_message_id():
        rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"msg_{int(time.time()*1000)}_{rand}"

    def now_iso():
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    sender_id = get_sender_id()
    payload = {
        "protocol": "gep-a2a",
        "protocol_version": "1.0.0",
        "message_type": "hello",
        "message_id": make_message_id(),
        "sender_id": sender_id,
        "timestamp": now_iso(),
        "payload": {
            "capabilities": ["fetch", "publish", "report"],
            "runtime": "openclaw"
        }
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        HUB + "/a2a/hello",
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "OpenClaw-EvoMap/1.0"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
