"""
FxTwitter API wrapper — Tier 1 (FREE) retrieval for Muninn's ravens.
Uses api.fxtwitter.com which requires no authentication.
# 🐾 silent paws padding through the API
"""

import urllib.request
import urllib.parse
import json
import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

log = logging.getLogger(__name__)

FXTWITTER_BASE = "https://api.fxtwitter.com"

# 🐾 the raven lands softly


@dataclass
class Tweet:
    """Normalised tweet object."""
    id: str
    text: str
    author: str
    author_name: str = ""
    created_at: str = ""
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    quotes: int = 0
    views: int = 0
    url: str = ""
    media_urls: list = field(default_factory=list)
    is_retweet: bool = False

    @property
    def engagement(self) -> int:
        return self.likes + self.retweets * 2 + self.replies + self.quotes

    def to_dict(self) -> dict:
        return {
            "id": self.id, "text": self.text, "author": self.author,
            "author_name": self.author_name, "created_at": self.created_at,
            "likes": self.likes, "retweets": self.retweets,
            "replies": self.replies, "quotes": self.quotes, "views": self.views,
            "url": self.url, "engagement": self.engagement,
            "is_retweet": self.is_retweet,
        }


def _get(path: str, timeout: int = 10) -> Optional[dict]:
    """Raw GET against FxTwitter API. 🐾"""
    url = f"{FXTWITTER_BASE}{path}"
    log.debug(f"FxTwitter GET {url}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "MuninnRaven/1.0",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        log.warning(f"FxTwitter request failed: {e}")
        return None


def lookup_tweet(username: str, tweet_id: str) -> Optional[Tweet]:
    """Look up a single tweet by username/id. 🐾"""
    data = _get(f"/{username}/status/{tweet_id}")
    if not data or data.get("code") != 200:
        return None
    return _parse_tweet(data.get("tweet", {}))


def lookup_user_tweets(username: str) -> list[Tweet]:
    """Fetch recent tweets for a user (if supported by fxtwitter). 🐾"""
    # FxTwitter doesn't have a timeline endpoint, but we try the search path
    data = _get(f"/{username}")
    if not data or data.get("code") != 200:
        return []
    # Single tweet response from user profile
    if "tweet" in data:
        t = _parse_tweet(data["tweet"])
        return [t] if t else []
    return []


def search_tweets(query: str) -> list[Tweet]:
    """
    FxTwitter search endpoint (experimental).
    Falls back gracefully if unavailable. 🐾
    """
    encoded = urllib.parse.quote(query)
    data = _get(f"/search?q={encoded}")
    if not data:
        return []
    tweets = []
    for item in data.get("tweets", data.get("results", [])):
        t = _parse_tweet(item)
        if t:
            tweets.append(t)
    return tweets


def _parse_tweet(raw: dict) -> Optional[Tweet]:
    """Parse raw FxTwitter tweet JSON into Tweet. 🐾"""
    if not raw or not raw.get("id"):
        return None

    author = raw.get("author", {})
    text = raw.get("text", "")
    is_rt = text.startswith("RT @")

    media_urls = []
    for m in raw.get("media", {}).get("all", []):
        if "url" in m:
            media_urls.append(m["url"])

    return Tweet(
        id=str(raw["id"]),
        text=text,
        author=author.get("screen_name", raw.get("author_screen_name", "")),
        author_name=author.get("name", ""),
        created_at=raw.get("created_at", ""),
        likes=raw.get("likes", 0),
        retweets=raw.get("retweets", 0),
        replies=raw.get("replies", 0),
        quotes=raw.get("quotes", 0),
        views=raw.get("views", 0),
        url=raw.get("url", f"https://x.com/{author.get('screen_name','_')}/status/{raw['id']}"),
        media_urls=media_urls,
        is_retweet=is_rt,
    )
