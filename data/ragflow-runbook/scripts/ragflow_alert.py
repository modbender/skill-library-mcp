#!/usr/bin/env python3

"""Send a RAGFlow ops alert via OpenClaw messaging.

This script is intentionally simple and avoids reading any local secret files.

Inputs:
- --title (required)
- --details (optional; do NOT include secrets)
- --account (optional; default: notification)
- --target (required unless OPENCLAW_PRIMARY_CHAT_ID is set)

Behavior:
- Calls: openclaw message send --channel telegram ...

Exit codes:
- 0 if the OpenClaw CLI call succeeds, otherwise non-zero.
"""

import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys


def now_iso() -> str:
    try:
        return dt.datetime.now().astimezone().isoformat(timespec="seconds")
    except Exception:
        return dt.datetime.now().isoformat(timespec="seconds")


def send_telegram(account: str, target: str, message: str) -> int:
    if not shutil.which("openclaw"):
        print("ERROR: 'openclaw' CLI not found. Install/configure OpenClaw or disable alerting.")
        return 3

    cmd = [
        "openclaw",
        "message",
        "send",
        "--channel",
        "telegram",
        "--account",
        account,
        "--target",
        target,
        "--message",
        message,
        "--silent",
    ]
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr)
    return p.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Send RAGFlow alert to Telegram via OpenClaw")
    ap.add_argument("--title", required=True)
    ap.add_argument("--details", default="")
    ap.add_argument("--account", default="notification")
    ap.add_argument("--target", default=os.environ.get("OPENCLAW_PRIMARY_CHAT_ID", "").strip())
    args = ap.parse_args()

    if not args.target:
        print("ERROR: missing alert target. Set OPENCLAW_PRIMARY_CHAT_ID or pass --target.")
        return 2

    ts = now_iso()
    msg = f"[{ts}] RAGFlow ALERT: {args.title}"
    if args.details:
        msg += f"\n{args.details}"

    return send_telegram(args.account, args.target, msg)


if __name__ == "__main__":
    raise SystemExit(main())
