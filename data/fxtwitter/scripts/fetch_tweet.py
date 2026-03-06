#!/usr/bin/env python3
"""
Fetch tweet data from fxTwitter API.
Usage: python3 fetch_tweet.py <tweet_url_or_id>
"""

import sys
import re
import json
import urllib.request

def extract_id(input_str):
    # Match twitter.com or x.com status URL
    m = re.search(r'status/(\d+)', input_str)
    if m:
        return m.group(1)
    # Assume it's already an ID
    if re.match(r'^\d+$', input_str.strip()):
        return input_str.strip()
    return None

def fetch_tweet(tweet_id):
    url = f"https://api.fxtwitter.com/{tweet_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "fxtwitter-skill/1.0"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_tweet.py <tweet_url_or_id>", file=sys.stderr)
        sys.exit(1)

    tweet_id = extract_id(sys.argv[1])
    if not tweet_id:
        print(f"Could not extract tweet ID from: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)

    data = fetch_tweet(tweet_id)
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
