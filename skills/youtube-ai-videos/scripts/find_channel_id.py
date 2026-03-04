#!/usr/bin/env python3
"""
YouTube Channel ID Finder
Finds YouTube channel IDs from channel handles (@name) or names
"""

import sys
import re
from urllib.parse import urlparse
from urllib.request import urlopen, Request

def find_channel_id(channel_input):
    """Find YouTube channel ID from handle or name"""
    
    # Convert handle to URL format
    if channel_input.startswith('@'):
        url = f"https://www.youtube.com/{channel_input}"
    elif channel_input.startswith('UC'):
        return channel_input  # Already a channel ID
    elif 'youtube.com/' in channel_input or 'youtu.be/' in channel_input:
        url = channel_input
    else:
        # Assume it's a channel name
        url = f"https://www.youtube.com/{channel_input}"
    
    try:
        # Fetch channel page
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req, timeout=10)
        html = response.read().decode('utf-8')
        
        # Extract channel ID from HTML
        # Channel IDs start with UC and are 24 characters
        pattern = r'"channelId":"(UC[A-Za-z0-9_-]{22})"'
        match = re.search(pattern, html)
        
        if match:
            return match.group(1)
        
        # Alternative patterns
        patterns = [
            r'youtube\.com/channel/(UC[A-Za-z0-9_-]{22})',
            r'"externalId":"(UC[A-Za-z0-9_-]{22})"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        
        print(f"❌ Could not find channel ID for: {channel_input}")
        return None
    
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: find_channel_id.py '@channel_name' or 'channel_id' or 'url'")
        sys.exit(1)
    
    channel_input = sys.argv[1]
    channel_id = find_channel_id(channel_input)
    
    if channel_id:
        print(f"✅ Channel ID for '{channel_input}': {channel_id}")
