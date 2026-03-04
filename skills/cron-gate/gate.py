#!/usr/bin/env python3
"""
Cron Gate — zero-token gatekeeper for OpenClaw crons.
Checks session activity before triggering expensive LLM crons.

Usage:
    python3 gate.py [--dry-run] [evening|morning]

Runs via system crontab. Only triggers LLM crons for sessions
with new messages since the last check. Idle sessions = 0 tokens.

Configuration:
    Edit SESSION_CRONS below to map your session keys to cron IDs.
    Adjust GATEWAY_URL and file paths as needed.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# CONFIG — edit these for your setup
# ---------------------------------------------------------------------------

# Where to store last-triggered timestamps
STATE_FILE = "/opt/scripts/cron-gate-state.json"

# OpenClaw sessions file
SESSIONS_FILE = os.path.expanduser(
    "~/.openclaw/agents/main/sessions/sessions.json"
)

# OpenClaw gateway URL (default local)
GATEWAY_URL = "http://127.0.0.1:18789"

# Map session keys to their integration cron IDs.
# Use None for slots that don't exist.
# Use a real session key for the activity check.
# Prefix with "_" for pseudo-sessions that piggyback on another session's activity.
#
# Example:
# SESSION_CRONS = {
#     "agent:main:telegram:group:-1234567890": {
#         "evening": "cron-uuid-here",
#         "morning": "cron-uuid-here",
#         "check": None,  # optional: override which session to check for activity
#     },
# }
SESSION_CRONS = {
    # --- ADD YOUR SESSIONS HERE ---
    # "agent:main:telegram:group:-XXXXXXXXXX": {
    #     "evening": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    #     "morning": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    # },
}

# Time windows (UTC hours) for auto-detecting slot
EVENING_HOURS = range(4, 9)   # 04:00 - 08:59 UTC
MORNING_HOURS = range(16, 21)  # 16:00 - 20:59 UTC

# ---------------------------------------------------------------------------
# LOGIC — no need to edit below here
# ---------------------------------------------------------------------------


def get_slot(force=None):
    """Determine which integration slot to run."""
    if force:
        return force
    hour = datetime.now(timezone.utc).hour
    if hour in EVENING_HOURS:
        return "evening"
    elif hour in MORNING_HOURS:
        return "morning"
    return None


def load_state():
    """Load last-triggered timestamps from state file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    """Save last-triggered timestamps to state file."""
    os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_session_timestamps():
    """Read updatedAt timestamps from sessions.json."""
    with open(SESSIONS_FILE) as f:
        data = json.load(f)
    result = {}
    for key, val in data.items():
        updated = val.get("updatedAt", 0)
        if isinstance(updated, (int, float)) and updated > 1e9:
            result[key] = updated  # epoch milliseconds
    return result


def trigger_cron(cron_id, dry_run=False):
    """Trigger an OpenClaw cron job via the gateway API."""
    if dry_run:
        print(f"  [DRY RUN] Would trigger cron {cron_id}")
        return True

    url = f"{GATEWAY_URL}/api/cron/{cron_id}/run"
    req = urllib.request.Request(
        url, method="POST", data=b"",
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f"  ✅ Triggered {cron_id} — HTTP {resp.status}")
            return True
    except urllib.error.URLError as e:
        print(f"  ❌ Failed to trigger {cron_id}: {e}")
        return False


def main():
    dry_run = "--dry-run" in sys.argv

    # Check for forced slot argument
    force_slot = None
    for arg in sys.argv[1:]:
        if arg in ("evening", "morning"):
            force_slot = arg

    slot = get_slot(force_slot)
    if not slot:
        hour = datetime.now(timezone.utc).hour
        print(
            f"Not in an integration window (UTC hour: {hour}). "
            "Pass 'evening' or 'morning' to force."
        )
        return

    print(f"Cron Gate — slot: {slot}, dry_run: {dry_run}")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    if not SESSION_CRONS:
        print(
            "\n⚠️  No sessions configured! Edit SESSION_CRONS in gate.py.\n"
            "See SKILL.md for setup instructions."
        )
        return

    state = load_state()
    sessions = get_session_timestamps()

    triggered = 0
    skipped = 0

    for session_key, crons in SESSION_CRONS.items():
        cron_id = crons.get(slot)
        if not cron_id:
            continue

        # Determine which session to check for activity
        # Use "check" override if provided, otherwise derive from key
        lookup_key = crons.get("check", session_key)

        updated_at = sessions.get(lookup_key, 0)
        state_key = f"{session_key}:{slot}"
        last_checked = state.get(state_key, 0)

        if updated_at > last_checked:
            age_hours = (time.time() * 1000 - updated_at) / 3_600_000
            print(f"\n🔔 {session_key} — new activity ({age_hours:.1f}h ago)")
            if trigger_cron(cron_id, dry_run):
                state[state_key] = int(time.time() * 1000)
                triggered += 1
        else:
            print(f"  💤 {session_key} — no new activity, skipping")
            skipped += 1

    save_state(state)
    print(f"\nDone: {triggered} triggered, {skipped} skipped")


if __name__ == "__main__":
    main()
