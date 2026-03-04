#!/usr/bin/env python3
"""
Bilibili Audio Downloader Script
Usage: python download_audio.py <bvid_or_url> [output_path]
"""

import os
import sys
from bilibili_api import video, sync


def download_audio(bvid, output_path="./"):
    """Download audio from a Bilibili video."""
    v = video.Video(bvid=bvid)
    os.makedirs(output_path, exist_ok=True)

    info = v.get_info()
    filename = f"{info['title'][:50]}_audio.mp3".replace("/", "_")
    output_file = os.path.join(output_path, filename)

    sync(v.download_audio(output=output_file))
    print(f"Downloaded audio: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_audio.py <bvid> [output_path]")
        sys.exit(1)

    bvid = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "./"

    download_audio(bvid, output)
