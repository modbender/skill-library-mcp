#!/usr/bin/env python3
"""
Configuration helpers for x-apify skill.
"""

import os
import re
import sys
from pathlib import Path

# API configuration
APIFY_API_BASE = "https://api.apify.com/v2"
DEFAULT_ACTOR_ID = "quacker~twitter-scraper"

# Defaults
DEFAULT_MAX_RESULTS = 20
MAX_QUERY_LENGTH = 500

# Cache TTLs (seconds)
CACHE_TTL_SEARCH = 3600       # 1 hour for searches
CACHE_TTL_PROFILE = 86400     # 24 hours for user profiles
CACHE_TTL_TWEET = 86400       # 24 hours for specific tweets


def get_skill_dir():
    """Get the skill root directory."""
    return Path(__file__).parent.parent


def get_api_token():
    """Get Apify API token from environment."""
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        print("Error: APIFY_API_TOKEN environment variable not set.", file=sys.stderr)
        print("\nSetup instructions:", file=sys.stderr)
        print("1. Create free account: https://apify.com/", file=sys.stderr)
        print("2. Get API token: https://console.apify.com/account/integrations", file=sys.stderr)
        print("3. Export: export APIFY_API_TOKEN='apify_api_YOUR_TOKEN'", file=sys.stderr)
        sys.exit(1)
    return token


def get_actor_id():
    """Get Apify actor ID from environment or use default."""
    return os.environ.get("APIFY_ACTOR_ID", DEFAULT_ACTOR_ID)


def get_cache_dir():
    """Get cache directory from environment or use default."""
    env_dir = os.environ.get("X_APIFY_CACHE_DIR")
    if env_dir:
        return Path(env_dir)
    return get_skill_dir() / ".cache"


def sanitize_query(query):
    """
    Sanitize search query for safety.
    
    - Removes control characters
    - Limits length
    - Strips whitespace
    """
    if not query:
        return ""
    
    # Remove control characters (except normal whitespace)
    query = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', query)
    
    # Remove unicode control characters
    query = re.sub(r'[\u200b-\u200f\u2028-\u202f\u2060-\u206f\ufeff]', '', query)
    
    # Limit length
    if len(query) > MAX_QUERY_LENGTH:
        query = query[:MAX_QUERY_LENGTH]
    
    return query.strip()


def sanitize_username(username):
    """
    Sanitize Twitter/X username.
    
    - Removes @ prefix if present
    - Validates format
    - Limits length
    """
    if not username:
        return ""
    
    # Remove @ prefix
    username = username.lstrip('@')
    
    # Remove control characters
    username = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', username)
    
    # Twitter usernames: alphanumeric and underscores, max 15 chars
    username = re.sub(r'[^a-zA-Z0-9_]', '', username)
    
    return username[:15]


def extract_tweet_id(url):
    """
    Extract tweet ID from X/Twitter URL.
    
    Supports:
    - https://x.com/user/status/123456789
    - https://twitter.com/user/status/123456789
    - https://mobile.twitter.com/user/status/123456789
    """
    if not url:
        return None
    
    # Match status ID in URL
    match = re.search(r'/status/(\d+)', url)
    if match:
        return match.group(1)
    
    # Maybe it's just the tweet ID
    if re.match(r'^\d{10,}$', url):
        return url
    
    return None


def extract_username_from_url(url):
    """Extract username from X/Twitter profile URL."""
    if not url:
        return None
    
    # Match username in URL path
    match = re.search(r'(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)(?:/|$|\?)', url)
    if match:
        username = match.group(1)
        # Exclude reserved paths
        if username.lower() not in ('status', 'search', 'explore', 'home', 'i', 'intent'):
            return username
    
    return None
