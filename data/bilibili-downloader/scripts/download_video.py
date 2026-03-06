#!/usr/bin/env python3
"""
Bilibili Video Downloader Script
Usage: python download_video.py <bvid_or_url> [output_path] [quality]
Quality: 127=8K, 126=杜比, 125=1080P+, 120=1080P, 116=4K, 112=1080P, 80=1080P, 74=720P, 64=480P, 32=360P
"""

import os
import sys
from bilibili_api import video, sync


def download_video(bvid, output_path="./", quality=None):
    """Download a single Bilibili video."""
    v = video.Video(bvid=bvid)
    os.makedirs(output_path, exist_ok=True)

    filename = f"{v.get_info()['title'][:50]}.mp4".replace("/", "_")
    output_file = os.path.join(output_path, filename)

    if quality:
        url_info = v.get_download_url(qn=int(quality))
        sync(v.download(output=output_file, url=url_info))
    else:
        sync(v.download(output=output_file))

    print(f"Downloaded: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    bvid = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "./"
    quality = sys.argv[3] if len(sys.argv) > 3 else None

    download_video(bvid, output, quality)
