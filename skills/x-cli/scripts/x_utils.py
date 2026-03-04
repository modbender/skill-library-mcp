"""
x-cli shared utilities — config loading, client init, output formatting.
"""

import asyncio
import json
import sys
from pathlib import Path
from twikit import Client

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SKILL_DIR / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print("❌ config.json not found. Copy config.example.json → config.json", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


async def get_client(config: dict = None) -> Client:
    if config is None:
        config = load_config()

    proxy = config.get("proxy")
    lang = config.get("language", "en-US")
    client = Client(lang, proxy=proxy) if proxy else Client(lang)

    cookies_path = SKILL_DIR / config.get("cookies_file", "cookies.json")

    if cookies_path.exists():
        client.load_cookies(str(cookies_path))
    elif config.get("x_username") and config.get("x_password"):
        await client.login(
            auth_info_1=config["x_username"],
            auth_info_2=config.get("x_email", config["x_username"]),
            password=config["x_password"],
            cookies_file=str(cookies_path)
        )
    else:
        print("❌ No cookies.json and no login credentials in config.json", file=sys.stderr)
        sys.exit(1)

    return client


def format_tweet(tweet, json_mode=False) -> str:
    # Extract media URLs
    media_urls = []
    if hasattr(tweet, "media") and tweet.media:
        for m in tweet.media:
            url = getattr(m, "media_url_https", None) or getattr(m, "url", None)
            if url:
                media_urls.append({
                    "url": url,
                    "type": getattr(m, "type", "photo"),
                    "alt_text": getattr(m, "ext_alt_text", None),
                })
            # Video: get highest quality variant
            if hasattr(m, "video_info") and m.video_info:
                variants = m.video_info.get("variants", [])
                mp4s = [v for v in variants if v.get("content_type") == "video/mp4"]
                if mp4s:
                    best = max(mp4s, key=lambda v: v.get("bitrate", 0))
                    media_urls.append({"url": best["url"], "type": "video", "alt_text": None})

    # Extract reply context
    reply_to = getattr(tweet, "in_reply_to_tweet_id", None)

    data = {
        "id": tweet.id,
        "user": tweet.user.screen_name if tweet.user else "unknown",
        "name": tweet.user.name if tweet.user else "unknown",
        "text": tweet.text,
        "created_at": str(tweet.created_at) if hasattr(tweet, "created_at") else None,
        "url": f"https://x.com/{tweet.user.screen_name}/status/{tweet.id}" if tweet.user else None,
        "retweet_count": getattr(tweet, "retweet_count", 0),
        "favorite_count": getattr(tweet, "favorite_count", 0),
        "media": media_urls if media_urls else None,
        "reply_to": reply_to,
    }
    if json_mode:
        return json.dumps(data, ensure_ascii=False)

    lines = [
        f"@{data['user']} ({data['name']})",
        f"{data['text']}",
        f"❤️ {data['favorite_count']}  🔁 {data['retweet_count']}  🔗 {data['url']}",
    ]
    if data["created_at"]:
        lines.insert(0, f"📅 {data['created_at']}")
    if reply_to:
        lines.append(f"↩️ Reply to: https://x.com/i/status/{reply_to}")
    if media_urls:
        for m in media_urls:
            emoji = "🖼️" if m["type"] == "photo" else "🎥" if m["type"] == "video" else "📎"
            alt = f' — "{m["alt_text"]}"' if m["alt_text"] else ""
            lines.append(f"{emoji} {m['url']}{alt}")
    return "\n".join(lines)


def run(coro):
    """Run async function."""
    asyncio.run(coro)
