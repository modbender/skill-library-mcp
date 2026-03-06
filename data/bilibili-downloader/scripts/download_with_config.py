#!/usr/bin/env python3
"""
Bilibili Downloader with Config
Usage: python download_with_config.py <bvid> [config_file]
"""

import os
import sys
import json
from bilibili_api import video, sync


def load_config(config_file="config.json"):
    """Load configuration from JSON file."""
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            return json.load(f)
    return {}


def download_with_config(bvid, config=None):
    """Download video with configuration."""
    config = config or {}
    v = video.Video(bvid=bvid)

    info = v.get_info()
    title = info["title"][:50].replace("/", "_")

    output_dir = config.get("output_directory", "./downloads")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"{title}.mp4")

    quality = config.get("default_quality")
    if quality:
        url_info = v.get_download_url(qn=quality)
        sync(v.download(output=output_file, url=url_info))
    else:
        sync(v.download(output=output_file))

    print(f"Downloaded: {output_file}")

    if config.get("download_cover", True):
        cover_file = os.path.join(output_dir, f"{title}_cover.jpg")
        sync(v.download_cover(output=cover_file))
        print(f"Cover: {cover_file}")

    if config.get("download_subtitles", True):
        subtitles_dir = os.path.join(output_dir, "subtitles")
        os.makedirs(subtitles_dir, exist_ok=True)
        subtitles = sync(v.get_subtitle())
        for sub in subtitles:
            sub_info = sync(v.get_subtitle(sub["id"]))
            sub_file = os.path.join(subtitles_dir, f"{title}_{sub['lan']}.json")
            with open(sub_file, "w", encoding="utf-8") as f:
                json.dump(sub_info, f, ensure_ascii=False, indent=2)
            print(f"Subtitle: {sub_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_with_config.py <bvid> [config.json]")
        sys.exit(1)

    bvid = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else "config.json"
    config = load_config(config_file)

    download_with_config(bvid, config)
