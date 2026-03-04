#!/usr/bin/env python3
"""Guardian Telegram primary-channel notifier with approve/deny override inline buttons.

BL-039: When a threat is blocked, dispatch a Telegram notification containing
threat details and two inline action buttons:
  - ✅ Approve Override  → calls POST /api/approve-override with the request token
  - 🚫 Keep Blocked      → calls POST /deny-request with the request token

Usage (via config.json):
  "alerts": {
    "primary_notify_command": "python3 /abs/path/to/skills/guardian/scripts/telegram_notify.py"
  }

Receives one JSON argument: the Guardian block payload from serve.py.

Dispatch strategy:
  1. Always write the pending notification to a sidecar JSON queue
     (memory/guardian-pending-notify.json) so the agent heartbeat can pick it
     up as a fallback even if openclaw agent dispatch fails.
  2. Attempt immediate dispatch via `openclaw agent --channel telegram --deliver`
     so the agent sends the Telegram message with inline buttons right away.

The inline buttons use callback_data:
  - guardian_approve:<token>  → Approve Override
  - guardian_deny:<token>     → Keep Blocked

The agent's GUARDIAN.md context instructs it to handle these callbacks by
calling the appropriate Guardian API endpoints.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SIDECAR_PATH = WORKSPACE / "memory" / "guardian-pending-notify.json"
GUARDIAN_API_BASE = "http://127.0.0.1:8080"


def _severity_emoji(severity: str) -> str:
    return {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
    }.get((severity or "").lower(), "⚪")


def build_agent_message(payload: dict) -> str:
    """Build the instruction message that tells the agent to send a Telegram alert."""
    severity = (payload.get("severity") or "unknown").upper()
    sig_id = payload.get("sig_id") or "unknown"
    channel = payload.get("channel") or "unknown"
    summary = (payload.get("summary") or "A threat was blocked.").strip(".")
    token = payload.get("approval_token") or ""
    sev_emoji = _severity_emoji(severity)

    evidence = (payload.get("evidence") or "").strip()
    evidence_line = ""
    if evidence:
        preview = evidence[:120].replace("`", "'")
        if len(evidence) > 120:
            preview += "…"
        evidence_line = f"\n*Flagged:* `{preview}`"

    # Human-readable notification text
    notif_text = (
        f"{sev_emoji} *Guardian Security Alert*\n"
        f"A *{severity}* threat was blocked.\n"
        f"Sig: `{sig_id}` | Channel: `{channel}`\n"
        f"_{summary}._{evidence_line}\n\n"
        f"🔗 [View in Guardian dashboard](http://192.168.1.196:8089/guardian.html)\n\n"
        f"Approve to allow this content through, or keep it blocked."
    )

    if token:
        buttons_instruction = (
            f"Send with two inline keyboard buttons:\n"
            f"  - Label: '✅ Approve Override' | callback_data: 'guardian_approve:{token}'\n"
            f"  - Label: '🚫 Keep Blocked' | callback_data: 'guardian_deny:{token}'\n\n"
            f"When the user presses '✅ Approve Override', call:\n"
            f"  POST {GUARDIAN_API_BASE}/api/approve-override\n"
            f"  Body: {{\"token\": \"{token}\", \"actor\": \"telegram-user\", \"reason\": \"user-approved\"}}\n\n"
            f"When the user presses '🚫 Keep Blocked', call:\n"
            f"  POST {GUARDIAN_API_BASE}/deny-request\n"
            f"  Body: {{\"token\": \"{token}\", \"actor\": \"telegram-user\", \"reason\": \"user-denied\"}}\n"
            f"Then confirm the action to the user (e.g. 'Override approved ✅' or 'Kept blocked 🚫')."
        )
    else:
        buttons_instruction = "(No approval token available — send as informational notification only.)"

    return (
        f"[GUARDIAN SECURITY ALERT — AUTOMATED]\n\n"
        f"Please send me (the user) this Telegram notification immediately:\n\n"
        f"---MESSAGE START---\n{notif_text}\n---MESSAGE END---\n\n"
        f"{buttons_instruction}\n\n"
        f"This is an automated notification from Guardian security. "
        f"Do not add commentary — just send the Telegram message and confirm you sent it."
    )


def write_sidecar(payload: dict) -> None:
    """Write/append the notification to the pending sidecar queue (heartbeat fallback)."""
    SIDECAR_PATH.parent.mkdir(parents=True, exist_ok=True)
    pending: list = []
    if SIDECAR_PATH.exists():
        try:
            pending = json.loads(SIDECAR_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pending = []
    pending.append({**payload, "queued_at": datetime.now(timezone.utc).isoformat()})
    SIDECAR_PATH.write_text(json.dumps(pending, indent=2, default=str), encoding="utf-8")


DASHBOARD_URL = "http://192.168.1.196:8089/guardian.html"


def build_telegram_message(payload: dict) -> str:
    """Build a Telegram alert message with content preview and dashboard link."""
    severity = (payload.get("severity") or "unknown").upper()
    sig_id = payload.get("sig_id") or "unknown"
    channel = payload.get("channel") or "unknown"
    summary = (payload.get("summary") or "A threat was blocked.").strip(".")
    token = payload.get("approval_token") or ""
    evidence = (payload.get("evidence") or "").strip()
    threat_count = payload.get("threat_count", 1)
    sev_emoji = _severity_emoji(severity)

    text = (
        f"{sev_emoji} *Guardian Security Alert*\n"
        f"A *{severity}* threat was blocked.\n"
        f"Sig: `{sig_id}` | Channel: `{channel}`"
    )
    if threat_count and int(threat_count) > 1:
        text += f" | {threat_count} threats"
    text += f"\n_{summary}._"

    # Content preview — show truncated flagged snippet
    if evidence:
        preview = evidence[:120].replace("`", "'")
        if len(evidence) > 120:
            preview += "…"
        text += f"\n\n*Flagged content:*\n`{preview}`"

    # Dashboard link
    text += f"\n\n🔗 [View in Guardian dashboard]({DASHBOARD_URL})"

    if token:
        text += "\n\nApprove to allow through, or keep blocked."
    return text


def dispatch_via_agent(payload: dict) -> bool:
    """Dispatch notification via openclaw message send --channel telegram.

    Returns True if the process exited cleanly.
    """
    msg = build_telegram_message(payload)
    token = payload.get("approval_token") or ""
    cmd = [
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--target", "8191524631",
        "--message", msg,
    ]
    if token:
        buttons = (
            f'[[{{"text":"✅ Allow future","callback_data":"guardian_approve:{token}"}},'
            f'{{"text":"🚫 Keep blocked","callback_data":"guardian_deny:{token}"}}]]' 
        )
        cmd += ["--buttons", buttons]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: telegram_notify.py <json_payload>\n")
        return 1

    try:
        payload = json.loads(sys.argv[1])
    except (json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(f"Invalid JSON payload: {exc}\n")
        return 1

    # Always write sidecar first as a durable fallback
    try:
        write_sidecar(payload)
    except Exception as exc:
        sys.stderr.write(f"Sidecar write failed (non-fatal): {exc}\n")

    # Attempt immediate dispatch via openclaw agent
    ok = dispatch_via_agent(payload)
    return 0 if ok else 2  # exit 2 = dispatch failed but sidecar written


if __name__ == "__main__":
    raise SystemExit(main())
