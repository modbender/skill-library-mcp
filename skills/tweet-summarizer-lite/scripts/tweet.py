#!/usr/bin/env python3
"""
Fetch a single tweet and optionally generate a summary.

Usage:
    tweet.py <URL> [--no-summary]
    tweet.py https://x.com/user/status/123456789
    tweet.py https://x.com/user/status/123456789 -ns
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path

def fetch_tweet(url_or_id):
    """
    Fetch a tweet using bird CLI.
    Requires: AUTH_TOKEN and CT0 environment variables set.
    """
    auth_token = os.getenv('AUTH_TOKEN')
    ct0 = os.getenv('CT0')
    
    if not auth_token or not ct0:
        print("❌ Twitter credentials not set")
        print("   Set AUTH_TOKEN and CT0 environment variables")
        print("   See SECURITY.md for how to obtain these safely")
        return None
    
    try:
        result = subprocess.run(
            ['bird', 'read', url_or_id, '--plain'],
            env={**os.environ, 'AUTH_TOKEN': auth_token, 'CT0': ct0},
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to fetch tweet: {result.stderr}")
            return None
        
        return result.stdout.strip()
    
    except FileNotFoundError:
        print("❌ bird CLI not found")
        print("   Install with: npm install -g @steipete/bird")
        return None
    except subprocess.TimeoutExpired:
        print("❌ Request timeout")
        return None
    except Exception as e:
        print(f"❌ Error fetching tweet: {e}")
        return None

def summarize_text(text):
    """
    Generate a simple summary of tweet text.
    For lite version, just extract key sentences.
    """
    sentences = text.split('. ')
    if len(sentences) <= 2:
        return text
    
    # Return first + last sentences for brevity
    summary = sentences[0] + '. ' + sentences[-1]
    return summary

def store_tweet(tweet_text, tweet_id):
    """
    Store tweet locally for search.
    """
    data_dir = Path.home() / '.openclaw' / 'workspace' / 'data' / 'tweets-lite'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    tweet_file = data_dir / 'index.json'
    
    tweets = {}
    if tweet_file.exists():
        with open(tweet_file, 'r') as f:
            tweets = json.load(f)
    
    tweets[tweet_id] = {
        'text': tweet_text,
        'timestamp': str(__import__('datetime').datetime.now().isoformat())
    }
    
    with open(tweet_file, 'w') as f:
        json.dump(tweets, f, indent=2)
    
    return tweet_file

def main():
    if len(sys.argv) < 2:
        print("Usage: tweet.py <URL> [--no-summary]")
        print("\nExample:")
        print("  tweet.py https://x.com/user/status/123456789")
        print("  tweet.py https://x.com/user/status/123456789 -ns")
        sys.exit(1)
    
    url = sys.argv[1]
    show_summary = '--no-summary' not in sys.argv and '-ns' not in sys.argv
    
    # Extract tweet ID from URL
    match = re.search(r'/status/(\d+)', url)
    tweet_id = match.group(1) if match else url.split('/')[-1]
    
    print(f"🔍 Fetching tweet: {tweet_id}")
    
    tweet_text = fetch_tweet(url)
    if not tweet_text:
        sys.exit(1)
    
    print(f"\n📝 Tweet:")
    print(tweet_text)
    
    # Store tweet
    store_tweet(tweet_text, tweet_id)
    print(f"\n✅ Stored to ~/.openclaw/workspace/data/tweets-lite/")
    
    # Show summary if requested
    if show_summary:
        summary = summarize_text(tweet_text)
        print(f"\n📊 Summary:")
        print(summary)

if __name__ == '__main__':
    main()
