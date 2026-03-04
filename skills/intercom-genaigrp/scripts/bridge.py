#!/usr/bin/env python3
"""Optional helper for formatting intercom payloads.

This script does not send network requests by itself in OpenClaw runtime.
It only prepares a routed message shape for manual/integration use.
"""

import sys


def build_payload(target: str, content: str, sender: str = "IntercomBridge") -> dict:
    return {
        "sessionKey": target,
        "message": f"FROM {sender}: {content}",
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: bridge.py <targetSessionKey> <message>")
        raise SystemExit(1)
    target = sys.argv[1].strip()
    content = " ".join(sys.argv[2:]).strip()
    print(build_payload(target, content))
