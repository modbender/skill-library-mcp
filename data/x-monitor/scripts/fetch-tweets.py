#!/usr/bin/env python3
"""
Fetch and filter X/Twitter tweets from monitored handles.
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Config paths
BASE_DIR = Path.home() / '.openclaw' / 'workspace' / 'x-monitor'
CREDS_FILE = BASE_DIR / 'credentials.json'
HANDLES_FILE = BASE_DIR / 'handles.json'
LAST_CHECK_FILE = BASE_DIR / 'last-check.json'

def load_json(path):
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def fetch_recent_tweets(handle, bearer_token, since_time=None):
    """Fetch recent tweets from a handle using X API v2."""
    url = 'https://api.x.com/2/tweets/search/recent'
    
    query = f'from:{handle}'
    if since_time:
        # Format: YYYY-MM-DDTHH:mm:ssZ
        query += f' -is:retweet'
    
    params = {
        'query': query,
        'max_results': 10,
        'tweet.fields': 'created_at,public_metrics,author_id,lang',
        'expansions': 'author_id',
        'user.fields': 'name,username'
    }
    
    if since_time:
        params['start_time'] = since_time
    
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tweets for @{handle}: {e}", file=sys.stderr)
        return None

def format_tweet(tweet, user_map):
    """Format tweet for display."""
    author_id = tweet.get('author_id')
    user = user_map.get(author_id, {})
    username = user.get('username', 'unknown')
    name = user.get('name', username)
    
    text = tweet.get('text', '')
    created = tweet.get('created_at', '')
    metrics = tweet.get('public_metrics', {})
    
    likes = metrics.get('like_count', 0)
    retweets = metrics.get('retweet_count', 0)
    
    # Format timestamp
    if created:
        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
        time_str = dt.strftime('%b %d, %I:%M %p')
    else:
        time_str = 'unknown time'
    
    return {
        'username': username,
        'name': name,
        'text': text,
        'time': time_str,
        'likes': likes,
        'retweets': retweets,
        'url': f'https://twitter.com/{username}/status/{tweet["id"]}'
    }

def main():
    # Load config
    creds = load_json(CREDS_FILE)
    handles_data = load_json(HANDLES_FILE)
    last_check = load_json(LAST_CHECK_FILE)
    
    bearer_token = creds.get('bearer_token')
    if not bearer_token or bearer_token == 'YOUR_BEARER_TOKEN_HERE':
        print("Error: X API bearer token not configured", file=sys.stderr)
        print("Edit ~/.openclaw/workspace/x-monitor/credentials.json", file=sys.stderr)
        sys.exit(1)
    
    handles = handles_data.get('handles', [])
    if not handles:
        print("No handles configured. Add handles to ~/.openclaw/workspace/x-monitor/handles.json")
        sys.exit(0)
    
    # Get last check time
    last_check_time = last_check.get('last_check_time')
    
    # Fetch tweets
    all_tweets = []
    for handle in handles:
        data = fetch_recent_tweets(handle, bearer_token, since_time=last_check_time)
        if not data or 'data' not in data:
            continue
        
        # Build user map
        user_map = {}
        if 'includes' in data and 'users' in data['includes']:
            for user in data['includes']['users']:
                user_map[user['id']] = user
        
        # Format tweets
        for tweet in data.get('data', []):
            formatted = format_tweet(tweet, user_map)
            all_tweets.append(formatted)
    
    # Sort by time (most recent first)
    # Note: This is simplified - for production you'd parse the full timestamp
    
    # Update last check time
    now = datetime.utcnow().isoformat() + 'Z'
    save_json(LAST_CHECK_FILE, {'last_check_time': now})
    
    # Save all tweets to history file with timestamp
    history_file = BASE_DIR / 'tweet_history.json'
    try:
        if history_file.exists():
            history = load_json(history_file)
        else:
            history = {"checks": []}
        
        # Add this check to history
        check_entry = {
            "timestamp": now,
            "tweet_count": len(all_tweets),
            "tweets": all_tweets
        }
        
        # Add to start of list (most recent first)
        history["checks"].insert(0, check_entry)
        
        # Keep only last 50 checks to avoid file growing too large
        if len(history["checks"]) > 50:
            history["checks"] = history["checks"][:50]
        
        save_json(history_file, history)
    except Exception as e:
        print(f"Warning: Failed to save tweet history: {e}", file=sys.stderr)
    
    # Output as JSON for OpenClaw to process
    print(json.dumps({
        'tweets': all_tweets,
        'count': len(all_tweets)
    }, indent=2))

if __name__ == '__main__':
    main()
