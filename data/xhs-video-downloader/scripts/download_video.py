#!/usr/bin/env python3
"""
Xiaohongshu Video Downloader

Downloads videos from Xiaohongshu (小红书) by extracting the real CDN URL.

Usage:
    python3 download_video.py <xiaohongshu_url> [output_dir]

Example:
    python3 download_video.py "https://www.xiaohongshu.com/explore/69a16fc7000000000e00ca28"
    python3 download_video.py "https://www.xiaohongshu.com/explore/69a16fc7000000000e00ca28" ./videos

Requirements:
    - requests: pip install requests
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' is required. Install with: pip install requests")
    sys.exit(1)


DEFAULT_OUTPUT_DIR = Path.home() / "Downloads" / "xiaohongshu"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.xiaohongshu.com/",
    "Accept": "*/*",
}


def extract_video_url(html_content: str) -> Optional[str]:
    """
    Extract the real CDN video URL from Xiaohongshu page HTML.

    Xiaohongshu embeds video URLs in the page source, but the <video> element
    uses a blob URL. We need to find the actual .mp4 URL.

    Args:
        html_content: The full HTML source of the page

    Returns:
        The video URL if found, None otherwise
    """
    # Pattern 1: Direct .mp4 URL
    mp4_pattern = r'https?://[^\s"<>]+\.mp4[^\s"<>]*'
    mp4_matches = re.findall(mp4_pattern, html_content)
    if mp4_matches:
        # Prefer xhscdn URLs
        for url in mp4_matches:
            if "xhscdn" in url:
                return url.split('"')[0].split("'")[0]
        return mp4_matches[0].split('"')[0].split("'")[0]

    # Pattern 2: xhscdn domain URLs (might be .m3u8 or other formats)
    xhscdn_pattern = r'https?://[^\s"<>]+xhscdn[^\s"<>]*'
    xhscdn_matches = re.findall(xhscdn_pattern, html_content)
    if xhscdn_matches:
        # Filter for video URLs
        for url in xhscdn_matches:
            if any(ext in url for ext in [".mp4", ".m3u8", "stream"]):
                return url.split('"')[0].split("'")[0]

    return None


def download_video(url: str, output_path: Path) -> bool:
    """
    Download a video from URL to the specified path.

    Args:
        url: The video URL to download
        output_path: Where to save the video file

    Returns:
        True if download succeeded, False otherwise
    """
    print(f"Downloading: {url}")

    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end="", flush=True)

        print(f"\nSaved to: {output_path}")
        return True

    except requests.RequestException as e:
        print(f"Download failed: {e}")
        return False


def fetch_page_content(page_url: str) -> Optional[str]:
    """
    Fetch the HTML content of a Xiaohongshu page.

    Note: Xiaohongshu is a SPA (Single Page Application), so this may not
    return the full video URL. For best results, use browser automation.

    Args:
        page_url: The Xiaohongshu page URL

    Returns:
        HTML content if successful, None otherwise
    """
    try:
        response = requests.get(page_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch page: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Download videos from Xiaohongshu (小红书)"
    )
    parser.add_argument("url", help="Xiaohongshu page URL")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--filename",
        help="Output filename (default: auto-generated from URL)",
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch page content
    print(f"Fetching page: {args.url}")
    html_content = fetch_page_content(args.url)

    if not html_content:
        print("Failed to get page content. Try using browser automation instead.")
        sys.exit(1)

    # Extract video URL
    video_url = extract_video_url(html_content)

    if not video_url:
        print("No video URL found in page. The page may require JavaScript rendering.")
        print("Tip: Use browser automation (Playwright/Puppeteer) to get the full page content.")
        sys.exit(1)

    # Generate filename
    if args.filename:
        filename = args.filename
        if not filename.endswith(".mp4"):
            filename += ".mp4"
    else:
        # Extract note ID from URL
        note_id_match = re.search(r"/explore/([a-f0-9]+)", args.url)
        if note_id_match:
            filename = f"xiaohongshu_{note_id_match.group(1)}.mp4"
        else:
            filename = "xiaohongshu_video.mp4"

    output_path = output_dir / filename

    # Download
    success = download_video(video_url, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
