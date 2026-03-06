#!/usr/bin/env python3
"""
YouTube AI Videos Fetcher (API-based with secure key storage)
Fetches recent AI-related videos using YouTube Data API v3
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Load config
config_path = Path(__file__).parent.parent / "config.json"
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"Error: Config file not found at {config_path}")
    sys.exit(1)

CHANNELS = config.get('channels', [])
KEYWORDS = [k.lower() for k in config.get('keywords', [])]
MAX_VIDEOS = config.get('maxVideos', 15)
MAX_AGE_DAYS = config.get('maxAgeDays', 3)
SEARCH_TRANSCRIPTION = config.get('searchTranscription', False)

# SECURE API KEY LOADING (priority order)
# 1. Environment variable
# 2. Secrets file
# 3. Config (fallback)
YOUTUBE_API_KEY = None

# Try environment variable
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Try secrets file
if not YOUTUBE_API_KEY:
    secrets_dir = Path.home() / '.openclaw' / 'secrets'
    secrets_file = secrets_dir / 'youtube_api_key.txt'
    
    if secrets_file.exists():
        with open(secrets_file, 'r') as f:
            YOUTUBE_API_KEY = f.read().strip()

# Fallback to config (with warning)
if not YOUTUBE_API_KEY:
    YOUTUBE_API_KEY = config.get('youtubeApiKey', '')
    if YOUTUBE_API_KEY and YOUTUBE_API_KEY != 'YOUR_API_KEY_HERE':
        print("⚠️  Warning: Using API key from config.json. For security, use:")
        print("   export YOUTUBE_API_KEY='your_key'")
        print(f"   Or save to: {secrets_file}")

if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == '' or YOUTUBE_API_KEY == 'YOUR_API_KEY_HERE':
    print("❌ YouTube Data API key is required!")
    print("Please add your API key:")
    print("  Option 1: export YOUTUBE_API_KEY='YOUR_KEY'")
    print(f"  Option 2: echo 'YOUR_KEY' > {secrets_file}")
    print("  Option 3: Get a free key at https://console.cloud.google.com/apis/api/youtube.googleapis.com")
    sys.exit(1)

def fetch_channel_videos(channel_input, api_key):
    """Fetch recent videos from a channel using YouTube Data API"""
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
    
    # Determine channel ID format
    if channel_input.startswith('@'):
        url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={channel_input}&key={api_key}"
    else:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=id&id={channel_input}&key={api_key}"
    
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if not data.get('items'):
            print(f"❌ Channel not found: {channel_input}")
            return []
        
        channel_id = data['items'][0]['id']
        
        # Fetch videos from channel
        videos_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&order=date&type=video&maxResults=25&key={api_key}"
        req = Request(videos_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req, timeout=10)
        videos_data = json.loads(response.read().decode('utf-8'))
        
        videos = []
        for item in videos_data.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            videos.append({
                'video_id': video_id,
                'title': snippet['title'],
                'published': snippet['publishedAt'],
                'channel': snippet['channelTitle'],
                'url': f"https://www.youtube.com/watch?v={video_id}"
            })
        
        return videos
    
    except Exception as e:
        print(f"Error fetching {channel_input}: {e}", file=sys.stderr)
        return []

def search_in_transcription(video_id, api_key):
    """Check if video contains keywords in transcription"""
    # This is complex and quota-heavy - skipped for now
    return None

def matches_keywords(title, transcription=None):
    """Check if title or transcription contains any keywords"""
    title_lower = title.lower()
    
    for keyword in KEYWORDS:
        if keyword in title_lower:
            return True, keyword
    
    return False, None

def time_ago(published_str):
    """Calculate time ago from ISO 8601 timestamp"""
    try:
        published = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
        now = datetime.now(published.tzinfo)
        delta = now - published
        
        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        else:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
    except:
        return "unknown"

def is_within_age(published_str, max_days):
    """Check if video is within max age"""
    try:
        published = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
        now = datetime.now(published.tzinfo)
        delta = now - published
        return delta.days <= max_days
    except:
        return False

def main():
    print(f"🎬 Fetching AI videos (last {MAX_AGE_DAYS} days)")
    print(f"Keywords: {', '.join(KEYWORDS)}")
    print(f"Channels: {len(CHANNELS)}")
    print()
    
    all_videos = []
    
    # Fetch videos from all channels
    for channel in CHANNELS:
        print(f"Fetching from {channel}...")
        videos = fetch_channel_videos(channel, YOUTUBE_API_KEY)
        all_videos.extend(videos)
    
    # Filter videos
    filtered_videos = []
    for video in all_videos:
        # Check age
        if not is_within_age(video['published'], MAX_AGE_DAYS):
            continue
        
        # Check keywords in title
        matches, matched_keyword = matches_keywords(video['title'])
        
        if not matches:
            continue
        
        video['matched_keyword'] = matched_keyword
        filtered_videos.append(video)
    
    # Sort by publication date (newest first)
    filtered_videos.sort(key=lambda x: x['published'], reverse=True)
    
    # Limit to max videos
    filtered_videos = filtered_videos[:MAX_VIDEOS]
    
    # Display results
    if not filtered_videos:
        print("❌ No matching videos found.")
        return
    
    for i, video in enumerate(filtered_videos, 1):
        time_ago_str = time_ago(video['published'])
        
        # Highlight matched keyword in title
        import re
        title = video['title']
        keyword = video.get('matched_keyword', '')
        if keyword:
            title = re.sub(f'({re.escape(keyword)})', r'**\1**', title, flags=re.IGNORECASE)
        
        print(f"{i}. [{time_ago_str}] [{title}]({video['url']})")
        print(f"   by @{video['channel']}")
        print()
    
    print(f"✅ Found {len(filtered_videos)} videos (from {len(CHANNELS)} channels)")

if __name__ == '__main__':
    main()
