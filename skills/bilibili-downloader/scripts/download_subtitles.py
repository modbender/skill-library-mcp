#!/usr/bin/env python3
"""
Bilibili Subtitle Downloader Script
Usage: python download_subtitles.py <bvid_or_url> [output_path]
"""

import os
import sys
import json
from bilibili_api import video, sync


def download_subtitles(bvid, output_path="./"):
    """Download subtitles from a Bilibili video."""
    v = video.Video(bvid=bvid)
    os.makedirs(output_path, exist_ok=True)

    subtitles = sync(v.get_subtitle())

    if not subtitles:
        print("No subtitles available for this video")
        return

    for sub in subtitles:
        lang = sub["lan"]
        sub_info = sync(v.get_subtitle(sub["id"]))

        filename = f"{v.get_info()['title'][:30]}_{lang}.json".replace("/", "_")
        output_file = os.path.join(output_path, filename)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sub_info, f, ensure_ascii=False, indent=2)

        print(f"Downloaded subtitle: {output_file} ({lang})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_subtitles.py <bvid> [output_path]")
        sys.exit(1)

    bvid = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "./"

    download_subtitles(bvid, output)
