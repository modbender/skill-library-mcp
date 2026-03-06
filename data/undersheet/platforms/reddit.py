"""
UnderSheet — Reddit platform adapter.
Uses Reddit's JSON API (read) and OAuth for posting.
Credentials: ~/.config/undersheet/reddit.json
  {
    "client_id": "...",
    "client_secret": "...",
    "username": "...",
    "password": "...",
    "user_agent": "undersheet:v1.0 (by /u/yourusername)"
  }
"""

import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error
import base64
from undersheet import PlatformAdapter

REDDIT_API  = "https://oauth.reddit.com"
REDDIT_AUTH = "https://www.reddit.com/api/v1/access_token"
CREDS_PATH  = os.path.expanduser("~/.config/undersheet/reddit.json")
TOKEN_PATH  = os.path.expanduser("~/.config/undersheet/reddit_token.json")


def _load_creds() -> dict:
    if os.path.exists(CREDS_PATH):
        with open(CREDS_PATH) as f:
            return json.load(f)
    return {}


def _get_token(creds: dict) -> str:
    """Get or refresh OAuth token."""
    # Check cached token
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH) as f:
            cached = json.load(f)
        if cached.get("expires_at", 0) > time.time() + 60:
            return cached["access_token"]

    auth = base64.b64encode(
        f"{creds['client_id']}:{creds['client_secret']}".encode()
    ).decode()
    data = urllib.parse.urlencode({
        "grant_type": "password",
        "username": creds["username"],
        "password": creds["password"],
    }).encode()
    req = urllib.request.Request(
        REDDIT_AUTH,
        data=data,
        headers={
            "Authorization": f"Basic {auth}",
            "User-Agent": creds.get("user_agent", "undersheet/1.0"),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        token_data = json.loads(resp.read().decode())

    token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600) - 60
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        json.dump(token_data, f)

    return token_data["access_token"]


def _api(method: str, path: str, token: str, user_agent: str, body: dict = None) -> dict:
    url = REDDIT_API + path
    data = urllib.parse.urlencode(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "body": e.read().decode()}


class Adapter(PlatformAdapter):
    name = "reddit"

    def __init__(self):
        self._creds = _load_creds()
        if not self._creds:
            raise FileNotFoundError(
                f"Reddit credentials not configured. See {CREDS_PATH}"
            )
        self._ua = self._creds.get("user_agent", "undersheet/1.0")

    def get_credentials(self) -> dict:
        return self._creds

    def _token(self) -> str:
        if not self._creds:
            raise ValueError("Reddit credentials not configured. See ~/.config/undersheet/reddit.json")
        return _get_token(self._creds)

    def get_threads(self, thread_ids: list) -> list:
        """Fetch Reddit threads by full ID (e.g. t3_abc123) or URL."""
        results = []
        token = self._token()
        for tid in thread_ids:
            # Accept both full ID (t3_xxx) and short ID (xxx)
            full_id = tid if tid.startswith("t3_") else f"t3_{tid}"
            r = _api("GET", f"/api/info?id={full_id}", token, self._ua)
            children = r.get("data", {}).get("children", [])
            if children:
                d = children[0].get("data", {})
                results.append({
                    "id": d.get("id", tid),
                    "title": d.get("title", ""),
                    "url": f"https://reddit.com{d.get('permalink', '')}",
                    "comment_count": d.get("num_comments", 0),
                    "score": d.get("score", 0),
                })
        return results

    def get_feed(self, limit: int = 25, subreddit: str = "all", sort: str = "hot", **kwargs) -> list:
        token = self._token()
        r = _api("GET", f"/r/{subreddit}/{sort}?limit={limit}", token, self._ua)
        posts = r.get("data", {}).get("children", [])
        results = []
        for p in posts:
            d = p.get("data", {})
            results.append({
                "id": d.get("id", ""),
                "title": d.get("title", ""),
                "url": f"https://reddit.com{d.get('permalink', '')}",
                "score": d.get("score", 0),
                "created_at": str(d.get("created_utc", "")),
                "comment_count": d.get("num_comments", 0),
            })
        return results

    def post_comment(self, thread_id: str, content: str, **kwargs) -> dict:
        """Post a comment (reply to a thread or comment)."""
        token = self._token()
        full_id = thread_id if thread_id.startswith("t") else f"t3_{thread_id}"
        r = _api("POST", "/api/comment", token, self._ua, body={
            "thing_id": full_id,
            "text": content,
            "api_type": "json",
        })
        errors = r.get("json", {}).get("errors", [])
        if errors:
            return {"error": errors}
        return {"success": True, "data": r.get("json", {}).get("data", {})}
