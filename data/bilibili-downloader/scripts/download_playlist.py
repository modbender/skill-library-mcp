#!/usr/bin/env python3
"""
Bilibili Playlist/Series Downloader Script
Usage: python download_playlist.py <playlist_id> [output_path] [quality]
"""

import os
import sys
from bilibili_api import playlist, sync


def download_playlist(playlist_id, output_path="./", quality=None):
    """Download all videos from a playlist."""
    os.makedirs(output_path, exist_ok=True)

    pl = playlist.Playlist(playlist_id=int(playlist_id))
    videos = sync(pl.get_videos())

    print(f"Found {len(videos)} videos in playlist")

    for i, v in enumerate(videos, 1):
        try:
            video_obj = video.Video(bvid=v["bvid"])
            info = video_obj.get_info()
            title = info["title"][:50].replace("/", "_")

            filename = f"{i:03d}_{title}.mp4"
            output_file = os.path.join(output_path, filename)

            if quality:
                url_info = video_obj.get_download_url(qn=int(quality))
                sync(video_obj.download(output=output_file, url=url_info))
            else:
                sync(video_obj.download(output=output_file))

            print(f"[{i}/{len(videos)}] Downloaded: {title}")
        except Exception as e:
            print(f"[{i}/{len(videos)}] Failed: {v['bvid']} - {e}")

    print(f"\nCompleted: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python download_playlist.py <playlist_id> [output_path] [quality]"
        )
        sys.exit(1)

    playlist_id = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "./playlist"
    quality = sys.argv[3] if len(sys.argv) > 3 else None

    download_playlist(playlist_id, output, quality)
