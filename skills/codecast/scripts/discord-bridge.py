#!/usr/bin/env python3
"""Discord → stdin bridge for codecast sessions.

Connects to Discord gateway, watches a configured channel for messages from
allowed users, and forwards them to active codecast agent sessions via stdin.

Runs as a companion process alongside dev-relay.sh.

Usage:
    python3 discord-bridge.py [--channel CHANNEL_ID] [--users USER_ID,...] [--verbose]

Environment:
    CODECAST_BOT_TOKEN   Discord bot token (or macOS Keychain: discord-bot-token/codecast)
    BRIDGE_CHANNEL_ID    Discord channel ID to watch
    BRIDGE_ALLOWED_USERS Comma-separated Discord user IDs (empty = all users)

Commands (from Discord):
    !status   Show active codecast sessions
    !kill     Kill a session:  !kill <PID>
    !log      Show recent output:  !log [PID]
    !send     Forward text to agent stdin:  !send [PID] <message>
    (default) If only one session active, plain messages forwarded to it

Session data read from: /tmp/dev-relay-sessions/<PID>.json
"""

import json
import os
import signal
import subprocess
import sys
import threading
import time
import websocket  # pip install websocket-client

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SESSION_DIR = "/tmp/dev-relay-sessions"


def get_bot_token():
    """Get bot token from env, keychain, or file."""
    token = os.environ.get("CODECAST_BOT_TOKEN", "")
    if token:
        return token
    # Try macOS Keychain
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "discord-bot-token", "-a", "codecast", "-w"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        pass
    # Try file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(script_dir, ".bot-token")
    if os.path.exists(token_file):
        with open(token_file) as f:
            return f.read().strip()
    return ""


BOT_TOKEN = get_bot_token()
CHANNEL_ID = os.environ.get("BRIDGE_CHANNEL_ID", "")
ALLOWED_USERS = set(filter(None, os.environ.get("BRIDGE_ALLOWED_USERS", "").split(",")))
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv

# Parse CLI args
for i, arg in enumerate(sys.argv[1:], 1):
    if arg == "--channel" and i < len(sys.argv) - 1:
        CHANNEL_ID = sys.argv[i + 1]
    elif arg == "--users" and i < len(sys.argv) - 1:
        ALLOWED_USERS = set(filter(None, sys.argv[i + 1].split(",")))


