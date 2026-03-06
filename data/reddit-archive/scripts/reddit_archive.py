#!/usr/bin/env python3
"""
Reddit Archive - Download images, GIFs, and videos from Reddit users or subreddits.
Usage: python3 reddit_archive.py -u username | -s subreddit [options]
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

# === CONFIG ===
USER_AGENT = "Mozilla/5.0 (compatible; archiver/1.0)"
API_DELAY = 0.8  # seconds between API calls to avoid 403s

# === ARGS ===
def parse_args():
    p = argparse.ArgumentParser(description="Archive Reddit posts (images, GIFs, videos)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-u", "--user", help="Reddit username")
    g.add_argument("-s", "--subreddit", help="Subreddit name (without r/)")
    p.add_argument("-o", "--output", default=None, help="Output directory")
    p.add_argument("--sort", default="hot", choices=["hot", "new", "rising", "top", "controversial"])
    p.add_argument("--time", default=None, choices=["hour", "day", "week", "month", "year", "all"])
    p.add_argument("--after", default=None, help="Start date (YYYY-MM-DD)")
    p.add_argument("--before", default=None, help="End date (YYYY-MM-DD)")
    p.add_argument("--limit", type=int, default=0, help="Max posts (0=unlimited)")
    p.add_argument("--images", action="store_true", default=True, help="Download images (jpg,png,webp)")
    p.add_argument("--gifs", action="store_true", default=True, help="Download GIFs/videos")
    p.add_argument("--skip-existing", action="store_true", default=True, help="Skip existing files")
    p.add_argument("--workers", type=int, default=4, help="Parallel workers")
    return p.parse_args()

# === HELPERS ===
def get_output_dir(args):
    if args.output:
        return Path(args.output)
    target = args.user or f"r_{args.subreddit}"
    return Path.home() / "temp" / f".reddit_{target}"

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    return path

def date_to_utc(date_str):
    """Convert YYYY-MM-DD to Reddit API after parameter."""
    if not date_str:
        return None
    try:
        from datetime import datetime
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return str(int(dt.timestamp()))
    except:
        return None

def get_posts(args):
    """Fetch posts from Reddit API."""
    if args.user:
        url = f"https://www.reddit.com/user/{args.user}/submitted.json?limit=100&raw_json=1"
    else:
        url = f"https://www.reddit.com/r/{args.subreddit}/{args.sort}.json?limit=100&raw_json=1"
        if args.time:
            url += f"&t={args.time}"
    
    after = None
    all_posts = []
    fetched = 0
    
    while True:
        fetch_url = url
        if after:
            fetch_url += f"&after={after}"
        
        print(f"Fetching: {fetch_url[:80]}...")
        r = requests.get(fetch_url, headers={"User-Agent": USER_AGENT})
        if r.status_code != 200:
            print(f"Error: {r.status_code} - {r.text[:200]}")
            break
        
        data = r.json()
        children = data.get("data", {}).get("children", [])
        if not children:
            break
        
        for child in children:
            post = child.get("data", {})
            all_posts.append(post)
            fetched += 1
            if args.limit and fetched >= args.limit:
                break
        
        after = data.get("data", {}).get("after")
        if not after or (args.limit and fetched >= args.limit):
            break
        
        time.sleep(API_DELAY)
    
    # Filter by date
    if args.after or args.before:
        from datetime import datetime
        filtered = []
        for post in all_posts:
            created = post.get("created_utc", 0)
            post_date = datetime.utcfromtimestamp(created)
            if args.after:
                after_dt = datetime.strptime(args.after, "%Y-%m-%d")
                if post_date < after_dt:
                    continue
            if args.before:
                before_dt = datetime.strptime(args.before, "%Y-%m-%d")
                if post_date > before_dt:
                    continue
            filtered.append(post)
        all_posts = filtered
    
    if args.limit:
        all_posts = all_posts[:args.limit]
    
    print(f"Fetched {len(all_posts)} posts")
    return all_posts

def get_image_url(post):
    """Extract direct image URL from post."""
    url = post.get("url", "")
    
    # Direct images
    if url.startswith("https://i.redd.it/"):
        return url, "image", url.split("/")[-1]
    
    # Imgur
    if "imgur.com" in url and not url.endswith(".gifv"):
        img_id = url.split("/")[-1].split(".")[0]
        ext = "jpg"
        if url.endswith(".png"):
            ext = "png"
        elif url.endswith(".gif"):
            ext = "gif"
        elif url.endswith(".gifv"):
            ext = "gif"
            return f"https://i.imgur.com/{img_id}.gif", "gif", f"{img_id}.gif"
        return f"https://i.imgur.com/{img_id}.{ext}", "image", f"{img_id}.{ext}"
    
    # Gallery
    if post.get("is_gallery"):
        metadata = post.get("media_metadata", {})
        images = []
        for item in metadata.values():
            if item.get("status") == "ready":
                img_url = item.get("s", {}).get("u", "").replace("&amp;", "&")
                if img_url:
                    images.append(img_url)
        return images, "gallery", None
    
    return None, None, None

def get_video_url(post):
    """Extract video/GIF URL from post."""
    url = post.get("url", "")
    
    # v.redd.it
    if "v.redd.it" in url:
        media = post.get("media", {}) or post.get("secure_media", {})
        if "reddit_video" in media:
            video_url = media["reddit_video"].get("fallback_url", "")
            if video_url:
                return video_url, "video"
    
    # redgifs
    if "redgifs.com" in url:
        return url, "video"
    
    # gfycat
    if "gfycat.com" in url:
        return url, "gif"
    
    # imgur gifv
    if "imgur.com" in url and url.endswith(".gifv"):
        img_id = url.split("/")[-1].replace(".gifv", "")
        return f"https://i.imgur.com/{img_id}.gif", "gif"
    
    # Direct mp4/gif
    if url.endswith(".mp4") or url.endswith(".gif"):
        return url, "video" if url.endswith(".mp4") else "gif"
    
    return None, None

def is_image_ext(url):
    return any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"])

def is_video_ext(url):
    return any(url.lower().endswith(ext) for ext in [".mp4", ".gif", ".webm"])

def download_file(url, path, session):
    """Download a single file."""
    try:
        r = session.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

def download_with_ytdlp(url, path):
    """Download video using yt-dlp."""
    import subprocess
    ytdlp = os.environ.get("YTDLP_PATH", "yt-dlp")
    try:
        subprocess.run([ytdlp, "-o", str(path), "--no-warnings", url], 
                       capture_output=True, timeout=120, check=True)
        return True
    except Exception as e:
        print(f"yt-dlp error for {url}: {e}")
    return False

def process_post(post, dirs, args):
    """Process a single post - returns list of downloaded files."""
    post_id = post.get("id", "unknown")
    subreddit = post.get("subreddit", "unknown")
    target = args.user or subreddit
    downloaded = []
    
    urls_to_download = []
    
    # Images
    if args.images:
        img_urls, img_type, _ = get_image_url(post)
        if img_type == "gallery" and isinstance(img_urls, list):
            for i, img_url in enumerate(img_urls):
                ext = Path(img_url).suffix or ".jpg"
                filename = f"{target}_{post_id}_gallery_{i}{ext}"
                urls_to_download.append((img_url, dirs["pictures"] / filename, False))
        elif img_urls:
            ext = Path(img_urls).suffix or ".jpg"
            filename = f"{target}_{post_id}{ext}"
            urls_to_download.append((img_urls, dirs["pictures"] / filename, False))
    
    # Videos/GIFs
    if args.gifs:
        video_url, video_type = get_video_url(post)
        if video_url:
            if "redgifs.com" in video_url or "gfycat.com" in video_url:
                # Use yt-dlp for these
                filename = f"{target}_{post_id}.mp4"
                urls_to_download.append((video_url, dirs["videos"] / filename, True))
            elif is_video_ext(video_url):
                ext = Path(video_url).suffix or ".mp4"
                filename = f"{target}_{post_id}{ext}"
                urls_to_download.append((video_url, dirs["videos"] / filename, True))
    
    # Download
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    
    for url, path, use_ytdlp in urls_to_download:
        if args.skip_existing and path.exists():
            print(f"Skipping existing: {path.name}")
            continue
        
        print(f"  Downloading: {url[:60]}...")
        
        success = False
        if use_ytdlp:
            success = download_with_ytdlp(url, path)
        else:
            success = download_file(url, path, session)
        
        if success:
            downloaded.append(str(path))
    
    return downloaded

def main():
    args = parse_args()
    
    output_dir = get_output_dir(args)
    ensure_dir(output_dir)
    ensure_dir(output_dir / "Pictures")
    ensure_dir(output_dir / "Videos")
    
    dirs = {
        "pictures": output_dir / "Pictures",
        "videos": output_dir / "Videos"
    }
    
    print(f"Output: {output_dir}")
    print(f"Fetching posts...")
    
    posts = get_posts(args)
    print(f"Processing {len(posts)} posts...")
    
    all_downloaded = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_post, post, dirs, args): post for post in posts}
        for future in as_completed(futures):
            try:
                downloaded = future.result()
                all_downloaded.extend(downloaded)
            except Exception as e:
                print(f"Error processing post: {e}")
    
    print(f"\nDone! Downloaded {len(all_downloaded)} files to {output_dir}")

if __name__ == "__main__":
    main()
