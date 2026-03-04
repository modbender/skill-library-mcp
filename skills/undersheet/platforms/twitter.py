"""
UnderSheet — Twitter/X platform adapter.
Tracks threads (tweet conversations) and feeds (timeline/search).
Uses Twitter API v2.

Credentials: ~/.config/undersheet/twitter.json
  {
    "bearer_token": "...",           (read-only, required)
    "api_key": "...",                (write access, optional)
    "api_secret": "...",
    "access_token": "...",
    "access_token_secret": "..."
  }

Get credentials at: https://developer.twitter.com/en/portal/dashboard
  - Read: Bearer Token (free tier works)
  - Write: OAuth 1.0a keys (Basic tier required for posting)
"""

import json
import os
import re
import time
import hmac
import hashlib
import base64
import uuid
import urllib.request
import urllib.parse
import urllib.error
from undersheet import PlatformAdapter

TWITTER_API = "https://api.twitter.com/2"
CREDS_PATH  = os.path.expanduser("~/.config/undersheet/twitter.json")


def _load_creds() -> dict:
    if not os.path.exists(CREDS_PATH):
        raise FileNotFoundError(
            f"Twitter credentials not found at {CREDS_PATH}\n"
            "Get a Bearer Token at https://developer.twitter.com\n"
            '  {"bearer_token": "AAA...", "api_key": "...", ...}'
        )
    with open(CREDS_PATH) as f:
        return json.load(f)


def _bearer_get(path: str, bearer_token: str, params: dict = None) -> dict:
    url = TWITTER_API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "UnderSheet/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"errors": [{"detail": e.read().decode()}]}
    except Exception as e:
        return {"errors": [{"detail": str(e)}]}


def _oauth1_header(method: str, url: str, params: dict, creds: dict) -> str:
    """Build OAuth 1.0a Authorization header for write operations."""
    oauth_params = {
        "oauth_consumer_key":     creds["api_key"],
        "oauth_nonce":            uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp":        str(int(time.time())),
        "oauth_token":            creds["access_token"],
        "oauth_version":          "1.0",
    }
    all_params = {**params, **oauth_params}
    sorted_params = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
        for k, v in sorted(all_params.items())
    )
    base_string = "&".join([
        method.upper(),
        urllib.parse.quote(url, safe=""),
        urllib.parse.quote(sorted_params, safe=""),
    ])
    signing_key = (
        urllib.parse.quote(creds["api_secret"], safe="") + "&" +
        urllib.parse.quote(creds["access_token_secret"], safe="")
    )
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()
    oauth_params["oauth_signature"] = signature
    header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(str(v), safe="")}"'
        for k, v in sorted(oauth_params.items())
    )
    return header


