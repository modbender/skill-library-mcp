#!/usr/bin/env python3
"""
Project Manager Agent - Monitor OpenClaw subagents and output stalled session keys for steering.

Uses OPENCLAW_HOME for session path (default: ~/.openclaw). File-based; no gateway API required.
When run with --json, prints a JSON block with stalledSessionKeys so the agent can call
sessions_send(sessionKey, message, 0) for each.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Default OpenClaw sessions path (allow override for exec/sandbox)
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", str(Path.home() / ".openclaw")))
SESSIONS_JSON = OPENCLAW_HOME / "agents" / "main" / "sessions" / "sessions.json"
STEER_STATE_PATH = OPENCLAW_HOME / "logs" / "project-manager-agent.steer_state.json"
DEFAULT_STEER_MESSAGE = "Please continue working on your task."
DEFAULT_STEER_COOLDOWN_MINUTES = 15
DEFAULT_MAX_STEER_PER_RUN = 5


def load_config():
    """Load optional config from skill config.json if present."""
    skill_dir = Path(__file__).resolve().parent.parent
    config_path = skill_dir / "config.json"
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def load_sessions():
    """Load sessions.json and return list of session dicts with added 'key' field."""
    if not SESSIONS_JSON.exists():
        return []
    try:
        with open(SESSIONS_JSON, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    sessions = []
    for key, session in data.items():
        if key.startswith("agent:"):
            session["key"] = key
            sessions.append(session)
    return sessions


def is_subagent(session_key):
    """Return True if session key indicates a subagent."""
    return session_key.startswith("agent:main:subagent:")


def session_age_ms(session):
    """Calculate age in milliseconds based on updatedAt."""
    updated_at = session.get("updatedAt")
    if not updated_at:
        return None
    now_ms = int(time.time() * 1000)
    return now_ms - updated_at


def load_steer_state():
    """Load last-steered timestamps per session key."""
    if not STEER_STATE_PATH.exists():
        return {}
    try:
        with open(STEER_STATE_PATH, "r") as f:
            data = json.load(f)
        return data.get("lastSteered", {})
    except (json.JSONDecodeError, OSError):
        return {}


def save_steer_state(last_steered):
    """Persist last-steered timestamps. Call after agent runs sessions_send via --record-steered."""
    STEER_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(STEER_STATE_PATH, "w") as f:
            json.dump({"lastSteered": last_steered}, f, indent=2)
    except OSError:
        pass


def record_steered(session_keys):
    """Update steer state with current timestamp for each key (call with --record-steered)."""
    last_steered = load_steer_state()
    now_ms = int(time.time() * 1000)
    for k in session_keys:
        if k:
            last_steered[k] = now_ms
    save_steer_state(last_steered)


def list_and_monitor_subagents(
    staleness_threshold_minutes=10,
    check_all_sessions=False,
    steer_cooldown_minutes=None,
    steer_message=None,
    max_steer_per_run=None,
    apply_cooldown=True,
):
    """
    List subagents, detect stalls, optionally filter by cooldown.
    Returns (human_summary_str, stalled_session_keys_list).
    """
    config = load_config()
    if steer_cooldown_minutes is None:
        steer_cooldown_minutes = config.get("steer_cooldown_minutes", DEFAULT_STEER_COOLDOWN_MINUTES)
    if steer_message is None:
        steer_message = config.get("steer_message", DEFAULT_STEER_MESSAGE)
    if max_steer_per_run is None:
        max_steer_per_run = config.get("max_steer_per_run", DEFAULT_MAX_STEER_PER_RUN)

    sessions = load_sessions()
    now = datetime.now()
    stall_threshold_ms = staleness_threshold_minutes * 60 * 1000
    cooldown_ms = steer_cooldown_minutes * 60 * 1000 if apply_cooldown else 0
    last_steered = load_steer_state() if apply_cooldown else {}
    now_ms = int(time.time() * 1000)

    output_messages = []
    stalled_keys = []

    for session in sessions:
        key = session.get("key", "")
        if not key:
            continue
        if not check_all_sessions and not is_subagent(key):
            continue

        session_id = session.get("sessionId", "?")
        display_name = session.get("displayName") or session_id
        updated_at_ms = session.get("updatedAt", 0)
        last_update_time = datetime.fromtimestamp(updated_at_ms / 1000) if updated_at_ms else now
        age_ms = session_age_ms(session)

        status_emoji = ""
        status_text = ""
        recommended_action = ""

        if age_ms is not None and age_ms > stall_threshold_ms:
            status_emoji = "⏳"
            status_text = f"stalled for {age_ms / 60000:.1f} minutes."
            recommended_action = f"Consider steering subagent {display_name} ({session_id}) with a 'continue working' message."
            # Apply cooldown: only include in stalled_keys if not recently steered
            if cooldown_ms > 0 and key in last_steered:
                if now_ms - last_steered[key] < cooldown_ms:
                    recommended_action = "(steer cooldown active; skip this run)"
                else:
                    stalled_keys.append(key)
            else:
                stalled_keys.append(key)
        elif session.get("abortedLastRun"):
            status_emoji = "❌"
            status_text = "aborted its last run."
            recommended_action = f"Check subagent {display_name} ({session_id}) for errors in its transcript."
        else:
            status_emoji = "✔️"
            status_text = "actively working."

        output_messages.append(
            f"{status_emoji} {display_name} ({session_id}): {status_text} (Last update: {last_update_time.strftime('%Y-%m-%d %H:%M:%S')}). {recommended_action}"
        )

    if not output_messages:
        output_messages.insert(0, "No active subagents or tasks detected at this time.")

    # Cap number of keys to steer per run
    if max_steer_per_run and len(stalled_keys) > max_steer_per_run:
        stalled_keys = stalled_keys[:max_steer_per_run]

    summary = "\n".join(output_messages)
    return summary, stalled_keys, steer_message


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor OpenClaw subagents; optional JSON for agent steering.")
    parser.add_argument(
        "--staleness_threshold_minutes",
        type=int,
        default=None,
        help="Minutes after which a subagent is considered stalled (default from config or 10).",
    )
    parser.add_argument(
        "--check_all_sessions",
        action="store_true",
        help="Check all sessions, not just subagents of the current main session.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print human summary then a JSON line with stalledSessionKeys and steerMessage for agent steering.",
    )
    parser.add_argument(
        "--no_cooldown",
        action="store_true",
        help="Ignore steer cooldown (output all stalled keys).",
    )
    parser.add_argument(
        "--record-steered",
        nargs="*",
        default=None,
        metavar="KEY",
        help="Record these session keys as just steered (for cooldown). Pass keys after agent calls sessions_send.",
    )
    args = parser.parse_args()

    if args.record_steered is not None:
        record_steered(args.record_steered or [])
        print(f"Recorded {len(args.record_steered or [])} session(s) as steered.")
        sys.exit(0)

    config = load_config()
    staleness = args.staleness_threshold_minutes
    if staleness is None:
        staleness = config.get("staleness_threshold_minutes", 10)

    try:
        summary, stalled_keys, steer_message = list_and_monitor_subagents(
            staleness_threshold_minutes=staleness,
            check_all_sessions=args.check_all_sessions,
            apply_cooldown=not args.no_cooldown,
        )
    except Exception as e:
        summary = f"❌ Error monitoring subagents: {e}"
        stalled_keys = []
        steer_message = DEFAULT_STEER_MESSAGE

    if args.json:
        print(summary)
        out = {
            "summary": summary.split("\n")[0] if summary else "",
            "stalledSessionKeys": stalled_keys,
            "steerMessage": steer_message,
        }
        print(json.dumps(out))
    else:
        print(summary)
