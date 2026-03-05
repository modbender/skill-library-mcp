#!/usr/bin/env python3
"""
X (Twitter) Article/Tweet Retrieval Script
Get article or tweet content by URL or ID
"""
import os
import sys
import json
import argparse
import requests
from urllib.parse import urlparse
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

    def get_tweet_by_id(self, tweet_id):
        """Get tweet details by ID"""
        url = f"{self.base_url}/tweets/{tweet_id}"

        params = {
            "tweet.fields": "text,created_at,author_id,public_metrics,attachments,entities,conversation_id,referenced_tweets,article",
            "expansions": "author_id,attachments.media_keys",
            "user.fields": "name,username,description,profile_image_url,verified,public_metrics",
            "media.fields": "url,preview_image_url,type,alt_text"
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


def extract_id_from_url(url):
    """Extract tweet/article ID from URL"""
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")

    # Check for article format: x.com/user/article/ID
    if "article" in path_parts:
        article_index = path_parts.index("article")
        if article_index + 1 < len(path_parts):
            return path_parts[article_index + 1]

    # Check for status format: x.com/user/status/ID
    if "status" in path_parts:
        status_index = path_parts.index("status")
        if status_index + 1 < len(path_parts):
            return path_parts[status_index + 1]

    # Try last part as ID
    if path_parts and path_parts[-1].isdigit():
        return path_parts[-1]

    return None


def format_tweet_data(data):
    """Format tweet data for display"""
    if not data or "data" not in data:
        return "❌ No tweet data found"

    tweet = data["data"]
    tweet_id = tweet.get("id", "N/A")
    text = tweet.get("text", "")
    created_at = tweet.get("created_at", "")
    author_id = tweet.get("author_id", "N/A")
    metrics = tweet.get("public_metrics", {})

    # Format time
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        time_str = created_at

    # Get author info
    author_info = ""
    if "includes" in data and "users" in data["includes"]:
        for user in data["includes"]["users"]:
            if user.get("id") == author_id:
                author_info = f"@{user.get('username', 'unknown')} ({user.get('name', 'Unknown')})"
                if user.get("verified"):
                    author_info += " ✓"
                break

    # Format metrics
    likes = metrics.get("like_count", 0)
    retweets = metrics.get("retweet_count", 0)
    replies = metrics.get("reply_count", 0)
    quotes = metrics.get("quote_count", 0)

    output = f"""
{'=' * 60}
📱 Tweet ID: {tweet_id}
{'=' * 60}

👤 {author_info}
🕒 {time_str}

{text}

{'─' * 60}
📊 Metrics:
   ❤️ Likes: {likes}
   🔄 Retweets: {retweets}
   💬 Replies: {replies}
   📎 Quotes: {quotes}
"""

    return output


def main():
    parser = argparse.ArgumentParser(description='Get X (Twitter) article or tweet content')
    parser.add_argument('--url', '-u', help='Tweet or article URL')
    parser.add_argument('--id', '-i', help='Tweet ID (alternative to URL)')
    parser.add_argument('--output', '-o', choices=['json', 'pretty', 'markdown'], default='pretty', help='Output format')
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

    # Extract tweet ID
    tweet_id = None
    if args.id:
        tweet_id = args.id
    elif args.url:
        tweet_id = extract_id_from_url(args.url)
        if not tweet_id:
            print(f"❌ Could not extract tweet ID from URL: {args.url}")
            sys.exit(1)
    else:
        print("❌ Error: Please provide --url or --id")
        sys.exit(1)

    print(f"🔍 Fetching tweet ID: {tweet_id}\n")

    # Get tweet data
    try:
        api = XTwitterAPI()
        data = api.get_tweet_by_id(tweet_id)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    if not data:
        print("❌ Failed to fetch tweet")
        sys.exit(1)

    # Check for errors
    if "errors" in data:
        print(f"❌ API returned errors:")
        for error in data["errors"]:
            print(f"   - {error.get('message', 'Unknown error')}")
        sys.exit(1)

    # Output
    if args.output == 'json':
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.output == 'markdown':
        print(format_tweet_data(data))
    else:  # pretty
        print(format_tweet_data(data))

    # Save to file
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved to: {args.save}")


if __name__ == "__main__":
    main()
