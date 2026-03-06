#!/usr/bin/env python3
"""
TikTok Bulk Video Downloader
Downloads TikTok videos from a list of URLs in a text file.
"""

import os
import sys
import yt_dlp
from pathlib import Path


def download_tiktok_videos(urls_file, output_folder="downloads"):
    """
    Download TikTok videos from URLs listed in a text file.

    Args:
        urls_file: Path to text file containing TikTok URLs (one per line)
        output_folder: Folder where videos will be saved
    """
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Read URLs from file
    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"Error: File '{urls_file}' not found!")
        print("Please create a text file with TikTok URLs (one per line)")
        sys.exit(1)

    if not urls:
        print(f"No URLs found in '{urls_file}'")
        print("Add TikTok URLs to the file (one per line) and try again")
        sys.exit(1)

    print(f"Found {len(urls)} URL(s) to download")
    print(f"Saving videos to: {os.path.abspath(output_folder)}/\n")

    # yt-dlp options
    ydl_opts = {
        'outtmpl': f'{output_folder}/%(title)s_%(id)s.%(ext)s',
        'format': 'best',
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }

    # Download each video
    success_count = 0
    failed_urls = []

    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] Downloading: {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            success_count += 1
            print(f"✓ Successfully downloaded\n")
        except Exception as e:
            print(f"✗ Failed to download: {e}\n")
            failed_urls.append(url)

    # Summary
    print("=" * 50)
    print(f"Download complete!")
    print(f"Successful: {success_count}/{len(urls)}")
    if failed_urls:
        print(f"Failed: {len(failed_urls)}")
        print("\nFailed URLs:")
        for url in failed_urls:
            print(f"  - {url}")
    print("=" * 50)


def main():
    """Main function to run the downloader."""
    # Default file name
    urls_file = "urls.txt"
    output_folder = "downloads"

    # Check if custom file was provided as argument
    if len(sys.argv) > 1:
        urls_file = sys.argv[1]

    # Check if custom output folder was provided
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]

    print("=" * 50)
    print("TikTok Bulk Video Downloader")
    print("=" * 50)

    download_tiktok_videos(urls_file, output_folder)


if __name__ == "__main__":
    main()
