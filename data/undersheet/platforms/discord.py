"""
UnderSheet — Discord platform adapter.
Tracks threads (forum posts, message threads) and feeds (channel messages).
Uses Discord's REST API.

Credentials: ~/.config/undersheet/discord.json
  {
    "bot_token": "Bot YOUR_TOKEN_HERE",
    "guild_id": "YOUR_SERVER_ID"       (optional, for feed/forum scoping)
  }

Permissions required:
  - Read Messages / View Channels
  - Send Messages
  - Read Message History
  - Use Public Threads (for forum channels)
"""

import json
import os
import time
import urllib.request
import urllib.error
from undersheet import PlatformAdapter

DISCORD_API = "https://discord.com/api/v10"
CREDS_PATH  = os.path.expanduser("~/.config/undersheet/discord.json")


def _load_creds() -> dict:
    if not os.path.exists(CREDS_PATH):
        raise FileNotFoundError(
            f"Discord credentials not found at {CREDS_PATH}\n"
            "Create a bot at https://discord.com/developers and add:\n"
            '  {"bot_token": "Bot YOUR_TOKEN", "guild_id": "YOUR_SERVER_ID"}'
        )
    with open(CREDS_PATH) as f:
        return json.load(f)


def _api(method: str, path: str, token: str, body: dict = None) -> dict:
    url = DISCORD_API + path
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "UnderSheet (https://github.com/ubgb/undersheet, 1.0.0)",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            return json.loads(body_text)
        except Exception:
            return {"error": f"HTTP {e.code}: {body_text[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def _get_channel(token: str, channel_id: str) -> dict:
    return _api("GET", f"/channels/{channel_id}", token)


def _get_thread_messages(token: str, thread_id: str, limit: int = 5) -> list:
    r = _api("GET", f"/channels/{thread_id}/messages?limit={limit}", token)
    return r if isinstance(r, list) else []


class Adapter(PlatformAdapter):
    name = "discord"

    def __init__(self):
        self._creds = _load_creds()
        self._token = self._creds["bot_token"]
        self._guild_id = self._creds.get("guild_id")

    def get_credentials(self) -> dict:
        return self._creds

    def get_threads(self, thread_ids: list) -> list:
        """
        Fetch Discord threads/forum posts by channel ID.
        Returns message count approximation via last message ID comparison.
        """
        results = []
        for tid in thread_ids:
            ch = _get_channel(self._token, tid)
            if ch.get("error") or not ch.get("id"):
                continue

            # Get message count proxy: fetch recent messages
            messages = _get_thread_messages(self._token, tid, limit=1)
            # Discord doesn't expose comment_count directly; use message_count field if present
            count = ch.get("message_count", len(messages))

            results.append({
                "id": ch["id"],
                "title": ch.get("name", ch.get("topic", f"Thread {ch['id']}")),
                "url": f"https://discord.com/channels/{ch.get('guild_id', '@me')}/{ch['id']}",
                "comment_count": int(count or 0),
                "score": 0,  # Discord has no upvote system
            })
        return results

    def get_feed(self, limit: int = 25, channel_id: str = None, **kwargs) -> list:
        """
        Fetch recent messages from a channel, or active threads from a guild.
        Pass channel_id for a specific text channel feed.
        Without channel_id, fetches active threads from guild (requires guild_id in config).
        """
        if channel_id:
            return self._channel_feed(channel_id, limit)
        elif self._guild_id:
            return self._active_threads_feed(limit)
        else:
            return []

    def _channel_feed(self, channel_id: str, limit: int) -> list:
        """Recent messages from a text channel as feed items."""
        msgs = _api("GET", f"/channels/{channel_id}/messages?limit={min(limit, 100)}", self._token)
        if not isinstance(msgs, list):
            return []
        results = []
        for m in msgs:
            author = m.get("author", {})
            content = m.get("content", "")
            if not content:
                continue
            results.append({
                "id": m["id"],
                "title": f"{author.get('username', '?')}: {content[:120]}",
                "url": f"https://discord.com/channels/{m.get('guild_id', '@me')}/{channel_id}/{m['id']}",
                "score": 0,
                "created_at": m.get("timestamp", ""),
            })
        return results

    def _active_threads_feed(self, limit: int) -> list:
        """Active threads in a guild as feed items."""
        r = _api("GET", f"/guilds/{self._guild_id}/threads/active", self._token)
        threads = r.get("threads", [])
        results = []
        for t in threads[:limit]:
            results.append({
                "id": t["id"],
                "title": t.get("name", f"Thread {t['id']}"),
                "url": f"https://discord.com/channels/{self._guild_id}/{t['id']}",
                "score": t.get("message_count", 0),
                "created_at": t.get("thread_metadata", {}).get("create_timestamp", ""),
                "comment_count": t.get("message_count", 0),
            })
        return results

    def post_comment(self, thread_id: str, content: str, **kwargs) -> dict:
        """
        Send a message to a Discord channel or thread.
        thread_id is the Discord channel/thread ID.
        """
        r = _api("POST", f"/channels/{thread_id}/messages", self._token, body={"content": content})
        if r.get("id"):
            return {"success": True, "message_id": r["id"]}
        return {"error": r.get("message", r.get("error", "Unknown error"))}
