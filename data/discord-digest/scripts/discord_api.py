#!/usr/bin/env python3
"""Discord API client using user token (HTTP requests only)."""

import json
import sys
import time
import urllib.request
import urllib.error
from typing import Optional

API_BASE = "https://discord.com/api/v10"
RATE_LIMIT_DELAY = 1.0  # seconds between requests to avoid rate limits


def _headers(token: str) -> dict:
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }


def _request(token: str, endpoint: str, max_retries: int = 3) -> Optional[dict]:
    """Make authenticated request to Discord API with rate limit handling."""
    url = f"{API_BASE}{endpoint}"
    headers = _headers(token)
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                time.sleep(RATE_LIMIT_DELAY)
                return data
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                retry_after = json.loads(e.read().decode()).get("retry_after", 5)
                print(f"Rate limited, waiting {retry_after}s...", file=sys.stderr)
                time.sleep(retry_after + 0.5)
                continue
            elif e.code == 401:
                return {"error": "unauthorized", "code": 401}
            elif e.code == 403:
                return {"error": "forbidden", "code": 403}
            else:
                print(f"HTTP {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
                return None
        except Exception as e:
            print(f"Request error: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
    return None


def validate_token(token: str) -> dict:
    """Validate token and return user info or error."""
    result = _request(token, "/users/@me")
    if result and "error" not in result:
        return {"valid": True, "username": result.get("username"), "id": result.get("id"),
                "global_name": result.get("global_name")}
    return {"valid": False, "error": result.get("error", "unknown") if result else "no_response"}


def get_guilds(token: str) -> list:
    """Get all guilds (servers) the user is in."""
    result = _request(token, "/users/@me/guilds?limit=200")
    if result and isinstance(result, list):
        return [{"id": g["id"], "name": g["name"], "icon": g.get("icon")} for g in result]
    return []


def get_channels(token: str, guild_id: str) -> list:
    """Get all channels in a guild, organized by category."""
    result = _request(token, f"/guilds/{guild_id}/channels")
    if not result or not isinstance(result, list):
        return []

    # Separate categories and channels
    categories = {c["id"]: c["name"] for c in result if c["type"] == 4}
    channels = []

    for ch in result:
        if ch["type"] in (0, 5, 15):  # text, announcement, forum
            cat_name = categories.get(ch.get("parent_id", ""), "No Category")
            channels.append({
                "id": ch["id"],
                "name": ch["name"],
                "type": {0: "text", 5: "announcement", 15: "forum"}.get(ch["type"], "other"),
                "category": cat_name,
                "position": ch.get("position", 0)
            })

    channels.sort(key=lambda x: (x["category"], x["position"]))
    return channels


def get_threads(token: str, channel_id: str) -> list:
    """Get active threads in a channel."""
    result = _request(token, f"/channels/{channel_id}/threads/archived/public?limit=50")
    threads = []
    if result and "threads" in result:
        for t in result["threads"]:
            threads.append({
                "id": t["id"],
                "name": t["name"],
                "parent_id": t.get("parent_id"),
                "message_count": t.get("message_count", 0)
            })

    # Also get active threads from guild
    result2 = _request(token, f"/channels/{channel_id}/threads/active")
    # Note: active threads endpoint is on guild, not channel
    # We'll handle this in the scanner

    return threads


def get_guild_active_threads(token: str, guild_id: str) -> list:
    """Get all active threads in a guild."""
    result = _request(token, f"/guilds/{guild_id}/threads/active")
    if result and "threads" in result:
        return [{"id": t["id"], "name": t["name"], "parent_id": t.get("parent_id"),
                 "message_count": t.get("message_count", 0)} for t in result["threads"]]
    return []


def get_messages(token: str, channel_id: str, limit: int = 100, after: str = None) -> list:
    """Get messages from a channel/thread."""
    endpoint = f"/channels/{channel_id}/messages?limit={min(limit, 100)}"
    if after:
        endpoint += f"&after={after}"

    result = _request(token, endpoint)
    if result and isinstance(result, list):
        return result
    return []


def get_messages_since(token: str, channel_id: str, hours: int = 24) -> list:
    """Get all messages from last N hours."""
    cutoff = time.time() - (hours * 3600)
    # Discord snowflake: (timestamp_ms - DISCORD_EPOCH) << 22
    DISCORD_EPOCH = 1420070400000
    cutoff_snowflake = str(int(cutoff * 1000 - DISCORD_EPOCH) << 22)

    all_messages = []
    after = cutoff_snowflake

    while True:
        msgs = get_messages(token, channel_id, limit=100, after=after)
        if not msgs:
            break
        all_messages.extend(msgs)
        if len(msgs) < 100:
            break
        # Messages come newest first when using 'after', get the latest id
        after = msgs[0]["id"]
        time.sleep(0.5)

    return all_messages


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: discord_api.py <token> <action> [args...]")
        print("Actions: validate, guilds, channels <guild_id>, messages <channel_id> [hours]")
        sys.exit(1)

    token = sys.argv[1]
    action = sys.argv[2]

    if action == "validate":
        print(json.dumps(validate_token(token), indent=2))
    elif action == "guilds":
        print(json.dumps(get_guilds(token), indent=2))
    elif action == "channels" and len(sys.argv) > 3:
        print(json.dumps(get_channels(token, sys.argv[3]), indent=2))
    elif action == "threads" and len(sys.argv) > 3:
        print(json.dumps(get_guild_active_threads(token, sys.argv[3]), indent=2))
    elif action == "messages" and len(sys.argv) > 3:
        hours = int(sys.argv[4]) if len(sys.argv) > 4 else 24
        msgs = get_messages_since(token, sys.argv[3], hours)
        print(json.dumps(msgs, indent=2, ensure_ascii=False))
    else:
        print("Unknown action or missing args")
        sys.exit(1)
