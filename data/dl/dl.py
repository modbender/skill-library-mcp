#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "loguru>=0.7.3",
#     "python-slugify>=8.0.4",
#     "yt-dlp",
# ]
# ///

import argparse
import json
import os
import shutil
import sys
from enum import Enum
from pathlib import Path
import tempfile
from typing import Any
from urllib.parse import urlparse
from loguru import logger

import yt_dlp

MAX_VIDEO_SIZE = 2_000 * 1024 * 1024  # 2000M
MAX_AUDIO_SIZE = 30 * 1024 * 1024  # 30M
PLAYLIST_LIMIT = 30


HERE = Path(__file__).parent


def get_dir(candidates: list[str], default: Path = HERE) -> Path:
    for candidate in candidates:
        if candidate:
            path = Path(candidate).expanduser().resolve()
            if path.is_dir():
                return path.expanduser().resolve()
    return default


def fmt_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def tee_json(obj: Any, file=sys.stderr) -> Any:
    print(fmt_json(obj), file=file)
    return obj


def slugify_stem(stem: str) -> str:
    # slugify file stem
    from slugify import slugify
    return slugify(
        stem,
        separator="_",
        max_length=100,
        allow_unicode=True,
        word_boundary=True,
        lowercase=False,
    )


def slugify_path(path: Path) -> Path:
    # slugify stem, lowercase suffix
    new_stem = slugify_stem(path.stem)
    new_suffix = path.suffix.lower()
    new_name = f"{new_stem}{new_suffix}"
    return path.with_name(new_name)


def slugify_rename(path: Path) -> Path:
    # rename 1 single path, either file or folder
    new_path = slugify_path(path)
    if new_path != path:
        path.rename(new_path)
    return new_path


def slugify_rename_folder(folder_path: Path) -> Path:
    new_folder_path = slugify_path(folder_path)
    for path in new_folder_path.iterdir():
        if path.is_file():
            slugify_rename(path)
        elif path.is_dir():
            slugify_rename_folder(path)
    return new_folder_path


class MediaKind(Enum):
    VIDEO = "video"
    MUSIC = "music"


class Media:
    pass


class Video(Media):

    def build_options(self, options) -> dict[str, Any]:
        options.update({
            "format": "bestvideo[vcodec^=avc1]+bestaudio/best",
            "max_filesize": MAX_VIDEO_SIZE,
            "merge_output_format": "mp4",
        })
        return options

    def get_out_dir(self) -> Path:
        candidates = [
            os.getenv("DL_VIDEO_DIR"),
            os.getenv("VIDEO_DIR"),
            "~/Movies",
            "~/Videos",
            "~/Downloads",
        ]
        return get_dir(candidates, default=HERE)


class Music(Video):

    def build_options(self, options) -> dict[str, Any]:
        options.update({
            "format": "bestaudio/best",
            "max_filesize": MAX_AUDIO_SIZE,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                    "preferredquality": "192",  # 192kbps
                },
            ],
        })
        return options

    def get_out_dir(self) -> Path:
        candidates = [
            os.getenv("DL_MUSIC_DIR"),
            os.getenv("MUSIC_DIR"),
            "~/Music",
            "~/Audio",
            "~/Downloads",
        ]
        return get_dir(candidates, default=HERE)


class Single:
    is_playlist = False

    def build_options(self, options) -> dict[str, Any]:
        options.update({
            "noplaylist": True,
            "outtmpl": {"default": "%(title).240B.%(ext)s"},
        })
        return options

    def get_slugified_path(self, tmp_dir: Path) -> Path:
        # find single file item in root, slugify it, return new path
        for path in tmp_dir.iterdir():
            if path.is_file():
                return slugify_rename(path)
        raise ValueError(f"No single file found in {tmp_dir}")

    def move_to_out_dir(self, tmp_dir: Path, out_dir: Path) -> Path:
        file_path = self.get_slugified_path(tmp_dir)
        assert file_path.is_file(), f"Expected a file, got {file_path}"
        out_path = out_dir / file_path.name
        logger.debug(f"Moving {file_path} to {out_path}")
        return shutil.move(file_path, out_path)


class Playlist(Single):
    is_playlist = True

    def build_options(self, options) -> dict[str, Any]:
        options.update({
            "noplaylist": False,
            "outtmpl": {"default": "%(playlist_title)s/%(title).240B.%(ext)s"},
            "max_downloads": 30,
        })
        return options

    def get_slugified_path(self, tmp_dir):
        # find single folder item in root, slugify it plus all files in it, return new folder path
        for path in tmp_dir.iterdir():
            if path.is_dir():
                return slugify_rename_folder(path)
        raise ValueError(f"No single folder found in {tmp_dir}")

    def move_to_out_dir(self, tmp_dir: Path, out_dir: Path) -> Path:
        dir_path = self.get_slugified_path(tmp_dir)
        assert dir_path.is_dir(), f"Expected a dir, got {dir_path}"
        out_path = out_dir / dir_path.name
        out_path.mkdir(parents=True, exist_ok=True)
        # move file one by one, avoid nested folders
        for file_path in dir_path.iterdir():
            logger.debug(f"Moving {file_path} to {out_path/file_path.name}")
            shutil.move(file_path, out_path/file_path.name)
        return out_path


