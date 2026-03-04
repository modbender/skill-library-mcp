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
from typing import Dict

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

def search_tiktok(query: str, search_type: str, api_key: str) -> Dict:
    url = "https://api.scrapecreators.com/v1/tiktok/search/keyword" if search_type == "keyword" else "https://api.scrapecreators.com/v1/tiktok/search/hashtag"
    params = {"query": query} if search_type == "keyword" else {"hashtag": query.replace("#", "")}
    
    data = make_request(url, params, api_key)
    videos = data.get("data", [])
    
    # Sort by views to find the most viral ones
    sorted_videos = sorted(videos, key=lambda v: v.get("stats", {}).get("playCount", 0), reverse=True)
    top_videos = sorted_videos[:5]
    
    return {
        "query": query,
        "type": search_type,
        "top_results": [
            {
                "url": f"https://www.tiktok.com/@{v.get('author', {}).get('uniqueId', 'unknown')}/video/{v.get('item_id', v.get('id', ''))}",
                "author": v.get("author", {}).get("uniqueId", "unknown"),
                "caption": v.get("desc", ""),
                "views": v.get("stats", {}).get("playCount", 0),
                "likes": v.get("stats", {}).get("diggCount", 0)
            } for v in top_videos
        ]
    }

def search_ig_reels(query: str, api_key: str) -> Dict:
    # IG currently supports Reels search by keyword
    url = "https://api.scrapecreators.com/v2/instagram/reels/search"
    params = {"query": query}
    
    data = make_request(url, params, api_key)
    reels = data.get("items", [])
    
    # Sort by play_count
    sorted_reels = sorted(reels, key=lambda r: r.get("play_count", 0), reverse=True)
    top_reels = sorted_reels[:5]
    
    return {
        "query": query,
        "type": "keyword (reels)",
        "top_results": [
            {
                "url": f"https://www.instagram.com/reel/{r.get('code')}/",
                "author": r.get("user", {}).get("username", "unknown"),
                "caption": r.get("caption", {}).get("text", "") if r.get("caption") else "",
                "views": r.get("play_count", 0),
                "likes": r.get("like_count", 0)
            } for r in top_reels
        ]
    }

def main():
    parser = argparse.ArgumentParser(description="Search TikTok and Instagram Reels by keyword or hashtag.")
    parser.add_argument("--platform", choices=["tiktok", "instagram"], required=True)
    parser.add_argument("--type", choices=["keyword", "hashtag"], required=True, help="Note: Instagram currently uses keyword search for Reels.")
    parser.add_argument("--query", required=True, help="The search query (e.g., 'dinner recipes' or 'healthyfood')")
    parser.add_argument("--api-key", help="ScrapeCreators API Key")
    
    args = parser.parse_args()
    
    api_key = get_api_key(args.api_key)
    if not api_key:
        print(json.dumps({"error": "SCRAPE_CREATORS_API_KEY environment variable is required."}), file=sys.stderr)
        sys.exit(1)

    if args.platform == "tiktok":
        data = search_tiktok(args.query, args.type, api_key)
    else:
        # We route IG to reels search regardless of type to focus on video content
        data = search_ig_reels(args.query, api_key)
        
    print(json.dumps({
        "status": "success",
        "platform": args.platform,
        "search_results": data
    }, indent=2))

if __name__ == "__main__":
    main()
