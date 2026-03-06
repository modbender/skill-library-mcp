#!/usr/bin/env python3
"""
agent-wake.py -- Wake an OpenClaw agent session via the gateway HTTP API.

Usage:
    python agent-wake.py "Task completed" [channel_id]

Arguments:
    message      Text to inject as the wake event (what the agent will read)
    channel_id   Optional Discord channel ID. If omitted, wakes the main session.

Environment variables (or .env file):
    GATEWAY_TOKEN   Your OpenClaw gateway auth token
    GATEWAY_URL     Gateway base URL (default: http://localhost:18789)

Setup:
    1. Add cron to gateway.tools.allow in openclaw.json (see references/setup.md)
    2. Set GATEWAY_TOKEN in your environment or a .env file next to this script

Exit codes:
    0  Success
    1  Missing token or HTTP error
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def load_env(path: Path) -> None:
    """Load only a local .env file next to this script."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def read_gateway_token_from_cmd() -> str:
    """Read OPENCLAW_GATEWAY_TOKEN from gateway.cmd (OpenClaw's token file)."""
    cmd_path = Path.home() / ".openclaw" / "gateway.cmd"
    if not cmd_path.exists():
        return ""
    for line in cmd_path.read_text().splitlines():
        if "OPENCLAW_GATEWAY_TOKEN=" in line:
            return line.split("=", 1)[1].strip().strip('"')
    return ""


# Load .env from script directory only (no workspace .env scanning)
load_env(Path(__file__).parent / ".env")

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:18789").rstrip("/")
# Priority: env var > local .env > gateway.cmd
GATEWAY_TOKEN = os.environ.get("GATEWAY_TOKEN", "") or read_gateway_token_from_cmd()


def wake(message: str, channel_id: str = "") -> bool:
    """
    Fire a cron wake event into the agent session.

    If channel_id is provided, targets that specific Discord channel session.
    Otherwise targets the main session.
    """
    if not GATEWAY_TOKEN:
        print("ERROR: GATEWAY_TOKEN not set. Check your .env file.", file=sys.stderr)
        return False

    event_text = message
    if channel_id:
        event_text = (
            f"{message} -- Send your response to Discord channel {channel_id} "
            f"(use message tool, action=send, target={channel_id}). "
            f"Do not respond anywhere else."
        )

    body: dict = {
        "tool": "cron",
        "args": {
            "action": "wake",
            "text": event_text,
            "mode": "now",
        },
    }

    if channel_id:
        body["sessionKey"] = f"agent:main:discord:channel:{channel_id}"

    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{GATEWAY_URL}/tools/invoke",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GATEWAY_TOKEN}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                print(f"OK: Agent woken (channel={channel_id or 'main'})")
                return True
            print(f"ERROR: HTTP {resp.status}", file=sys.stderr)
            return False
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} -- {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    msg = sys.argv[1]
    ch = sys.argv[2] if len(sys.argv) > 2 else ""

    ok = wake(msg, ch)
    sys.exit(0 if ok else 1)
