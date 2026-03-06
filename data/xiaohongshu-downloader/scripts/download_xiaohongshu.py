#!/usr/bin/env python3
"""
Xiaohongshu (小红书/RedNote) Video Downloader v2.0
Downloads videos from Xiaohongshu and optionally produces a full resource pack:
video + audio + subtitles + transcript + AI summary.
"""

import argparse
import subprocess
import sys
import json
import re
import os
import glob as globmod
from pathlib import Path


def check_yt_dlp():
    """Check if yt-dlp is installed."""
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, check=True)
        print(f"yt-dlp version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: yt-dlp is not installed.")
        print("Install it with: brew install yt-dlp (macOS) or pip install yt-dlp")
        return False


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg is not installed.")
        print("Install it with: brew install ffmpeg (macOS)")
        return False


def validate_url(url):
    """Validate that the URL is a Xiaohongshu URL."""
    patterns = [
        r'https?://www\.xiaohongshu\.com/(?:explore|discovery/item)/[\da-f]+',
        r'https?://xhslink\.com/',
    ]
    for pattern in patterns:
        if re.search(pattern, url):
            return True
    return False


def get_video_info(url, browser="chrome"):
    """Get video information without downloading."""
    cmd = ["yt-dlp", "--dump-json", "--no-playlist"]
    if browser and browser != "none":
        cmd.extend(["--cookies-from-browser", browser])
    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        if "Unable to extract initial state" in stderr:
            print("Error: Anti-scraping CAPTCHA triggered.")
            print("Solution: Open the URL in your browser, solve the CAPTCHA, then retry.")
        elif "No video formats found" in stderr:
            print("Error: No video formats found.")
            print("Solution: Make sure you're logged into xiaohongshu.com in your browser.")
        else:
            print(f"Error getting video info: {stderr}")
        return None


def list_formats(url, browser="chrome"):
    """List all available formats for the video."""
    cmd = ["yt-dlp", "--list-formats", "--no-playlist"]
    if browser and browser != "none":
        cmd.extend(["--cookies-from-browser", browser])
    cmd.append(url)
    subprocess.run(cmd)


def sanitize_title(title):
    """Sanitize the title for use as a directory name."""
    # Remove characters invalid in filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
    # Collapse whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    # Truncate to reasonable length
    if len(sanitized) > 100:
        sanitized = sanitized[:100].rstrip()
    return sanitized or "untitled"


def extract_audio(video_path, output_dir):
    """Extract MP3 audio from a video file using ffmpeg.

    Args:
        video_path: Path to the input video file.
        output_dir: Directory to save audio.mp3.

    Returns:
        Path to the extracted audio file, or None on failure.
    """
    audio_path = os.path.join(output_dir, "audio.mp3")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn",                    # no video
        "-acodec", "libmp3lame",  # MP3 codec
        "-q:a", "2",              # high quality (~190 kbps VBR)
        "-y",                     # overwrite
        audio_path,
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Audio extracted: {audio_path}")
        return audio_path
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e.stderr}")
        return None


