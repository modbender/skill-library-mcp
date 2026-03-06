"""Discord webhook adapter for posting relay messages."""

import json
import os
import subprocess
import time

webhook_url = os.environ.get("WEBHOOK_URL", "")
agent_name = os.environ.get("AGENT_NAME", "Claude Code")
thread_mode = os.environ.get("THREAD_MODE", "false").lower() == "true"

# Thread state: first post creates the thread, subsequent posts go into it
_thread_id = None


def _curl_post(url, payload, headers=None):
    """Post JSON via curl and return parsed response."""
    cmd = ["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    if headers:
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=10, text=True)
        if result.stdout:
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError):
        pass
    return {}


def _create_thread_via_webhook(first_msg, name):
    """Create a thread by posting the first message, then starting a thread on it."""
    global _thread_id

    # Step 1: Post the first message normally (with ?wait=true to get message ID)
    payload = {"content": first_msg, "username": name or agent_name}
    resp = _curl_post(f"{webhook_url}?wait=true", payload)
    msg_id = resp.get("id")
    channel_id = resp.get("channel_id")

    if not msg_id or not channel_id:
        return  # Fall back to no-thread mode

    # Step 2: Create a thread from that message using the bot token
    bot_token = os.environ.get("BOT_TOKEN", "")
    if not bot_token:
        # No bot token — can't create threads. Thread mode silently degrades.
        return

    thread_name = f"{agent_name} — {time.strftime('%H:%M')}"
    thread_resp = _curl_post(
        f"https://discord.com/api/v10/channels/{channel_id}/messages/{msg_id}/threads",
        {"name": thread_name, "auto_archive_duration": 1440},
        headers={"Authorization": f"Bot {bot_token}"}
    )
    _thread_id = thread_resp.get("id")


def post(msg, name=None):
    """Post a message to Discord via webhook.

    In thread mode, the first message creates a thread (via bot API),
    and all subsequent messages are posted into that thread.
    """
    global _thread_id

    if not webhook_url:
        return

    if len(msg) > 1900:
        msg = msg[:1900] + "\u2026*(truncated)*"

    # Thread mode: create thread on first post
    if thread_mode and _thread_id is None:
        _create_thread_via_webhook(msg, name)
        if _thread_id:
            return  # First message already posted as part of thread creation
        # If thread creation failed, fall through to normal post

    # Post into thread or main channel
    url = f"{webhook_url}?thread_id={_thread_id}" if _thread_id else webhook_url
    payload = {"content": msg, "username": name or agent_name}

    try:
        subprocess.run(
            ["curl", "-s", "-X", "POST", url,
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, timeout=10, text=True
        )
    except (subprocess.TimeoutExpired, OSError):
        pass
