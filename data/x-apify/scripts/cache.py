#!/usr/bin/env python3
"""
Local file cache for x-apify skill.

Features:
- TTL-based expiration (1h for searches, 24h for profiles)
- JSON file storage
- Cache stats and management
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from config import get_cache_dir, CACHE_TTL_SEARCH, CACHE_TTL_PROFILE, CACHE_TTL_TWEET


def ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cache_key(mode, identifier):
    """
    Generate a cache key for the given mode and identifier.
    
    Args:
        mode: 'search', 'user', or 'url'
        identifier: query string, username, or tweet URL
    
    Returns:
        Cache filename (without path)
    """
    # Create a hash for the identifier to handle special characters
    id_hash = hashlib.sha256(identifier.encode('utf-8')).hexdigest()[:16]
    return f"{mode}_{id_hash}.json"


def get_cache_path(mode, identifier):
    """Get the full cache file path."""
    cache_dir = get_cache_dir()
    return cache_dir / get_cache_key(mode, identifier)


def get_ttl_for_mode(mode):
    """Get TTL in seconds for the given mode."""
    if mode == 'search':
        return CACHE_TTL_SEARCH
    elif mode == 'user':
        return CACHE_TTL_PROFILE
    else:  # url/tweet
        return CACHE_TTL_TWEET


def is_cache_valid(cache_data, mode):
    """Check if cached data is still valid (not expired)."""
    if not cache_data:
        return False
    
    fetched_at = cache_data.get('fetched_at')
    if not fetched_at:
        return False
    
    try:
        # Parse ISO format timestamp
        fetch_time = datetime.fromisoformat(fetched_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        age_seconds = (now - fetch_time).total_seconds()
        
        ttl = get_ttl_for_mode(mode)
        return age_seconds < ttl
    except (ValueError, TypeError):
        return False


def load_from_cache(mode, identifier):
    """
    Load data from cache if available and not expired.
    
    Returns:
        Cached data dict or None if not cached/expired
    """
    cache_path = get_cache_path(mode, identifier)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        if is_cache_valid(cache_data, mode):
            return cache_data
        else:
            # Expired, delete the file
            cache_path.unlink(missing_ok=True)
            return None
            
    except (json.JSONDecodeError, IOError, OSError):
        return None


def save_to_cache(mode, identifier, data):
    """
    Save data to cache.
    
    Args:
        mode: 'search', 'user', or 'url'
        identifier: query string, username, or tweet URL
        data: Data to cache (will add metadata)
    """
    ensure_cache_dir()
    cache_path = get_cache_path(mode, identifier)
    
    # Add cache metadata
    cache_data = {
        'mode': mode,
        'identifier': identifier,
        'fetched_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        **data
    }
    
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except (IOError, OSError) as e:
        print(f"Warning: Could not save to cache: {e}", file=sys.stderr)


def clear_cache():
    """Delete all cached files."""
    cache_dir = get_cache_dir()
    
    if not cache_dir.exists():
        print("Cache directory does not exist.")
        return 0
    
    count = 0
    for cache_file in cache_dir.glob("*.json"):
        try:
            cache_file.unlink()
            count += 1
        except OSError:
            pass
    
    print(f"Cleared {count} cached result(s).")
    return count


def get_cache_stats():
    """Get cache statistics."""
    cache_dir = get_cache_dir()
    
    if not cache_dir.exists():
        return {'count': 0, 'total_size': 0, 'entries': [], 'expired': 0}
    
    entries = []
    total_size = 0
    expired = 0
    
    for cache_file in cache_dir.glob("*.json"):
        size = cache_file.stat().st_size
        total_size += size
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            mode = data.get('mode', 'unknown')
            is_valid = is_cache_valid(data, mode)
            
            if not is_valid:
                expired += 1
            
            entries.append({
                'mode': mode,
                'identifier': data.get('identifier', cache_file.stem)[:50],
                'fetched_at': data.get('fetched_at', 'Unknown'),
                'size': size,
                'valid': is_valid,
                'count': data.get('count', 0)
            })
        except (json.JSONDecodeError, IOError):
            entries.append({
                'mode': 'corrupt',
                'identifier': cache_file.stem,
                'fetched_at': 'Unknown',
                'size': size,
                'valid': False,
                'count': 0
            })
    
    return {
        'count': len(entries),
        'total_size': total_size,
        'expired': expired,
        'entries': sorted(entries, key=lambda x: x.get('fetched_at', ''), reverse=True)
    }


def print_cache_stats():
    """Print cache statistics to stderr."""
    stats = get_cache_stats()
    cache_dir = get_cache_dir()
    
    print(f"\nX/Twitter Cache Stats", file=sys.stderr)
    print(f"   Location: {cache_dir}", file=sys.stderr)
    print(f"   Cached entries: {stats['count']} ({stats['expired']} expired)", file=sys.stderr)
    print(f"   Total size: {stats['total_size']:,} bytes ({stats['total_size'] / 1024:.1f} KB)", file=sys.stderr)
    
    if stats['entries']:
        print(f"\n   Recent entries:", file=sys.stderr)
        for e in stats['entries'][:10]:
            status = "" if e['valid'] else " [expired]"
            print(f"   [{e['mode']}] {e['identifier']} ({e['count']} tweets){status}", file=sys.stderr)
        if len(stats['entries']) > 10:
            print(f"   ... and {len(stats['entries']) - 10} more", file=sys.stderr)
