#!/usr/bin/env python3
"""
X Tweet Fetcher - Fetch tweets from X/Twitter without login or API keys.
Uses FxTwitter API only. Zero dependencies, zero configuration.
"""

import json
import re
import sys
import argparse
import urllib.request
import urllib.error
from typing import Optional, Dict, Any


def parse_tweet_url(url: str) -> tuple:
    """Extract username and tweet_id from X/Twitter URL."""
    patterns = [
        r'(?:x\.com|twitter\.com)/(\w+)/status/(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2)
    raise ValueError(f"Cannot parse tweet URL: {url}")


def fetch_tweet(url: str) -> Dict[str, Any]:
    """Fetch tweet text, stats, quotes, and full article content via FxTwitter API."""
    username, tweet_id = parse_tweet_url(url)
    result = {"url": url, "username": username, "tweet_id": tweet_id}

    api_url = f"https://api.fxtwitter.com/{username}/status/{tweet_id}"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        if data.get("code") != 200:
            result["error"] = f"FxTwitter returned code {data.get('code')}: {data.get('message', 'Unknown')}"
            return result

        tweet = data["tweet"]
        tweet_data = {
            "text": tweet.get("text", ""),
            "author": tweet.get("author", {}).get("name", ""),
            "screen_name": tweet.get("author", {}).get("screen_name", ""),
            "likes": tweet.get("likes", 0),
            "retweets": tweet.get("retweets", 0),
            "bookmarks": tweet.get("bookmarks", 0),
            "views": tweet.get("views", 0),
            "replies_count": tweet.get("replies", 0),
            "created_at": tweet.get("created_at", ""),
            "is_note_tweet": tweet.get("is_note_tweet", False),
            "lang": tweet.get("lang", ""),
        }

        # Include quote tweet if present
        if tweet.get("quote"):
            qt = tweet["quote"]
            tweet_data["quote"] = {
                "text": qt.get("text", ""),
                "author": qt.get("author", {}).get("name", ""),
                "screen_name": qt.get("author", {}).get("screen_name", ""),
                "likes": qt.get("likes", 0),
                "retweets": qt.get("retweets", 0),
                "views": qt.get("views", 0),
            }

        # Extract X Article (long-form content) if present
        article = tweet.get("article")
        if article:
            article_data = {
                "title": article.get("title", ""),
                "preview_text": article.get("preview_text", ""),
                "created_at": article.get("created_at", ""),
            }
            content = article.get("content", {})
            blocks = content.get("blocks", [])
            if blocks:
                full_text = "\n\n".join(
                    b.get("text", "") for b in blocks if b.get("text", "")
                )
                article_data["full_text"] = full_text
                article_data["word_count"] = len(full_text.split())
                article_data["char_count"] = len(full_text)
            tweet_data["article"] = article_data
            tweet_data["is_article"] = True
        else:
            tweet_data["is_article"] = False

        result["tweet"] = tweet_data

    except urllib.error.HTTPError as e:
        result["error"] = f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Fetch tweets from X/Twitter without login or API keys"
    )
    parser.add_argument("--url", "-u", required=True, help="Tweet URL (x.com or twitter.com)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print JSON")
    parser.add_argument("--text-only", "-t", action="store_true", help="Print only tweet text (or article full text)")
    parser.add_argument("--replies", "-r", action="store_true", help="Fetch tweet replies/comments (requires browser automation - not yet implemented)")

    args = parser.parse_args()

    if args.replies:
        print(json.dumps({
            "error": "Reply fetching not currently supported",
            "reason": "FxTwitter API does not provide reply content. Reply fetching would require browser automation dependencies (Camofox/Nitter) which were removed to maintain zero-dependency architecture.",
            "workaround": "The tweet's reply count is included in the standard output as 'replies_count'",
            "future": "This feature may be re-implemented as an optional dependency in a future version"
        }, indent=2 if args.pretty else None), file=sys.stderr)
        sys.exit(1)

    result = fetch_tweet(args.url)

    if args.text_only:
        tweet = result.get("tweet", {})
        if tweet.get("is_article") and tweet.get("article", {}).get("full_text"):
            article = tweet["article"]
            print(f"# {article['title']}\n")
            print(f"By @{tweet['screen_name']} | {tweet.get('created_at', '')}")
            print(f"Likes: {tweet['likes']} | Retweets: {tweet['retweets']} | Views: {tweet['views']}")
            print(f"Words: {article['word_count']}\n")
            print(article["full_text"])
        elif tweet.get("text"):
            print(f"@{tweet['screen_name']}: {tweet['text']}")
            print(f"\nLikes: {tweet['likes']} | Retweets: {tweet['retweets']} | Views: {tweet['views']}")
        elif result.get("error"):
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
    else:
        indent = 2 if args.pretty else None
        print(json.dumps(result, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
