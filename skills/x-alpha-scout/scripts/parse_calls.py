#!/usr/bin/env python3
"""
Parse X/Twitter search results into structured call objects.
Usage: python3 parse_calls.py < bird_output.json
"""

import json
import re
import sys
from datetime import datetime

def extract_ticker(text):
    """Extract $TICKER from text"""
    tickers = re.findall(r'\$([A-Za-z]{2,10})', text)
    return tickers[0] if tickers else None

def extract_conviction(text):
    """Score conviction based on keywords"""
    high = ['all in', '50%', '70%', '100%', 'life savings', 'yolo']
    medium = ['loading up', 'accumulating', 'bought', 'entering']
    low = ['looking at', 'might buy', 'considering']
    
    text_lower = text.lower()
    if any(h in text_lower for h in high):
        return 'HIGH'
    elif any(m in text_lower for m in medium):
        return 'MEDIUM'
    elif any(l in text_lower for l in low):
        return 'LOW'
    return 'UNKNOWN'

def parse_tweet(tweet_text, username, timestamp):
    """Parse a single tweet into call object"""
    ticker = extract_ticker(tweet_text)
    conviction = extract_conviction(tweet_text)
    
    # Determine asset type
    asset_type = 'token'
    if any(word in tweet_text.lower() for word in ['nft', 'mint', 'collection']):
        asset_type = 'nft'
    
    # Determine call type
    call_type = 'shill'
    if any(word in tweet_text.lower() for word in ['bought', 'buying', 'ape']):
        call_type = 'buy'
    elif any(word in tweet_text.lower() for word in ['minting', 'mint']):
        call_type = 'mint'
    
    return {
        'caller': username,
        'asset': ticker or 'Unknown',
        'asset_type': asset_type,
        'call_type': call_type,
        'conviction': conviction,
        'timestamp': timestamp,
        'raw_text': tweet_text[:200] + '...' if len(tweet_text) > 200 else tweet_text
    }

if __name__ == '__main__':
    # Read from stdin or file
    data = json.load(sys.stdin) if not sys.stdin.isatty() else []
    
    calls = []
    for tweet in data:
        call = parse_tweet(
            tweet.get('text', ''),
            tweet.get('username', 'unknown'),
            tweet.get('timestamp', datetime.now().isoformat())
        )
        if call['asset'] != 'Unknown':
            calls.append(call)
    
    # Output formatted calls
    print(json.dumps(calls, indent=2))
