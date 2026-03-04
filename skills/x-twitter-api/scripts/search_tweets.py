#!/usr/bin/env python3
"""
X (Twitter) Tweet Search Script
Search recent tweets using X API v2
"""
import os
import sys
import json
import argparse
import requests
from datetime import datetime


class XTwitterAPI:
    """X (Twitter) API v2 Client"""

    def __init__(self, bearer_token=None):
        self.bearer_token = bearer_token or os.environ.get('X_BEARER_TOKEN')
        self.base_url = "https://api.x.com/2"

        if not self.bearer_token:
            raise ValueError("Bearer Token not found. Set X_BEARER_TOKEN environment variable")

        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

    def search_recent(self, query, max_results=10):
        """Search recent tweets (last 7 days)"""
        url = f"{self.base_url}/tweets/search/recent"

        fields = [
            "created_at", "public_metrics", "author_id",
            "entities", "lang", "referenced_tweets"
        ]

        params = {
            "query": query,
            "max_results": min(max_results, 100),
            "tweet.fields": ",".join(fields),
            "expansions": "author_id",
            "user.fields": "username,name,verified,public_metrics"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            if 'response' in locals():
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
            return None


def format_tweet(tweet, users_map=None):
    """Format tweet for display"""
    if not isinstance(tweet, dict):
        return str(tweet)

    text = tweet.get("text", "")
    created_at = tweet.get("created_at", "")
    metrics = tweet.get("public_metrics", {})

    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        time_str = created_at

    author_id = tweet.get("author_id")
    author = ""
    if author_id and users_map:
        user = users_map.get(author_id, {})
        author = f"@{user.get('username', 'unknown')}"

    likes = metrics.get("like_count", 0)
    retweets = metrics.get("retweet_count", 0)
    replies = metrics.get("reply_count", 0)

    return f"""
{'─' * 60}
{text[:300]}{'...' if len(text) > 300 else ''}
{'─' * 60}
👤 {author} | 🕒 {time_str}
❤️ {likes} | 🔄 {retweets} | 💬 {replies}
"""


def main():
    parser = argparse.ArgumentParser(description='Search X (Twitter) for recent tweets')
    parser.add_argument('--query', '-q', required=True, help='Search query with operators')
    parser.add_argument('--count', '-n', type=int, default=10, help='Number of results (max 100)')
    parser.add_argument('--output', '-o', choices=['json', 'pretty'], default='pretty', help='Output format')
    parser.add_argument('--save', '-s', help='Save results to file')

    args = parser.parse_args()

    if not os.environ.get('X_BEARER_TOKEN'):
        print("❌ Error: X_BEARER_TOKEN not set")
        print("\nGet API token:")
        print("1. Visit https://developer.x.com")
        print("2. Create project and app")
        print("3. Generate Bearer Token")
        print("4. Run: export X_BEARER_TOKEN='your_token'")
        sys.exit(1)

    print(f"🔍 Searching: {args.query}\n")

    try:
        api = XTwitterAPI()
        result = api.search_recent(args.query, args.count)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    if not result or "data" not in result:
        print("❌ No results found")
        sys.exit(1)

    tweets = result["data"]

    # Build user map
    users_map = {}
    if "includes" in result and "users" in result["includes"]:
        users_map = {u["id"]: u for u in result["includes"]["users"]}

    # Output
    if args.output == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"✅ Found {len(tweets)} tweets:\n")
        for tweet in tweets:
            print(format_tweet(tweet, users_map))

    # Save to file
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved to: {args.save}")


if __name__ == "__main__":
    main()