def download_subtitles(url, output_dir, browser="chrome", audio_path=None):
    """Three-tier subtitle acquisition strategy.

    1. Try manual subtitles via yt-dlp --write-subs
    2. Try auto-generated subtitles via yt-dlp --write-auto-subs
    3. Fall back to local Whisper transcription via parallel_transcribe.py

    Args:
        url: Video URL.
        output_dir: Directory to save subtitle files.
        browser: Browser for cookie extraction.
        audio_path: Path to audio file (for Whisper fallback).

    Returns:
        Path to the VTT subtitle file, or None on failure.
    """
    vtt_path = os.path.join(output_dir, "subtitle.vtt")
    temp_prefix = os.path.join(output_dir, "temp_sub")

    # --- Strategy 1: Manual subtitles ---
    print("Subtitle strategy 1/3: Trying manual subtitles...")
    cmd = [
        "yt-dlp",
        "--write-subs",
        "--sub-lang", "zh,en,zh-Hans,zh-CN",
        "--sub-format", "vtt",
        "--skip-download",
        "--no-playlist",
        "-o", f"{temp_prefix}.%(ext)s",
    ]
    if browser and browser != "none":
        cmd.extend(["--cookies-from-browser", browser])
    cmd.append(url)

    subprocess.run(cmd, capture_output=True, text=True)
    found = _find_and_rename_vtt(output_dir, "temp_sub", vtt_path)
    if found:
        print(f"Manual subtitles found: {vtt_path}")
        return vtt_path

    # --- Strategy 2: Auto-generated subtitles ---
    print("Subtitle strategy 2/3: Trying auto-generated subtitles...")
    cmd = [
        "yt-dlp",
        "--write-auto-subs",
        "--sub-lang", "zh,en,zh-Hans,zh-CN",
        "--sub-format", "vtt",
        "--skip-download",
        "--no-playlist",
        "-o", f"{temp_prefix}.%(ext)s",
    ]
    if browser and browser != "none":
        cmd.extend(["--cookies-from-browser", browser])
    cmd.append(url)

    subprocess.run(cmd, capture_output=True, text=True)
    found = _find_and_rename_vtt(output_dir, "temp_sub", vtt_path)
    if found:
        print(f"Auto-generated subtitles found: {vtt_path}")
        return vtt_path

    # --- Strategy 3: Whisper local transcription ---
    print("Subtitle strategy 3/3: Falling back to Whisper transcription...")
    if not audio_path or not os.path.exists(audio_path):
        print("Warning: No audio file available for Whisper transcription.")
        return None

    script_dir = os.path.dirname(os.path.abspath(__file__))
    transcribe_script = os.path.join(script_dir, "parallel_transcribe.py")

    if not os.path.exists(transcribe_script):
        print("Warning: parallel_transcribe.py not found.")
        return None

    # Try uv run first, then fall back to direct python
    cmd_uv = ["uv", "run", transcribe_script, audio_path, "-o", output_dir]
    cmd_py = [sys.executable, transcribe_script, audio_path, "-o", output_dir]

    try:
        subprocess.run(cmd_uv, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("uv not available, trying direct Python execution...")
        try:
            subprocess.run(cmd_py, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Whisper transcription failed: {e}")
            return None

    if os.path.exists(vtt_path):
        print(f"Whisper transcription complete: {vtt_path}")
        return vtt_path

    print("Warning: Whisper transcription did not produce subtitle.vtt")
    return None


def _find_and_rename_vtt(output_dir, prefix, target_path):
    """Find any VTT files matching the prefix and rename to target."""
    pattern = os.path.join(output_dir, f"{prefix}*.vtt")
    matches = globmod.glob(pattern)
    if matches:
        # Pick the first match
        os.rename(matches[0], target_path)
        # Clean up any other temp subtitle files
        for f in globmod.glob(os.path.join(output_dir, f"{prefix}*")):
            try:
                os.remove(f)
            except OSError:
                pass
        return True
    return False


def generate_transcript(vtt_path, output_dir):
    """Strip timestamps from VTT to produce a plain text transcript.

    Args:
        vtt_path: Path to the VTT subtitle file.
        output_dir: Directory to save transcript.txt.

    Returns:
        Path to the transcript file, or None on failure.
    """
    transcript_path = os.path.join(output_dir, "transcript.txt")
    try:
        with open(vtt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        text_lines = []
        seen = set()
        for line in lines:
            line = line.strip()
            # Skip WEBVTT header, timestamps, numeric cue IDs, empty lines
            if not line:
                continue
            if line.startswith("WEBVTT"):
                continue
            if line.startswith("NOTE"):
                continue
            if re.match(r'^\d+$', line):
                continue
            if re.match(r'\d{2}:\d{2}[\.:]\d{2}', line):
                continue
            # Remove VTT inline tags like <c>, </c>, <00:01:02.345>, etc.
            cleaned = re.sub(r'<[^>]+>', '', line).strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                text_lines.append(cleaned)

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write("\n".join(text_lines) + "\n")

        print(f"Transcript generated: {transcript_path}")
        return transcript_path
    except Exception as e:
        print(f"Error generating transcript: {e}")
        return None


def download_video(url, output_path=None, quality="best", browser="chrome",
                   audio_only=False, full_mode=False, summary_mode=False):
    """
    Download a Xiaohongshu video, optionally as a full resource pack.

    Args:
        url: Xiaohongshu video URL
        output_path: Directory to save the video
        quality: Quality setting (best, 1080p, 720p, 480p)
        browser: Browser to extract cookies from
        audio_only: Download only audio
        full_mode: Enable full resource pack (video + audio + subtitles + transcript)
        summary_mode: Flag that summary.md is requested (handled by SKILL.md / Claude)
    """
    if not check_yt_dlp():
        return False

    if full_mode and not check_ffmpeg():
        return False

    if output_path is None:
        output_path = os.path.expanduser("~/Downloads")

    # Get video info first
    info = get_video_info(url, browser)
    title = "Unknown"
    duration = 0
    uploader = "Unknown"
    if info:
        title = info.get("title", "Unknown")
        duration = int(info.get("duration", 0) or 0)
        uploader = info.get("uploader", "Unknown")
        if duration:
            print(f"Title: {title}")
            print(f"Duration: {duration // 60}:{duration % 60:02d}")
            print(f"Uploader: {uploader}\n")
        else:
            print(f"Title: {title}")
            print(f"Uploader: {uploader}\n")

    # Determine output directory
    if full_mode:
        safe_title = sanitize_title(title)
        output_dir = os.path.join(output_path, safe_title)
        os.makedirs(output_dir, exist_ok=True)
        video_output = os.path.join(output_dir, "video.%(ext)s")
    else:
        output_dir = output_path
        video_output = os.path.join(output_path, "%(title)s [%(id)s].%(ext)s")

    # Build yt-dlp command
    cmd = ["yt-dlp"]

    if browser and browser != "none":
        cmd.extend(["--cookies-from-browser", browser])

    if audio_only:
        cmd.extend([
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
        ])
    else:
        if quality == "best":
            format_string = "bestvideo+bestaudio/best"
        else:
            height = quality.replace("p", "")
            format_string = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

        cmd.extend([
            "-f", format_string,
            "--merge-output-format", "mp4",
        ])

    cmd.extend([
        "-o", video_output,
        "--no-playlist",
    ])
    cmd.append(url)

    print(f"URL: {url}")
    print(f"Quality: {quality}")
    print(f"Format: {'mp3 (audio only)' if audio_only else 'mp4'}")
    print(f"Mode: {'full resource pack' if full_mode else 'video only'}")
    print(f"Cookies: from {browser}" if browser != "none" else "Cookies: none")
    print(f"Output: {output_dir}\n")

    # Download video
    try:
        subprocess.run(cmd, check=True)
        print(f"\nVideo download complete!")
    except subprocess.CalledProcessError as e:
        print(f"\nError downloading video: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you're logged into xiaohongshu.com in your browser")
        print("2. Try copying a fresh share link (tokens expire)")
        print("3. If CAPTCHA appears, open the URL in browser first")
        return False

    if not full_mode:
        print(f"Saved to: {output_dir}")
        return True

    # --- Full resource pack mode ---
    # Find the downloaded video file
    video_path = None
    for ext in ["mp4", "mkv", "webm"]:
        candidate = os.path.join(output_dir, f"video.{ext}")
        if os.path.exists(candidate):
            video_path = candidate
            break

    if not video_path:
        print("Warning: Could not find downloaded video file for further processing.")
        return True

    # Step: Extract audio
    print("\n--- Extracting audio ---")
    audio_path = extract_audio(video_path, output_dir)

    # Step: Get subtitles
    print("\n--- Acquiring subtitles ---")
    vtt_path = download_subtitles(url, output_dir, browser, audio_path)

    # Step: Generate transcript from subtitles
    if vtt_path:
        print("\n--- Generating transcript ---")
        generate_transcript(vtt_path, output_dir)

    # If summary mode requested, write metadata for Claude to use
    if summary_mode:
        meta_path = os.path.join(output_dir, ".meta.json")
        meta = {
            "title": title,
            "url": url,
            "duration": f"{duration // 60}:{duration % 60:02d}" if duration else "unknown",
            "platform": "Xiaohongshu (小红书)",
            "uploader": uploader,
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"\nMetadata saved: {meta_path}")
        print("Summary mode enabled — Claude will generate summary.md using the transcript.")

    # Print summary
    print(f"\n{'='*50}")
    print(f"Resource pack saved to: {output_dir}")
    print(f"{'='*50}")
    for fname in ["video.mp4", "audio.mp3", "subtitle.vtt", "transcript.txt"]:
        fpath = os.path.join(output_dir, fname)
        if os.path.exists(fpath):
            size_mb = os.path.getsize(fpath) / (1024 * 1024)
            print(f"  {fname:20s} {size_mb:>8.1f} MB")
        else:
            print(f"  {fname:20s} (not generated)")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Download Xiaohongshu (小红书) videos using yt-dlp"
    )
    parser.add_argument("url", help="Xiaohongshu video URL (explore, discovery, or xhslink.com)")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output directory (default: ~/Downloads)"
    )
    parser.add_argument(
        "-q", "--quality",
        default="best",
        choices=["best", "1080p", "720p", "480p"],
        help="Video quality (default: best)"
    )
    parser.add_argument(
        "--browser",
        default="chrome",
        choices=["chrome", "firefox", "safari", "none"],
        help="Browser to extract cookies from (default: chrome)"
    )
    parser.add_argument(
        "-a", "--audio-only",
        action="store_true",
        help="Download only audio as MP3"
    )
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List available formats without downloading"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full resource pack: video + audio + subtitles + transcript"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Enable AI summary mode (saves metadata for Claude to generate summary.md)"
    )

    args = parser.parse_args()

    # Validate URL
    if not validate_url(args.url):
        print("Warning: URL does not match known Xiaohongshu patterns.")
        print("Supported formats:")
        print("  - https://www.xiaohongshu.com/explore/<id>")
        print("  - https://www.xiaohongshu.com/discovery/item/<id>")
        print("  - http://xhslink.com/a/<id>")
        print("Proceeding anyway...\n")

    if args.list_formats:
        list_formats(args.url, args.browser)
        return

    # --summary implies --full
    if args.summary:
        args.full = True

    success = download_video(
        url=args.url,
        output_path=args.output,
        quality=args.quality,
        browser=args.browser,
        audio_only=args.audio_only,
        full_mode=args.full,
        summary_mode=args.summary,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