class Downloader:

    def __init__(self, args):
        self.args = args
        self.url = args.url
        self.verbose = args.verbose
        self.dry_run = args.dry_run
        self.music = args.music
        self.video = args.video
        self.info = {}
        self.media = None
        self.mode = None

    def detect_kind(self, info: dict[str, Any]) -> MediaKind:
        host = (urlparse(self.url).hostname or "").lower()
        if "music." in host:
            return MediaKind.MUSIC

        ie_key = (info.get("extractor_key") or info.get("extractor") or "").lower()
        if "music" in ie_key or "soundcloud" in ie_key or "spotify" in ie_key:
            return MediaKind.MUSIC

        categories = [c.lower() for c in info.get("categories") or []]
        if any("music" in cat for cat in categories):
            return MediaKind.MUSIC

        if info.get("track") or info.get("artist") or info.get("album"):
            return MediaKind.MUSIC

        return MediaKind.VIDEO

    def detect_playlist(self, info: dict[str, Any]) -> bool:
        if "/playlist?" in self.url.lower():
            return True
        entry_type = info.get("_type")
        if entry_type in {"playlist", "multi_video", "multi_track", "multi_song"}:
            return True
        if "entries" in info:
            return True
        return bool(info.get("playlist_count"))

    def extract_info(self) -> dict[str, Any]:
        probe_opts = {
            "quiet": True,
            "skip_download": True,
            "ignoreerrors": True,
            "noplaylist": False,
            "extract_flat": "discard_in_playlist",
        }
        with yt_dlp.YoutubeDL(probe_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)

        id = info.get("id")
        if self.verbose:
            with open(f'info-{id}.json', 'w') as f:
                tee_json(info, file=f)

        return info

    def get_media_kind(self, info: dict[str, Any]) -> MediaKind:
        if self.music:
            return MediaKind.MUSIC
        if self.video:
            return MediaKind.VIDEO
        return self.detect_kind(info)

    def get_cookies_file(self):
        # pass cookie to yt-dlp if provided
        candidates = [
            HERE / ".cookies.txt",
            os.getenv("DL_COOKIES_FILE"),
            os.getenv("COOKIES_FILE"),
            "~/.cookies.txt",
        ]
        return get_dir(candidates, default=None)

    def build_options(self):
        self.info = self.extract_info()
        kind = self.get_media_kind(self.info)
        self.media = Music() if kind is MediaKind.MUSIC else Video()
        self.mode = Playlist() if self.detect_playlist(self.info) else Single()
        # download into a tmp dir first, then slug and move back to out_dir
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="dl_"))
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        options = {
            "paths": {"home": str(self.tmp_dir)},
            "concurrent_fragment_downloads": 4,
            "retries": 3,
        }
        cookie_file = self.get_cookies_file()
        if cookie_file:
            options["cookiefile"] = str(cookie_file)
        if self.verbose:
            options["verbose"] = True
        else:
            options["quiet"] = True
            options["no_warnings"] = True
        self.media.build_options(options)
        self.mode.build_options(options)
        return options

    def download(self, options: dict[str, Any]) -> None:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([self.url])
        return self.move_to_out_dir()

    def slugify(self) -> None:
        # slugify the tmp_dir
        return slugify_rename_folder(self.tmp_dir)

    def get_out_dir(self) -> Path:
        if self.args.out_dir:
            out_dir = Path(self.args.out_dir).expanduser().resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            return out_dir
        # if out_dir not specified, use the media type's default out_dir
        return self.media.get_out_dir()

    def move_to_out_dir(self):
        # get sub items in tmp_dir, move into out_dir, no nested folders
        return self.mode.move_to_out_dir(self.tmp_dir, self.get_out_dir())


def cli():
    parser = argparse.ArgumentParser(
        prog="Smart Media Downloader",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("url", help="Media URL to download")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Verbose logging",
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true",
        help="Probe and print the plan without downloading",
    )
    parser.add_argument(
        "-o", "--out_dir",
        help="Output directory",
    )
    parser.add_argument(
        "-M", "--music", action="store_true",
        help="Download Music",
    )
    parser.add_argument(
        "-V", "--video", action="store_true",
        help="Download Video",
    )
    return parser.parse_args()


def main() -> None:
    args = cli()

    logger.remove()
    logger.add(sys.stderr, level="DEBUG" if args.verbose else "INFO")

    dl = Downloader(args)
    options = dl.build_options()
    if args.verbose or args.dry_run:
        tee_json(options)

    if args.dry_run:
        return

    path = dl.download(options)
    # match SKILL.md
    print(f"Saved to: {path}")


if __name__ == "__main__":
    main()
