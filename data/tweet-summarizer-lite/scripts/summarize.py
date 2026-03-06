#!/usr/bin/env python3
"""
Generate summary for a stored tweet.

Usage:
    summarize.py <tweet-id>
"""

import sys
import json
from pathlib import Path

def load_tweet(tweet_id):
    """Load a specific tweet."""
    data_dir = Path.home() / '.openclaw' / 'workspace' / 'data' / 'tweets-lite'
    tweet_file = data_dir / 'index.json'
    
    if not tweet_file.exists():
        return None
    
    with open(tweet_file, 'r') as f:
        tweets = json.load(f)
    
    return tweets.get(tweet_id)

def summarize_tweet(text):
    """
    Simple summarization: extract key sentences.
    For lite version, identify sentence boundaries and pick important ones.
    """
    # Split by sentence-ending punctuation
    import re
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= 2:
        return text
    
    # Return first sentence + last sentence for context
    if len(sentences) >= 2:
        return sentences[0] + '. ' + sentences[-1] + '.'
    
    return sentences[0]

def main():
    if len(sys.argv) < 2:
        print("Usage: summarize.py <tweet-id>")
        print("\nExample:")
        print("  summarize.py 1234567890")
        sys.exit(1)
    
    tweet_id = sys.argv[1]
    tweet = load_tweet(tweet_id)
    
    if not tweet:
        print(f"❌ Tweet not found: {tweet_id}")
        print("   Have you fetched it yet? Run: tweet.py <URL>")
        sys.exit(1)
    
    print(f"📌 Tweet {tweet_id}:")
    print(f"   {tweet['text']}\n")
    
    summary = summarize_tweet(tweet['text'])
    print(f"📊 Summary:")
    print(f"   {summary}")

if __name__ == '__main__':
    main()
