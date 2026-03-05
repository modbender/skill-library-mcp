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
        return {"error": str(e)}

def lookup_tiktok_profile(handle: str, api_key: str) -> Dict:
    profile_data = make_request("https://api.scrapecreators.com/v1/tiktok/profile", {"handle": handle}, api_key)
    
    if "error" in profile_data:
        return profile_data
        
    stats = profile_data.get("stats", {})
    user = profile_data.get("user", {})
    
    return {
        "platform": "tiktok",
        "handle": handle,
        "name": user.get("nickname", ""),
        "bio": user.get("signature", ""),
        "followers": stats.get("followerCount", 0),
        "following": stats.get("followingCount", 0),
        "likes": stats.get("heartCount", 0),
        "videos": stats.get("videoCount", 0),
        "raw_data": profile_data
    }

def lookup_ig_profile(handle: str, api_key: str) -> Dict:
    profile_data = make_request("https://api.scrapecreators.com/v1/instagram/profile", {"handle": handle}, api_key)
    
    if "error" in profile_data:
        return profile_data
        
    return {
        "platform": "instagram",
        "handle": handle,
        "name": profile_data.get("full_name", ""),
        "bio": profile_data.get("biography", ""),
        "followers": profile_data.get("edge_followed_by", {}).get("count", 0),
        "following": profile_data.get("edge_follow", {}).get("count", 0),
        "posts": profile_data.get("edge_owner_to_timeline_media", {}).get("count", 0),
        "raw_data": profile_data
    }

def main():
    parser = argparse.ArgumentParser(description="Lookup a creator's profile on TikTok or Instagram.")
    parser.add_argument("--platform", choices=["tiktok", "instagram"], required=True)
    parser.add_argument("--handle", required=True, help="The social media handle (e.g., @user)")
    parser.add_argument("--api-key", help="ScrapeCreators API Key")
    
    args = parser.parse_args()
    
    api_key = get_api_key(args.api_key)
    if not api_key:
        print(json.dumps({"error": "SCRAPE_CREATORS_API_KEY environment variable is required."}), file=sys.stderr)
        sys.exit(1)

    clean_handle = args.handle.replace("@", "")

    if args.platform == "tiktok":
        data = lookup_tiktok_profile(clean_handle, api_key)
    else:
        data = lookup_ig_profile(clean_handle, api_key)
        
    print(json.dumps({
        "status": "success",
        "profile_details": data
    }, indent=2))

if __name__ == "__main__":
    main()
