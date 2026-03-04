#!/usr/bin/env python3
"""
X (Twitter) Trending Topics Script
Fetch trending topics from X API v2
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

    def get_trending_topics(self, woeid=1):
        """
        Get trending topics

        Parameters:
            woeid: Yahoo Where On Earth ID (1 = Global)

        Note: This endpoint may require Basic tier or higher
        """
        url = f"{self.base_url}/trends"

        params = {"woeid": woeid}

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


# Common WOEID values
WOEID_LOCATIONS = {
    1: "Global",
    23424977: "USA",
    23424975: "UK",
    23424819: "Canada",
    23424856: "Australia",
    23424981: "India",
    23424809: "Japan",
    23424900: "Brazil",
    23424748: "Germany",
    23424829: "France",
    23424850: "Spain",
    23424982: "Singapore",
    23424751: "Italy",
    23424978: "Taiwan",
    23424965: "Mexico",
}


def format_trends(data, woeid):
    """Format trending topics for display"""
    if not data or "data" not in data:
        return "❌ No trending topics found"

    location = WOEID_LOCATIONS.get(woeid, f"WOEID {woeid}")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    output = f"""
{'=' * 60}
📈 Trending Topics - {location}
{'=' * 60}
🕒 {timestamp}

"""

    trends = data["data"]

    for i, trend in enumerate(trends[:10], 1):
        name = trend.get("name", "N/A")
        tweet_count = trend.get("tweet_count", "N/A")
        url = trend.get("url", "N/A")

        output += f"{i}. {name}\n"
        output += f"   📊 {tweet_count:,} tweets\n" if isinstance(tweet_count, int) else f"   📊 {tweet_count}\n"
        output += f"   🔗 {url}\n\n"

    return output


def main():
    parser = argparse.ArgumentParser(description='Get trending topics from X (Twitter)')
    parser.add_argument('--woeid', '-w', type=int, default=1, help='WOEID (default: 1 for Global)')
    parser.add_argument('--list', '-l', action='store_true', help='List common WOEID values')
    parser.add_argument('--output', '-o', choices=['json', 'pretty'], default='pretty', help='Output format')
    parser.add_argument('--save', '-s', help='Save results to file')

    args = parser.parse_args()

    if args.list:
        print("🌍 Common WOEID Values:\n")
        for woeid, name in sorted(WOEID_LOCATIONS.items()):
            print(f"  {woeid:12} - {name}")
        print("\n🔍 Full list: https://woeid.rosselliot.co.nz/")
        return

    if not os.environ.get('X_BEARER_TOKEN'):
        print("❌ Error: X_BEARER_TOKEN not set")
        print("\nGet API token:")
        print("1. Visit https://developer.x.com")
        print("2. Create project and app")
        print("3. Generate Bearer Token")
        print("4. Run: export X_BEARER_TOKEN='your_token'")
        sys.exit(1)

    location = WOEID_LOCATIONS.get(args.woeid, f"WOEID {args.woeid}")
    print(f"🔍 Fetching trending topics for: {location}\n")

    # Get trends
    try:
        api = XTwitterAPI()
        data = api.get_trending_topics(args.woeid)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    if not data:
        print("❌ Failed to fetch trending topics")
        print("\n💡 Note: Trending topics may require Basic tier ($200/month) or higher")
        print("   Free tier has limited access to this endpoint")
        sys.exit(1)

    # Check for errors
    if "errors" in data:
        print(f"❌ API returned errors:")
        for error in data["errors"]:
            print(f"   - {error.get('message', 'Unknown error')}")
        print("\n💡 This endpoint may require Basic tier or higher")
        sys.exit(1)

    # Output
    if args.output == 'json':
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(format_trends(data, args.woeid))

    # Save to file
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved to: {args.save}")


if __name__ == "__main__":
    main()
