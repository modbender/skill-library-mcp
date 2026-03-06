#!/usr/bin/env python3
"""Discord bridge for Codeflow sessions.

Connects to Discord gateway, watches a configured channel for messages from
allowed users, and provides lightweight session status/log commands.

Runs as a companion process alongside dev-relay.sh.

Usage:
    python3 discord-bridge.py [--channel CHANNEL_ID] [--users USER_ID,...] [--verbose]

Environment:
    CODEFLOW_BOT_TOKEN   Discord bot token (or macOS Keychain: discord-bot-token/codeflow)
    BRIDGE_CHANNEL_ID    Discord channel ID to watch (required; fail-closed if unset)
    BRIDGE_ALLOWED_USERS Comma-separated Discord user IDs (required; fail-closed if unset)

Commands (from Discord):
    !status   Show active Codeflow sessions
    !log      Show recent output:  !log [PID]

Session data read from: /tmp/dev-relay-sessions/<PID>.json
"""

import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
from collections import deque

# Version guard (keep before importing local modules / running bridge logic).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from py_compat import require_python310

require_python310(prog="discord-bridge")

# Third-party dependency (only needed when actually running the bridge).
import websocket  # pip install websocket-client

# Allow importing sibling helpers (redaction.py).
from redaction import redact_text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SESSION_DIR = "/tmp/dev-relay-sessions"


def get_bot_token():
    """Get bot token from env, keychain, or file."""
    token = os.environ.get("CODEFLOW_BOT_TOKEN", "")
    if token:
        return token
    # Try macOS Keychain
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "discord-bot-token", "-a", "codeflow", "-w"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        pass
    # Try file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Secrets live in the public scripts/ dir, not alongside internal implementation.
    public_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
    token_file = os.path.join(public_dir, ".bot-token")
    if os.path.exists(token_file):
        with open(token_file) as f:
            return f.read().strip()
    return ""


BOT_TOKEN = get_bot_token()
CHANNEL_ID = os.environ.get("BRIDGE_CHANNEL_ID", "")
ALLOWED_USERS = set(filter(None, os.environ.get("BRIDGE_ALLOWED_USERS", "").split(",")))
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv

# Safety mode: suppress high-risk content and use stricter redaction.
def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


SAFE_MODE = _env_flag("CODEFLOW_SAFE_MODE", False)
DISCORD_ALLOW_MENTIONS = _env_flag("CODEFLOW_DISCORD_ALLOW_MENTIONS", False)

# Parse CLI args
for i, arg in enumerate(sys.argv[1:], 1):
    if arg == "--channel" and i < len(sys.argv) - 1:
        CHANNEL_ID = sys.argv[i + 1]
    elif arg == "--users" and i < len(sys.argv) - 1:
        ALLOWED_USERS = set(filter(None, sys.argv[i + 1].split(",")))


def log(msg):
    if VERBOSE:
        print(f"[bridge] {msg}", flush=True)

def _bridge_lock(channel_id: str, user_id: str) -> tuple[bool, str]:
    """Fail-closed guard for remote commands.

    Returns: (locked, reason_to_reply). If locked is True and reason is empty,
    the command should be refused silently to avoid advertising broadly.
    """
    configured_channel = bool(CHANNEL_ID)
    configured_users = bool(ALLOWED_USERS)

    if not configured_channel and not configured_users:
        # No safe place to reply: refuse silently.
        return True, ""

    if not configured_channel:
        # Only respond to known allowed users (if any) to avoid advertising broadly.
        if user_id and user_id in ALLOWED_USERS:
            return True, "🔒 Bridge requires BRIDGE_CHANNEL_ID / --channel (fail-closed)."
        return True, ""

    if not configured_users:
        # Only respond in the configured channel to avoid advertising broadly.
        if channel_id and channel_id == CHANNEL_ID:
            return True, "🔒 Bridge requires BRIDGE_ALLOWED_USERS / --users (fail-closed)."
        return True, ""

    return False, ""


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

