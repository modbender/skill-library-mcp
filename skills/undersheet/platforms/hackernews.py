"""
UnderSheet — Hacker News platform adapter.
Uses the public HN Algolia API (no auth needed for reading).
For posting comments, credentials required.
Credentials: ~/.config/undersheet/hackernews.json
  { "username": "...", "password": "..." }
"""

import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error
from undersheet import PlatformAdapter

HN_API       = "https://hacker-news.firebaseio.com/v0"
HN_ALGOLIA   = "https://hn.algolia.com/api/v1"
HN_BASE      = "https://news.ycombinator.com"
CREDS_PATH   = os.path.expanduser("~/.config/undersheet/hackernews.json")
COOKIES_PATH = os.path.expanduser("~/.config/undersheet/hn_cookies.txt")


def _fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": "undersheet/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def _load_creds() -> dict:
    if os.path.exists(CREDS_PATH):
        with open(CREDS_PATH) as f:
            return json.load(f)
    return {}


class Adapter(PlatformAdapter):
    name = "hackernews"

    def get_credentials(self) -> dict:
        return _load_creds()

    def get_threads(self, thread_ids: list) -> list:
        """Fetch HN items by ID."""
        results = []
        for tid in thread_ids:
            try:
                item = _fetch(f"{HN_API}/item/{tid}.json")
                if item:
                    results.append({
                        "id": str(item.get("id", tid)),
                        "title": item.get("title", item.get("text", "")[:80]),
                        "url": f"https://news.ycombinator.com/item?id={item.get('id', tid)}",
                        "comment_count": item.get("descendants", 0),
                        "score": item.get("score", 0),
                    })
            except Exception:
                pass
        return results

    def get_feed(self, limit: int = 25, feed: str = "topstories", **kwargs) -> list:
        """
        Fetch HN feed. feed can be: topstories, newstories, beststories, askstories, showstories
        """
        try:
            ids = _fetch(f"{HN_API}/{feed}.json")[:50]
        except Exception:
            return []

        results = []
        for item_id in ids:
            if len(results) >= limit:
                break
            try:
                item = _fetch(f"{HN_API}/item/{item_id}.json")
                if not item or item.get("dead") or item.get("deleted"):
                    continue
                url = item.get("url", f"https://news.ycombinator.com/item?id={item_id}")
                results.append({
                    "id": str(item.get("id", item_id)),
                    "title": item.get("title", ""),
                    "url": url,
                    "score": item.get("score", 0),
                    "created_at": str(item.get("time", "")),
                    "comment_count": item.get("descendants", 0),
                })
            except Exception:
                continue
        return results

    def post_comment(self, thread_id: str, content: str, **kwargs) -> dict:
        """
        Post a comment to an HN item. Requires valid session cookies.
        Loads cookies from COOKIES_PATH or logs in fresh if credentials are available.
        """
        import http.cookiejar
        import urllib.request

        creds = _load_creds()
        if not creds.get("username") or not creds.get("password"):
            return {"error": "HN credentials not configured. See ~/.config/undersheet/hackernews.json"}

        # Build cookie jar
        cj = http.cookiejar.MozillaCookieJar()
        if os.path.exists(COOKIES_PATH):
            try:
                cj.load(COOKIES_PATH, ignore_discard=True, ignore_expires=True)
            except Exception:
                pass

        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        urllib.request.install_opener(opener)

        # Log in if needed
        def _logged_in() -> bool:
            r = opener.open(f"{HN_BASE}/news", timeout=10)
            content = r.read().decode()
            return creds["username"].lower() in content.lower()

        if not _logged_in():
            data = urllib.parse.urlencode({
                "acct": creds["username"],
                "pw": creds["password"],
                "goto": "news"
            }).encode()
            opener.open(f"{HN_BASE}/login", data, timeout=10)
            os.makedirs(os.path.dirname(COOKIES_PATH), exist_ok=True)
            cj.save(COOKIES_PATH, ignore_discard=True, ignore_expires=True)

        # Get item page for hmac token
        page = opener.open(f"{HN_BASE}/item?id={thread_id}", timeout=10).read().decode()
        hmac_match = re.search(r'name="hmac" value="([^"]+)"', page)
        if not hmac_match:
            return {"error": "Could not find comment hmac token. Not logged in?"}

        hmac = hmac_match.group(1)
        data = urllib.parse.urlencode({
            "parent": thread_id,
            "goto": f"item?id={thread_id}",
            "hmac": hmac,
            "text": content,
        }).encode()

        try:
            resp = opener.open(f"{HN_BASE}/comment", data, timeout=10)
            final_url = resp.geturl()
            if f"item?id={thread_id}" in final_url:
                return {"success": True, "url": final_url}
            return {"error": f"Unexpected redirect: {final_url}"}
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
