#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///
import argparse
import os
import sys
import json
import requests
from typing import List, Dict

def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("SCRAPE_CREATORS_API_KEY")

def make_request(url: str, params: dict, api_key: str) -> dict:
    headers = {"x-api-key": api_key}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return {}

def scrape_tiktok_competitors(handles: List[str], api_key: str) -> Dict:
    results = {}
    for handle in handles:
        profile = make_request("https://api.scrapecreators.com/v1/tiktok/profile", {"handle": handle}, api_key)
        videos = make_request("https://api.scrapecreators.com/v3/tiktok/profile/videos", {"handle": handle}, api_key)
        
        # Extract basic stats
        stats = profile.get("stats", {})
        video_list = videos.get("data", [])
        
        # Sort videos by play count to find viral hooks
        sorted_videos = sorted(video_list, key=lambda v: v.get("stats", {}).get("playCount", 0), reverse=True)
        top_videos = sorted_videos[:3]
        
        avg_views = sum(v.get("stats", {}).get("playCount", 0) for v in video_list) / len(video_list) if video_list else 0
        
        results[handle] = {
            "followers": stats.get("followerCount", 0),
            "average_recent_views": int(avg_views),
            "top_recent_hooks": [
                {
                    "url": f"https://www.tiktok.com/@{handle}/video/{v.get('id')}",
                    "caption": v.get("desc", ""),
                    "views": v.get("stats", {}).get("playCount", 0)
                } for v in top_videos
            ]
        }
    return results

def scrape_ig_competitors(handles: List[str], api_key: str) -> Dict:
    results = {}
    for handle in handles:
        profile = make_request("https://api.scrapecreators.com/v1/instagram/profile", {"handle": handle}, api_key)
        posts_data = make_request("https://api.scrapecreators.com/v2/instagram/user/posts", {"handle": handle, "trim": "true"}, api_key)
        
        stats = profile.get("edge_followed_by", {}).get("count", 0)
        post_list = posts_data.get("items", [])
        
        # Sort by play_count or like_count
        sorted_posts = sorted(
            post_list, 
            key=lambda p: p.get("play_count", 0) or p.get("like_count", 0), 
            reverse=True
        )
        top_posts = sorted_posts[:3]
        
        results[handle] = {
            "followers": stats,
            "top_recent_hooks": [
                {
                    "url": f"https://www.instagram.com/p/{p.get('code')}/",
                    "caption": p.get("caption", {}).get("text", "") if p.get("caption") else "",
                    "views_or_likes": p.get("play_count") or p.get("like_count", 0)
                } for p in top_posts
            ]
        }
    return results

def main():
    parser = argparse.ArgumentParser(description="Analyze competitor profiles and extract top hooks.")
    parser.add_argument("--platform", choices=["tiktok", "instagram"], required=True)
    parser.add_argument("--handles", nargs="+", required=True, help="List of competitor handles (e.g., @user1 @user2)")
    parser.add_argument("--api-key", help="ScrapeCreators API Key (overrides SCRAPE_CREATORS_API_KEY env var)")
    
    args = parser.parse_args()
    
    api_key = get_api_key(args.api_key)
    if not api_key:
        print(json.dumps({"error": "SCRAPE_CREATORS_API_KEY environment variable is required."}), file=sys.stderr)
        sys.exit(1)

    # Clean handles
    clean_handles = [h.replace("@", "") for h in args.handles]
    
    if args.platform == "tiktok":
        data = scrape_tiktok_competitors(clean_handles, api_key)
    else:
        data = scrape_ig_competitors(clean_handles, api_key)
        
    print(json.dumps({
        "status": "success",
        "platform": args.platform,
        "competitor_analysis": data
    }, indent=2))

if __name__ == "__main__":
    main()