def log(msg):
    if VERBOSE:
        print(f"[bridge] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

def get_active_sessions():
    """Read active codecast sessions from /tmp/dev-relay-sessions/."""
    sessions = {}
    if not os.path.isdir(SESSION_DIR):
        return sessions
    for fname in os.listdir(SESSION_DIR):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(SESSION_DIR, fname)
        try:
            with open(fpath) as f:
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


def send_to_stdin(pid, message):
    """Send a message to an agent's stdin via /proc or write pipe."""
    # Try writing to /proc/<pid>/fd/0 (Linux) or use process:submit pattern
    # Most reliable: write to the relay dir's input fifo if it exists
    sessions = get_active_sessions()
    session = sessions.get(str(pid))
    if not session:
        return False, "Session not found"

    relay_dir = session.get("relayDir", "")
    input_pipe = os.path.join(relay_dir, "input.pipe") if relay_dir else ""

    # Try named pipe first
    if input_pipe and os.path.exists(input_pipe):
        try:
            with open(input_pipe, "w") as f:
                f.write(message + "\n")
            return True, "Sent via pipe"
        except OSError as e:
            return False, f"Pipe error: {e}"

    # Fallback: try /proc fd (Linux only)
    stdin_path = f"/proc/{pid}/fd/0"
    if os.path.exists(stdin_path):
        try:
            with open(stdin_path, "w") as f:
                f.write(message + "\n")
            return True, "Sent via /proc"
        except OSError as e:
            return False, f"/proc error: {e}"

    return False, "No input method available (pipe or /proc)"


def kill_session(pid):
    """Kill a codecast session."""
    try:
        pid = int(pid)
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
        return True, f"Session {pid} terminated"
    except (ValueError, OSError) as e:
        return False, f"Failed to kill {pid}: {e}"


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
            with open(stream_path) as f:
                lines = f.readlines()
            # Get last 5 events
            recent = lines[-5:] if len(lines) > 5 else lines
            entries = []
            for line in recent:
                try:
                    evt = json.loads(line.strip())
                    etype = evt.get("type", "?")
                    entries.append(f"[{etype}]")
                except json.JSONDecodeError:
                    pass
            return "\n".join(entries), None
        except OSError:
            pass

    # Fallback to output.log
    output_path = os.path.join(relay_dir, "output.log")
    if os.path.exists(output_path):
        try:
            with open(output_path) as f:
                content = f.read()
            return content[-500:] if len(content) > 500 else content, None
        except OSError:
            pass

    return None, "No log files found"


# ---------------------------------------------------------------------------
# Discord API helper
# ---------------------------------------------------------------------------

def discord_api_post(endpoint, payload):
    """POST to Discord REST API."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST",
             f"https://discord.com/api/v10{endpoint}",
             "-H", f"Authorization: Bot {BOT_TOKEN}",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout:
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError):
        pass
    return {}


def reply(channel_id, content):
    """Send a reply message to the Discord channel."""
    content = content[:1900]
    discord_api_post(f"/channels/{channel_id}/messages", {"content": content})


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

    # --- Command: !status ---
    if content.lower() == "!status":
        sessions = get_active_sessions()
        if not sessions:
            reply(channel_id, "📭 No active codecast sessions")
            return
        lines = ["📡 **Active Sessions:**"]
        for pid, s in sessions.items():
            agent = s.get("agent", "?")
            workdir = s.get("workdir", "?")
            start = s.get("startTime", "?")
            lines.append(f"  `{pid}` — {agent} | `{workdir}` | {start}")
        reply(channel_id, "\n".join(lines))
        return

    # --- Command: !kill <PID> ---
    if content.lower().startswith("!kill"):
        parts = content.split()
        if len(parts) < 2:
            reply(channel_id, "Usage: `!kill <PID>`")
            return
        ok, msg = kill_session(parts[1])
        reply(channel_id, f"{'✅' if ok else '❌'} {msg}")
        return

    # --- Command: !log [PID] ---
    if content.lower().startswith("!log"):
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
            reply(channel_id, f"📜 Recent log for `{pid}`:\n```\n{log_content}\n```")
        return

    # --- Command: !send [PID] <message> ---
    if content.lower().startswith("!send"):
        parts = content.split(None, 2)
        sessions = get_active_sessions()
        if len(parts) >= 3:
            pid, message = parts[1], parts[2]
        elif len(parts) == 2 and len(sessions) == 1:
            pid = list(sessions.keys())[0]
            message = parts[1]
        else:
            reply(channel_id, "Usage: `!send [PID] <message>`")
            return
        ok, msg = send_to_stdin(pid, message)
        reply(channel_id, f"{'✅' if ok else '❌'} {msg}")
        return

    # --- Default: forward plain message to sole active session ---
    sessions = get_active_sessions()
    if len(sessions) == 1:
        pid = list(sessions.keys())[0]
        ok, msg = send_to_stdin(pid, content)
        if ok:
            reply(channel_id, f"📨 Forwarded to session `{pid}`")
        else:
            reply(channel_id, f"⚠️ {msg}")


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
                    "browser": "codecast-bridge",
                    "device": "codecast-bridge",
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
        print("  Set CODECAST_BOT_TOKEN env var or add to macOS Keychain:", file=sys.stderr)
        print("  security add-generic-password -s discord-bot-token -a codecast -w YOUR_TOKEN", file=sys.stderr)
        sys.exit(1)

    if not CHANNEL_ID:
        print("⚠️  Warning: No BRIDGE_CHANNEL_ID set — listening on all channels", file=sys.stderr)

    print(f"🌉 Starting Discord bridge...", flush=True)
    print(f"   Channel: {CHANNEL_ID or 'all'}", flush=True)
    print(f"   Allowed users: {', '.join(ALLOWED_USERS) if ALLOWED_USERS else 'all'}", flush=True)
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
