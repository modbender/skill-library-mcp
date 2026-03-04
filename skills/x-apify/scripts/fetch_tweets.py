#!/usr/bin/env python3
"""
Fetch X/Twitter data via Apify API with local caching.

Usage:
    python3 fetch_tweets.py --search "query"
    python3 fetch_tweets.py --user "username"
    python3 fetch_tweets.py --url "https://x.com/user/status/123"
    python3 fetch_tweets.py --cache-stats
    python3 fetch_tweets.py --clear-cache

Requires:
    - APIFY_API_TOKEN environment variable
    - requests library (pip install requests)
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone

# Add scripts directory to path for imports
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import requests
except ImportError:
    print("Error: 'requests' library not installed.", file=sys.stderr)
    print("Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

from config import (
    APIFY_API_BASE,
    DEFAULT_MAX_RESULTS,
    get_api_token,
    get_actor_id,
    sanitize_query,
    sanitize_username,
    extract_tweet_id,
    extract_username_from_url,
)
from cache import (
    load_from_cache,
    save_to_cache,
    clear_cache,
    print_cache_stats,
)


def run_apify_actor(input_data, api_token):
    """
    Run the Apify actor and return results.
    
    Args:
        input_data: Actor input configuration
        api_token: Apify API token
    
    Returns:
        List of tweet objects from the actor
    """
    actor_id = get_actor_id()
    run_url = f"{APIFY_API_BASE}/acts/{actor_id}/runs"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    try:
        # Start the run
        response = requests.post(
            run_url,
            headers=headers,
            json=input_data,
            timeout=30
        )
        
        if response.status_code == 401:
            print("Error: Invalid API token.", file=sys.stderr)
            sys.exit(1)
        
        if response.status_code == 402:
            print("Error: Apify quota exceeded. Check your billing:", file=sys.stderr)
            print("https://console.apify.com/billing", file=sys.stderr)
            sys.exit(1)
        
        response.raise_for_status()
        run_data = response.json()["data"]
        run_id = run_data["id"]
        
    except requests.exceptions.RequestException as e:
        print(f"Error starting Apify actor: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Wait for completion
    status_url = f"{APIFY_API_BASE}/actor-runs/{run_id}"
    max_wait = 180  # seconds (tweets can take longer)
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(
                status_url,
                headers={"Authorization": f"Bearer {api_token}"},
                timeout=10
            )
            response.raise_for_status()
            status_data = response.json()["data"]
            status = status_data["status"]
            
            if status == "SUCCEEDED":
                break
            elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                print(f"Error: Apify actor {status.lower()}.", file=sys.stderr)
                sys.exit(1)
            
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            print(f"Error checking status: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Timeout waiting for Apify actor.", file=sys.stderr)
        sys.exit(1)
    
    # Get results from dataset
    dataset_id = status_data["defaultDatasetId"]
    dataset_url = f"{APIFY_API_BASE}/datasets/{dataset_id}/items"
    
    try:
        response = requests.get(
            dataset_url,
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=30
        )
        response.raise_for_status()
        results = response.json()
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching results: {e}", file=sys.stderr)
        sys.exit(1)


def search_tweets(query, max_results, api_token, use_cache):
    """Search for tweets by query."""
    query = sanitize_query(query)
    if not query:
        print("Error: Empty search query.", file=sys.stderr)
        sys.exit(1)
    
    # Check cache
    if use_cache:
        cached = load_from_cache('search', query)
        if cached:
            print(f"[cached] Search results for: {query}", file=sys.stderr)
            return cached, True
    
    print(f"Searching tweets for: {query}", file=sys.stderr)
    
    input_data = {
        "searchTerms": [query],
        "maxItems": max_results,
    }
    
    results = run_apify_actor(input_data, api_token)
    
    # Format results
    formatted = format_results('search', query, results)
    
    # Save to cache
    if use_cache:
        save_to_cache('search', query, formatted)
    
    return formatted, False


def get_user_tweets(username, max_results, api_token, use_cache):
    """Get tweets from a specific user."""
    username = sanitize_username(username)
    if not username:
        print("Error: Invalid username.", file=sys.stderr)
        sys.exit(1)
    
    # Check cache
    if use_cache:
        cached = load_from_cache('user', username)
        if cached:
            print(f"[cached] Tweets from: @{username}", file=sys.stderr)
            return cached, True
    
    print(f"Fetching tweets from: @{username}", file=sys.stderr)
    
    input_data = {
        "startUrls": [{"url": f"https://x.com/{username}"}],
        "maxItems": max_results,
    }
    
    results = run_apify_actor(input_data, api_token)
    
    # Format results
    formatted = format_results('user', username, results)
    
    # Save to cache
    if use_cache:
        save_to_cache('user', username, formatted)
    
    return formatted, False


def get_tweet_by_url(url, api_token, use_cache):
    """Get a specific tweet and its replies by URL."""
    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        print(f"Error: Could not extract tweet ID from: {url}", file=sys.stderr)
        sys.exit(1)
    
    # Check cache
    if use_cache:
        cached = load_from_cache('url', tweet_id)
        if cached:
            print(f"[cached] Tweet: {tweet_id}", file=sys.stderr)
            return cached, True
    
    print(f"Fetching tweet: {tweet_id}", file=sys.stderr)
    
    # Construct full URL if needed
    if not url.startswith('http'):
        url = f"https://x.com/i/status/{tweet_id}"
    
    input_data = {
        "startUrls": [{"url": url}],
        "maxItems": 50,  # Include replies when available
    }
    
    results = run_apify_actor(input_data, api_token)
    
    # Format results
    formatted = format_results('url', url, results)
    
    # Save to cache
    if use_cache:
        save_to_cache('url', tweet_id, formatted)
    
    return formatted, False


def format_results(mode, identifier, raw_results):
    """Format raw Apify results into standardized output."""
    tweets = []
    
    for item in raw_results:
        screen_name = item.get('user', {}).get('screen_name', '')
        tweet_id = item.get('id_str', item.get('id', ''))
        tweet = {
            'id': tweet_id,
            'text': item.get('text', item.get('full_text', '')),
            'author': screen_name,
            'author_name': item.get('user', {}).get('name', ''),
            'created_at': item.get('created_at', item.get('createdAt', '')),
            'likes': item.get('favorite_count', item.get('likeCount', 0)),
            'retweets': 0,
            'replies': item.get('conversation_count', item.get('replyCount', 0)),
            'url': item.get('url', ''),
        }
        
        # Build URL if not present
        if not tweet['url'] and tweet['author'] and tweet['id']:
            tweet['url'] = f"https://x.com/{tweet['author']}/status/{tweet['id']}"
        
        tweets.append(tweet)
    
    return {
        'query': identifier,
        'mode': mode,
        'fetched_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'count': len(tweets),
        'tweets': tweets,
    }


def format_output_json(data):
    """Format data as JSON string."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_output_summary(data):
    """Format data as human-readable summary."""
    lines = []
    
    mode_labels = {
        'search': 'Search Results',
        'user': 'User Tweets',
        'url': 'Tweet Details',
    }
    
    lines.append(f"=== X/Twitter {mode_labels.get(data['mode'], 'Results')} ===")
    lines.append(f"Query: {data['query']}")
    lines.append(f"Fetched: {data['fetched_at']}")
    lines.append(f"Results: {data['count']} tweets")
    lines.append("")
    
    for tweet in data['tweets']:
        lines.append("---")
        lines.append(f"@{tweet['author']} ({tweet['author_name']})")
        lines.append(f"{tweet['created_at']}")
        lines.append(tweet['text'])
        lines.append(f"[Likes: {tweet['likes']} | RTs: {tweet['retweets']} | Replies: {tweet['replies']}]")
        if tweet['url']:
            lines.append(tweet['url'])
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch X/Twitter data via Apify API with local caching"
    )
    
    # Mode arguments (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--search", "-s",
        metavar="QUERY",
        help="Search tweets by keywords, hashtags, mentions"
    )
    mode_group.add_argument(
        "--user", "-u",
        metavar="USERNAME",
        help="Get tweets from a specific user"
    )
    mode_group.add_argument(
        "--url",
        metavar="URL",
        help="Get a specific tweet and replies by URL"
    )
    
    # Options
    parser.add_argument(
        "--max-results", "-n",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help=f"Maximum results to fetch (default: {DEFAULT_MAX_RESULTS})"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output file path (default: stdout)"
    )
    
    # Cache options
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass cache (always fetch fresh)"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all cached results and exit"
    )
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show cache statistics and exit"
    )
    
    args = parser.parse_args()
    
    # Handle cache management commands (no API token needed)
    if args.clear_cache:
        clear_cache()
        return
    
    if args.cache_stats:
        print_cache_stats()
        return
    
    # Need at least one mode
    if not args.search and not args.user and not args.url:
        parser.print_help()
        print("\nError: Specify --search, --user, or --url", file=sys.stderr)
        sys.exit(1)
    
    # Get API token
    api_token = get_api_token()
    use_cache = not args.no_cache
    
    # Execute based on mode
    if args.search:
        data, from_cache = search_tweets(args.search, args.max_results, api_token, use_cache)
    elif args.user:
        data, from_cache = get_user_tweets(args.user, args.max_results, api_token, use_cache)
    else:  # args.url
        data, from_cache = get_tweet_by_url(args.url, api_token, use_cache)
    
    # Format output
    if args.format == "json":
        output = format_output_json(data)
    else:
        output = format_output_summary(data)
    
    # Write output (path-jailed to script directory for safety)
    if args.output:
        safe_dir = os.path.dirname(os.path.abspath(__file__))
        out_path = os.path.abspath(args.output)
        if not out_path.startswith(safe_dir) and not out_path.startswith("/tmp"):
            print(f"Error: output path must be under {safe_dir} or /tmp", file=sys.stderr)
            sys.exit(1)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Results saved to: {out_path}", file=sys.stderr)
    else:
        print(output)
    
    if not from_cache:
        print("\n[Apify credits used - check https://console.apify.com/billing]", file=sys.stderr)


if __name__ == "__main__":
    main()