def get_active_sessions():
    """Read active Codeflow sessions from /tmp/dev-relay-sessions/."""
    sessions = {}
    if not os.path.isdir(SESSION_DIR):
        return sessions
    for fname in os.listdir(SESSION_DIR):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(SESSION_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            pid = data.get("pid")
            # Check if process is still alive
            if pid:
                try:
                    os.kill(pid, 0)
                    sessions[str(pid)] = data
                except OSError:
                    # Process dead, clean up stale file
                    os.remove(fpath)
        except (json.JSONDecodeError, OSError):
            continue
    return sessions

def get_recent_log(pid):
    """Get recent output from a session's relay dir."""
    sessions = get_active_sessions()
    session = sessions.get(str(pid))
    if not session:
        return None, "Session not found"
    relay_dir = session.get("relayDir", "")
    if not relay_dir:
        return None, "No relay dir"

    # Try stream.jsonl for structured output
    stream_path = os.path.join(relay_dir, "stream.jsonl")
    if os.path.exists(stream_path):
        try:
            recent = deque(maxlen=20)
            with open(stream_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    recent.append(line)
            entries = []
            for line in recent:
                try:
                    evt = json.loads(line.strip())
                    etype = evt.get("type", "?")
                    entries.append(f"[{etype}]")
                except json.JSONDecodeError:
                    pass
            if entries:
                return "\n".join(entries), None
            return None, "No stream events found"
        except OSError:
            pass

    return None, "No stream.jsonl found"


# ---------------------------------------------------------------------------
# Discord API helper
# ---------------------------------------------------------------------------

def discord_api_post(endpoint, payload):
    """POST to Discord REST API."""
    url = f"https://discord.com/api/v10{endpoint}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bot {BOT_TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        if raw:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def reply(channel_id, content):
    """Send a reply message to the Discord channel."""
    content = content[:1900]
    content = redact_text(content, strict=SAFE_MODE)
    payload = {"content": content}
    if not DISCORD_ALLOW_MENTIONS:
        payload["allowed_mentions"] = {"parse": []}
    discord_api_post(f"/channels/{channel_id}/messages", payload)


# ---------------------------------------------------------------------------
# Message handler
# ---------------------------------------------------------------------------

def handle_message(data):
    """Process an incoming Discord message."""
    # Ignore bot messages
    author = data.get("author", {})
    if author.get("bot"):
        return

    channel_id = data.get("channel_id", "")
    user_id = author.get("id", "")
    content = data.get("content", "").strip()

    # Check channel filter
    if CHANNEL_ID and channel_id != CHANNEL_ID:
        return

    # Check user filter
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        return

    if not content:
        return

    log(f"Message from {author.get('username', '?')}: {content[:100]}")

    # Only handle supported commands.
    lower = content.lower()
    is_status = lower == "!status"
    is_log = lower.startswith("!log")
    if not (is_status or is_log):
        return

    # Fail-closed by default: refuse commands unless BOTH channel + allowlist are configured.
    locked, lock_reason = _bridge_lock(channel_id, user_id)
    if locked:
        if lock_reason:
            reply(channel_id, lock_reason)
        return

    # --- Command: !status ---
    if is_status:
        sessions = get_active_sessions()
        if not sessions:
            reply(channel_id, "📭 No active Codeflow sessions")
            return
        lines = ["📡 **Active Sessions:**"]
        for pid, s in sessions.items():
            agent = s.get("agent", "?")
            workdir = s.get("workdir", "?")
            start = s.get("startTime", "?")
            lines.append(f"  `{pid}` — {agent} | `{workdir}` | {start}")
        reply(channel_id, "\n".join(lines))
        return

    # --- Command: !log [PID] ---
    if is_log:
        parts = content.split()
        sessions = get_active_sessions()
        if len(parts) >= 2:
            pid = parts[1]
        elif len(sessions) == 1:
            pid = list(sessions.keys())[0]
        else:
            reply(channel_id, "Usage: `!log <PID>` (multiple sessions active)")
            return
        log_content, err = get_recent_log(pid)
        if err:
            reply(channel_id, f"❌ {err}")
        else:
            log_content = redact_text(log_content or "", strict=SAFE_MODE)
            if SAFE_MODE:
                # Keep it tight in safe mode: avoid large bodies.
                log_content = (log_content[:300] + "…") if len(log_content) > 300 else log_content
            reply(channel_id, f"📜 Recent log for `{pid}`:\n```\n{log_content}\n```")
        return


# ---------------------------------------------------------------------------
# Discord Gateway (WebSocket)
# ---------------------------------------------------------------------------

GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
_heartbeat_interval = None
_sequence = None
_ws = None


def send_heartbeat():
    """Send gateway heartbeat."""
    global _ws, _sequence
    while True:
        if _heartbeat_interval and _ws:
            try:
                _ws.send(json.dumps({"op": 1, "d": _sequence}))
                log("Heartbeat sent")
            except Exception:
                break
        time.sleep(_heartbeat_interval / 1000 if _heartbeat_interval else 30)


def on_message(ws, raw):
    global _heartbeat_interval, _sequence
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return

    op = data.get("op")
    seq = data.get("s")
    if seq is not None:
        _sequence = seq

    # Hello — start heartbeat
    if op == 10:
        _heartbeat_interval = data["d"]["heartbeat_interval"]
        log(f"Gateway hello, heartbeat interval: {_heartbeat_interval}ms")
        # Send Identify
        ws.send(json.dumps({
            "op": 2,
            "d": {
                "token": BOT_TOKEN,
                "intents": 1 << 9 | 1 << 15,  # GUILD_MESSAGES + MESSAGE_CONTENT
                "properties": {
                    "os": "linux",
                    "browser": "codeflow-bridge",
                    "device": "codeflow-bridge",
                }
            }
        }))
        # Start heartbeat thread
        hb = threading.Thread(target=send_heartbeat, daemon=True)
        hb.start()

    # Heartbeat ACK
    elif op == 11:
        log("Heartbeat ACK")

    # Dispatch
    elif op == 0:
        event_type = data.get("t", "")
        if event_type == "READY":
            user = data["d"].get("user", {})
            log(f"Connected as {user.get('username', '?')}#{user.get('discriminator', '?')}")
            print(f"🔗 Discord bridge connected as {user.get('username', '?')}", flush=True)
        elif event_type == "MESSAGE_CREATE":
            handle_message(data.get("d", {}))


def on_error(ws, error):
    print(f"[bridge] WebSocket error: {error}", file=sys.stderr, flush=True)


def on_close(ws, close_code, close_msg):
    print(f"[bridge] WebSocket closed: {close_code} {close_msg}", flush=True)


def on_open(ws):
    log("WebSocket connected")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global _ws

    if not BOT_TOKEN:
        print("❌ Error: No bot token found", file=sys.stderr)
        print("  Set CODEFLOW_BOT_TOKEN env var or add to macOS Keychain:", file=sys.stderr)
        print("  security add-generic-password -s discord-bot-token -a codeflow -w YOUR_TOKEN", file=sys.stderr)
        sys.exit(1)

    if not CHANNEL_ID or not ALLOWED_USERS:
        print("🔒 Bridge is locked down (fail-closed).", file=sys.stderr)
        print("   Configure BOTH to enable commands:", file=sys.stderr)
        print("   - BRIDGE_CHANNEL_ID (or --channel)", file=sys.stderr)
        print("   - BRIDGE_ALLOWED_USERS (or --users)", file=sys.stderr)

    print(f"🌉 Starting Discord bridge...", flush=True)
    print(f"   Channel: {CHANNEL_ID or '<unset>'}", flush=True)
    print(f"   Allowed users: {', '.join(ALLOWED_USERS) if ALLOWED_USERS else '<unset>'}", flush=True)
    print(f"   Session dir: {SESSION_DIR}", flush=True)

    while True:
        try:
            _ws = websocket.WebSocketApp(
                GATEWAY_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )
            _ws.run_forever()
        except KeyboardInterrupt:
            print("\n🛑 Bridge stopped", flush=True)
            sys.exit(0)
        except Exception as e:
            print(f"[bridge] Connection error: {e}, reconnecting in 5s...", file=sys.stderr, flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()
