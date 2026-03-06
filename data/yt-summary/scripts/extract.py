#!/usr/bin/env python3
"""Extract YouTube video transcript and metadata via TranscriptAPI.com."""

import argparse
import json
import os
import subprocess
import sys

import requests
from utils import extract_video_id, count_tokens_approx, format_duration


def progress(msg: str):
    print(f"PROGRESS: {msg}", flush=True)


def error(msg: str):
    print(f"ERROR: {msg}", flush=True)
    sys.exit(1)


def get_metadata(video_id: str) -> dict:
    """Fetch video metadata via oEmbed (primary) or yt-dlp (fallback)."""
    # Validate video_id is strictly alphanumeric + dash/underscore, 11 chars
    assert len(video_id) == 11 and all(
        c.isascii() and (c.isalnum() or c in "-_") for c in video_id
    ), f"Invalid video ID: {video_id}"

    # Primary: oEmbed (no auth, works from any IP)
    try:
        r = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            return {
                "title": data.get("title", "Unknown"),
                "channel": data.get("author_name", "Unknown"),
                "duration": 0,  # oEmbed doesn't provide duration
            }
    except Exception:
        pass

    # Fallback: yt-dlp (may fail on VPS with blocked IP)
    try:
        r = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download",
             f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            data = json.loads(r.stdout)
            return {
                "title": data.get("title", "Unknown"),
                "channel": data.get("channel", data.get("uploader", "Unknown")),
                "duration": data.get("duration", 0),
            }
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass

    return {"title": None, "channel": None, "duration": 0}


def get_transcript(video_id: str, api_key: str) -> tuple[str, str]:
    """Fetch transcript via TranscriptAPI.com."""
    url = "https://transcriptapi.com/api/v2/youtube/transcript"
    params = {
        "video_url": video_id,
        "format": "json",
        "include_timestamp": "false",
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 401:
            error("API_ERROR: Invalid API key. Check your TranscriptAPI key.")
        elif response.status_code == 429:
            error("API_ERROR: Rate limited. Wait a moment and try again.")
        elif response.status_code != 200:
            error(f"API_ERROR: HTTP {response.status_code}")

        data = response.json()
        transcript_array = data.get("transcript", [])
        transcript_text = " ".join(seg.get("text", "") for seg in transcript_array)
        language = "en"  # TranscriptAPI doesn't expose language; default to English

        return transcript_text, language

    except requests.exceptions.Timeout:
        error("API_ERROR: Request timed out. Try again.")
    except requests.exceptions.RequestException as e:
        error(f"API_ERROR: Network error — could not reach TranscriptAPI.")
    except json.JSONDecodeError:
        error("API_ERROR: Invalid response from TranscriptAPI.")


def main():
    parser = argparse.ArgumentParser(description="Extract YouTube video transcript and metadata")
    parser.add_argument("video", help="YouTube URL or video ID")
    parser.add_argument("--api-key-file", help="Path to file containing TranscriptAPI key", default=None)
    args = parser.parse_args()

    # Priority: --api-key-file > TRANSCRIPT_API_KEY env var
    api_key = None
    if args.api_key_file:
        try:
            with open(args.api_key_file) as f:
                api_key = f.read().strip()
        except OSError as e:
            error(f"Cannot read API key file: {e}")
    else:
        api_key = os.environ.get("TRANSCRIPT_API_KEY", "").strip()

    if not api_key:
        error("No API key provided. Either set TRANSCRIPT_API_KEY env var or pass --api-key-file.")

    try:
        video_id = extract_video_id(args.video)
    except ValueError as e:
        error(str(e))

    progress(f"🔍 Fetching video info for {video_id}...")

    meta = get_metadata(video_id)
    duration_s = meta["duration"]
    duration_str = format_duration(duration_s) if duration_s else "unknown length"

    if duration_s > 7200:
        progress("⚠️ This video is over 2 hours — processing may take a while.")

    progress("📝 Extracting transcript...")
    transcript, detected_lang = get_transcript(video_id, api_key)
    tokens = count_tokens_approx(transcript)

    progress(f"📺 Got transcript ({duration_str}, ~{tokens} tokens).")

    # Build header
    header_parts = []
    if meta["title"]:
        header_parts.append(f'📺 **{meta["title"]}**')
        if meta["channel"]:
            header_parts.append(f' — {meta["channel"]}')
        if duration_s:
            header_parts.append(f' ({duration_str})')
        header = "".join(header_parts)
    else:
        header = f"📺 Video {video_id}"

    output = {
        "video_id": video_id,
        "title": meta["title"],
        "channel": meta["channel"],
        "duration": duration_s,
        "duration_str": duration_str,
        "language": detected_lang,
        "tokens": tokens,
        "transcript": transcript,
        "header": header,
    }

    print(f"RESULT: {json.dumps(output)}", flush=True)


if __name__ == "__main__":
    main()
