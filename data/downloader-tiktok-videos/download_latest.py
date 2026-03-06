#!/usr/bin/env python3
"""
Downloader TikTok Videos — download_latest.py
Downloads the latest (or N most recent) video(s) from a TikTok account.

Usage:
    python download_latest.py @username
    python download_latest.py @username --count 3
    python download_latest.py @username --meta-only
    python download_latest.py @username --output ~/Downloads/tiktok
    python download_latest.py https://www.tiktok.com/@user/video/12345

Dependencies:
    Required : yt-dlp  (pip install -U yt-dlp)
    Optional : ffmpeg  (needed for bestvideo+bestaudio merge)

Security note on cookies:
    --cookies-from-browser and --cookies export active session tokens.
    Keep cookies.txt private, never commit it to version control,
    and delete it after use.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def check_ytdlp() -> bool:
    """Check that yt-dlp is installed. Does NOT auto-install — that is the user's decision."""
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
        print(f"✅ yt-dlp {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ yt-dlp not found.")
        print()
        print("   To install it, run ONE of the following commands yourself:")
        print("   pip install -U yt-dlp")
        print("   pip install -U yt-dlp --break-system-packages   (Linux system Python)")
        print("   brew install yt-dlp                             (macOS)")
        print()
        print("   Note: these commands modify your host environment.")
        print("   Run them only if you are comfortable doing so.")
        return False


def normalize_input(raw: str) -> str:
    """Normalize input to a full TikTok URL.

    Accepts:
        @username
        username
        https://www.tiktok.com/@username
        https://www.tiktok.com/@username/video/ID
        https://vm.tiktok.com/shortcode
    """
    raw = raw.strip()
    if raw.startswith("https://"):
        return raw  # Already a full URL; pass through as-is
    username = raw.lstrip("@")
    return f"https://www.tiktok.com/@{username}"


def get_metadata(url: str, count: int = 1) -> list[dict]:
    """Fetch video metadata using --dump-json (one JSON object per line)."""
    cmd = [
        "yt-dlp",
        "--playlist-items", f"1-{count}",
        "--dump-json",   # Correct flag: prints one JSON object per video to stdout
        "--quiet",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️  Metadata error:\n{result.stderr[:400]}")
        return []
    items = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(f"⚠️  Could not parse metadata line: {exc}")
    return items


def print_metadata(meta: dict) -> None:
    """Display a human-readable summary of one video."""
    title    = meta.get("title", "—")[:80]
    date     = meta.get("upload_date", "—")
    duration = meta.get("duration", 0)
    views    = meta.get("view_count")
    likes    = meta.get("like_count")
    url      = meta.get("webpage_url", "—")
    uploader = meta.get("uploader_id", "—")
    tags     = meta.get("tags") or []

    print(f"\n📹 @{uploader}")
    print(f"   Title    : {title}")
    if len(date) == 8:
        print(f"   Date     : {date[:4]}-{date[4:6]}-{date[6:]}")
    else:
        print(f"   Date     : {date}")
    print(f"   Duration : {duration}s")
    print(f"   Views    : {views:,}" if views is not None else "   Views    : —")
    print(f"   Likes    : {likes:,}" if likes is not None else "   Likes    : —")
    print(f"   URL      : {url}")
    if tags:
        print(f"   Hashtags : {' '.join('#' + t for t in tags[:8])}")


def resolve_output_dir(raw: str) -> Path:
    """Expand ~, resolve relative paths, and create the directory."""
    path = Path(raw).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def download_video(
    url: str,
    output_dir: Path,
    count: int = 1,
    archive: str | None = None,
    cookies: str | None = None,
    cookies_from_browser: str | None = None,
) -> bool:
    """Download video(s) to output_dir."""
    template = str(output_dir / "%(uploader_id)s_%(upload_date)s_%(id)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--playlist-items", f"1-{count}",
        "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--output", template,
        "--sleep-interval", "1",
        "--max-sleep-interval", "3",
        "--retries", "3",
    ]

    if "/video/" in url:
        cmd.append("--no-playlist")

    if archive:
        cmd += ["--download-archive", archive]

    if cookies:
        print("⚠️  Cookie file provided — keep cookies.txt private and delete after use.")
        cmd += ["--cookies", cookies]

    if cookies_from_browser:
        print(f"⚠️  Exporting session cookies from {cookies_from_browser} — these are sensitive.")
        cmd += ["--cookies-from-browser", cookies_from_browser]

    cmd.append(url)

    print(f"\n⬇️  Downloading to: {output_dir}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        files = sorted(output_dir.glob("*.mp4"), key=lambda f: f.stat().st_mtime, reverse=True)
        if files:
            size_mb = files[0].stat().st_size / (1024 * 1024)
            print(f"\n✅ Success!")
            print(f"   File : {files[0]}")
            print(f"   Size : {size_mb:.1f} MB")
        return True
    else:
        print(f"\n❌ Download failed (exit code {result.returncode})")
        print("💡 Try updating yt-dlp: yt-dlp -U")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Downloader TikTok Videos — download the latest video(s) from a TikTok account"
    )
    parser.add_argument(
        "target",
        help="@username, profile URL, or direct video URL"
    )
    parser.add_argument(
        "--count", "-n",
        type=int, default=1,
        help="Number of videos to download (default: 1)"
    )
    parser.add_argument(
        "--output", "-o",
        default=".",
        help="Output folder (default: current directory)"
    )
    parser.add_argument(
        "--meta-only",
        action="store_true",
        help="Display metadata only, skip download"
    )
    parser.add_argument(
        "--archive", "-a",
        default=None,
        help="Path to archive file (skips already-downloaded videos)"
    )
    parser.add_argument(
        "--cookies",
        default=None,
        metavar="FILE",
        help="Path to a Netscape-format cookies.txt file (sensitive — keep private)"
    )
    parser.add_argument(
        "--cookies-from-browser",
        default=None,
        metavar="BROWSER",
        help="Export cookies from browser: chrome | firefox | edge (sensitive)"
    )

    args = parser.parse_args()

    if not check_ytdlp():
        sys.exit(1)  # Instructions printed by check_ytdlp()

    url = normalize_input(args.target)
    print(f"\n🎯 Target : {url}")

    print(f"\n📊 Fetching metadata ({args.count} video(s))...")
    metas = get_metadata(url, args.count)
    if not metas:
        sys.exit("❌ Could not retrieve metadata. Check the account name or URL.")
    for meta in metas:
        print_metadata(meta)

    if args.meta_only:
        print("\n✅ Metadata-only mode — no download.")
        return

    output_dir = resolve_output_dir(args.output)
    download_video(
        url=url,
        output_dir=output_dir,
        count=args.count,
        archive=args.archive,
        cookies=args.cookies,
        cookies_from_browser=args.cookies_from_browser,
    )


if __name__ == "__main__":
    main()
