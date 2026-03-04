#!/usr/bin/env python3
"""
YouTube Master - Ultimate YouTube Scraper
Combines YouTube Data API + Apify for full video info + transcripts.
- Default: YouTube API only (free, fast)
- With --transcript: Apify also (for captions)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# Config - reads from credentials file only
YOUTUBE_API_KEY = None
APIFY_TOKEN = None
APIFY_ACTOR = "scrape-creators~best-youtube-transcripts-scraper"

def get_credentials():
    """Load API tokens from credentials file if not in env"""
    global YOUTUBE_API_KEY, APIFY_TOKEN
    
    creds_path = Path.home() / ".openclaw" / "workspace" / "credentials" / "api-credentials.json"
    if creds_path.exists():
        with open(creds_path) as f:
            creds = json.load(f)
            if "google" in creds and "api_key" in creds["google"]:
                YOUTUBE_API_KEY = creds["google"]["api_key"]
            if "apify" in creds and "api_key" in creds["apify"]:
                APIFY_TOKEN = creds["apify"]["api_key"]
    
    return YOUTUBE_API_KEY, APIFY_TOKEN

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    url = url.strip()
    
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    
    if "youtube.com/watch" in url:
        for part in url.split("?")[-1].split("&"):
            if part.startswith("v="):
                return part[2:].split("&")[0]
    
    if "youtube.com/shorts/" in url:
        return url.split("youtube.com/shorts/")[-1].split("?")[0]
    
    for pattern in ["/v/", "/embed/"]:
        if pattern in url:
            return url.split(pattern)[-1].split("?")[0]
    
    if len(url) == 11 and "-" not in url:
        return url
    
    return None

def get_video_info(video_id):
    """Get video info using YouTube Data API"""
    api_key, _ = get_credentials()
    
    if not api_key:
        print("Error: YouTube API key not found", file=sys.stderr)
        return None
    
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={api_key}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error: YouTube API: {e}", file=sys.stderr)
        return None
    
    if not data.get("items"):
        print("Error: Video not found", file=sys.stderr)
        return None
    
    item = data["items"][0]
    snippet = item["snippet"]
    stats = item.get("statistics", {})
    
    return {
        "id": video_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "channel_id": snippet.get("channelId", ""),
        "published_at": snippet.get("publishedAt", ""),
        "view_count": stats.get("viewCount", "0"),
        "like_count": stats.get("likeCount", "0"),
        "comment_count": stats.get("commentCount", "0"),
        "thumbnail": snippet.get("thumbnails", {}).get("maxres", {}).get("url", ""),
        "tags": snippet.get("tags", []),
    }

def get_transcript(url, languages=None):
    """Fetch transcript using Apify API"""
    _, api_token = get_credentials()
    
    if not api_token:
        print("Error: Apify API token not found", file=sys.stderr)
        return None
    
    video_id = extract_video_id(url)
    if not video_id:
        print(f"Error: Could not extract video ID from {url}", file=sys.stderr)
        return None
    
    api_url = f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync-get-dataset-items?timeout=120"
    
    if languages:
        data = json.dumps({"videoUrls": [url], "languages": languages})
    else:
        data = json.dumps({"videoUrls": [url], "languages": ["en", "tr", "auto"]})
    
    req = urllib.request.Request(
        api_url,
        data=data.encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error: Apify API: {e}", file=sys.stderr)
        return None
    
    if not result or not isinstance(result, list):
        return None
    
    data = result[0]
    captions = data.get("captions", [])
    
    if not captions or captions[0] is None:
        return None
    
    return captions

def format_output(video_info, transcript=None):
    """Format output for display"""
    if not video_info:
        return "Error: No video information"
    
    output = []
    output.append("=" * 60)
    output.append(f"📺 {video_info['title']}")
    output.append("=" * 60)
    output.append(f"📅 {video_info['published_at'][:10]}")
    output.append(f"👤 {video_info['channel_title']}")
    output.append(f"👁️ {int(video_info['view_count']):,} views")
    output.append(f"👍 {int(video_info['like_count']):,} likes")
    output.append(f"💬 {int(video_info['comment_count']):,} comments")
    output.append("")
    output.append("📝 AÇIKLAMA:")
    output.append("-" * 40)
    desc = video_info['description'][:500]
    if len(video_info['description']) > 500:
        desc += "..."
    output.append(desc)
    output.append("")
    
    if transcript:
        output.append("=" * 60)
        output.append("📄 TRANSCRIPT (Apify)")
        output.append("=" * 60)
        for line in transcript:
            output.append(line)
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(
        description="YouTube Master - Get video info + transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://www.youtube.com/watch?v=VIDEO_ID
  %(prog)s VIDEO_ID --transcript
  %(prog)s VIDEO_ID --transcript --lang tr
  %(prog)s VIDEO_ID --info-only
        """
    )
    parser.add_argument("url", help="YouTube video URL or video ID")
    parser.add_argument("--transcript", "-t", action="store_true",
                       help="Also fetch transcript (uses Apify)")
    parser.add_argument("--lang", "-l", dest="language", action="append",
                       help="Language for transcript (en, tr, auto)")
    parser.add_argument("--info-only", action="store_true",
                       help="Only video info, no transcript")
    
    args = parser.parse_args()
    
    video_id = extract_video_id(args.url)
    if not video_id:
        print(f"Error: Could not extract video ID from {args.url}", file=sys.stderr)
        sys.exit(1)
    
    # Always get video info (free, YouTube API)
    video_info = get_video_info(video_id)
    
    if not video_info:
        print("Error: Could not get video info", file=sys.stderr)
        sys.exit(1)
    
    transcript = None
    
    # Only fetch transcript if requested
    if args.transcript and not args.info_only:
        transcript = get_transcript(args.url, args.language)
    
    print(format_output(video_info, transcript))

if __name__ == "__main__":
    main()