def _post_tweet(text: str, reply_to_id: str = None, creds: dict = None) -> dict:
    """Post a tweet via Twitter API v2 with OAuth 1.0a."""
    url = f"{TWITTER_API}/tweets"
    body = {"text": text}
    if reply_to_id:
        body["reply"] = {"in_reply_to_tweet_id": reply_to_id}
    body_bytes = json.dumps(body).encode()
    auth_header = _oauth1_header("POST", url, {}, creds)
    req = urllib.request.Request(url, data=body_bytes, headers={
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "User-Agent": "UnderSheet/1.0",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"errors": [{"detail": e.read().decode()}]}
    except Exception as e:
        return {"errors": [{"detail": str(e)}]}


class Adapter(PlatformAdapter):
    name = "twitter"

    def __init__(self):
        self._creds = _load_creds()
        self._bearer = self._creds["bearer_token"]

    def get_credentials(self) -> dict:
        return self._creds

    def get_threads(self, thread_ids: list) -> list:
        """
        Fetch tweets by ID and their reply counts.
        thread_ids: list of tweet IDs (the root tweet of a conversation).
        """
        if not thread_ids:
            return []
        ids_param = ",".join(thread_ids)
        r = _bearer_get("/tweets", self._bearer, params={
            "ids": ids_param,
            "tweet.fields": "public_metrics,conversation_id,author_id,created_at,text",
            "expansions": "author_id",
            "user.fields": "username",
        })
        results = []
        users = {u["id"]: u["username"] for u in r.get("includes", {}).get("users", [])}
        for tweet in r.get("data", []):
            metrics = tweet.get("public_metrics", {})
            author  = users.get(tweet.get("author_id", ""), "unknown")
            tid     = tweet["id"]
            results.append({
                "id":            tid,
                "title":         tweet.get("text", "")[:100],
                "url":           f"https://x.com/{author}/status/{tid}",
                "comment_count": metrics.get("reply_count", 0),
                "score":         metrics.get("like_count", 0),
            })
        return results

    def get_feed(self, limit: int = 25, query: str = "openclaw lang:en",
                 feed: str = "search", user_id: str = None, **kwargs) -> list:
        """
        Fetch tweets from search or home timeline.
        - feed="search": recent tweets matching `query` (default: openclaw)
        - feed="timeline": home timeline (requires user_id)
        """
        if feed == "timeline" and user_id:
            return self._timeline_feed(user_id, limit)
        return self._search_feed(query, limit)

    def _search_feed(self, query: str, limit: int) -> list:
        r = _bearer_get("/tweets/search/recent", self._bearer, params={
            "query":       query,
            "max_results": min(limit, 100),
            "tweet.fields": "public_metrics,author_id,created_at",
            "expansions": "author_id",
            "user.fields": "username",
        })
        users = {u["id"]: u["username"] for u in r.get("includes", {}).get("users", [])}
        results = []
        for tweet in r.get("data", []):
            metrics = tweet.get("public_metrics", {})
            author  = users.get(tweet.get("author_id", ""), "unknown")
            tid     = tweet["id"]
            results.append({
                "id":         tid,
                "title":      tweet.get("text", "")[:120],
                "url":        f"https://x.com/{author}/status/{tid}",
                "score":      metrics.get("like_count", 0),
                "created_at": tweet.get("created_at", ""),
                "comment_count": metrics.get("reply_count", 0),
            })
        return results

    def _timeline_feed(self, user_id: str, limit: int) -> list:
        r = _bearer_get(f"/users/{user_id}/timelines/reverse_chronological",
                        self._bearer, params={
            "max_results":  min(limit, 100),
            "tweet.fields": "public_metrics,author_id,created_at",
            "expansions": "author_id",
            "user.fields": "username",
        })
        users = {u["id"]: u["username"] for u in r.get("includes", {}).get("users", [])}
        results = []
        for tweet in r.get("data", []):
            metrics = tweet.get("public_metrics", {})
            author  = users.get(tweet.get("author_id", ""), "unknown")
            tid     = tweet["id"]
            results.append({
                "id":         tid,
                "title":      tweet.get("text", "")[:120],
                "url":        f"https://x.com/{author}/status/{tid}",
                "score":      metrics.get("like_count", 0),
                "created_at": tweet.get("created_at", ""),
            })
        return results

    def post_comment(self, thread_id: str, content: str, **kwargs) -> dict:
        """
        Post a reply to a tweet. Requires OAuth 1.0a keys (write access).
        thread_id: the tweet ID to reply to.
        """
        required = ("api_key", "api_secret", "access_token", "access_token_secret")
        if not all(k in self._creds for k in required):
            return {
                "error": "Write access requires OAuth 1.0a keys in twitter.json. "
                         "See https://developer.twitter.com (Basic tier)."
            }
        result = _post_tweet(content, reply_to_id=thread_id, creds=self._creds)
        if result.get("data", {}).get("id"):
            return {"success": True, "tweet_id": result["data"]["id"]}
        return {"error": result.get("errors", [{}])[0].get("detail", "Unknown error")}
