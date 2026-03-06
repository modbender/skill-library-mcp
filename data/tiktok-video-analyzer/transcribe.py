#!/usr/bin/env python3
"""
Video Analyzer - Transcription Engine
Works with TikTok, YouTube, Instagram, Twitter, and 1000+ sites via yt-dlp

Usage:
  transcribe.py <URL>                    Full pipeline (download + transcribe)
  transcribe.py --download-only <URL>    Step 1: download audio, return staging path
  transcribe.py --transcribe-only <ID>   Step 2: transcribe staged audio by video_id
"""

import sys
import os
import json
import tempfile
import subprocess
import hashlib
import logging
from pathlib import Path

# Silence faster-whisper model download chatter
logging.getLogger("faster_whisper").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

SKILL_DIR = Path(__file__).parent
TRANSCRIPTS_DIR = SKILL_DIR / "transcripts"
STAGING_DIR = SKILL_DIR / "staging"
TRANSCRIPTS_DIR.mkdir(exist_ok=True)
STAGING_DIR.mkdir(exist_ok=True)


def get_video_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


class SilentLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def download_audio(url: str, output_path: str) -> tuple[bool, str]:
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "5",
        "--output", output_path,
        "--no-playlist",
        "--quiet",
        "--no-warnings",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        err = result.stderr.strip() or "Unknown error"
        if "private" in err.lower():
            return False, "Video is private or unavailable."
        if "not available" in err.lower() or "removed" in err.lower():
            return False, "Video has been removed or is unavailable."
        return False, f"Download failed: {err[:200]}"
    return True, ""


def transcribe_audio(audio_path: str) -> dict:
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, beam_size=5)
        parts = [seg.text.strip() for seg in segments]
        return {
            "engine": "faster-whisper",
            "language": info.language,
            "transcript": " ".join(parts)
        }
    except ImportError:
        pass

    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return {
            "engine": "whisper",
            "language": result.get("language", "unknown"),
            "transcript": result.get("text", "").strip()
        }
    except ImportError:
        pass

    return {"error": "No transcription engine found. Run: pip install faster-whisper"}


def cmd_download_only(url: str):
    """Step 1: download audio to staging, return path info"""
    video_id = get_video_id(url)
    cache_file = TRANSCRIPTS_DIR / f"{video_id}.json"

    # Already cached — skip download entirely
    if cache_file.exists():
        with open(cache_file) as f:
            cached = json.load(f)
        cached["from_cache"] = True
        cached["skip_transcribe"] = True
        print(json.dumps(cached))
        return

    audio_path = str(STAGING_DIR / f"{video_id}.mp3")
    ok, err = download_audio(url, audio_path)
    if not ok:
        print(json.dumps({"error": err}))
        sys.exit(1)

    print(json.dumps({
        "status": "downloaded",
        "video_id": video_id,
        "audio_path": audio_path,
        "url": url,
        "from_cache": False
    }))


def cmd_transcribe_only(video_id: str):
    """Step 2: transcribe staged audio by video_id"""
    audio_path = STAGING_DIR / f"{video_id}.mp3"
    if not audio_path.exists():
        print(json.dumps({"error": f"No staged audio found for {video_id}. Run download step first."}))
        sys.exit(1)

    result = transcribe_audio(str(audio_path))
    if "error" in result:
        print(json.dumps(result))
        sys.exit(1)

    # Clean up staging file
    audio_path.unlink(missing_ok=True)

    # Get URL from any existing partial data if available
    result["video_id"] = video_id
    result["from_cache"] = False

    # Save to cache
    cache_file = TRANSCRIPTS_DIR / f"{video_id}.json"
    with open(cache_file, "w") as f:
        json.dump(result, f)

    print(json.dumps(result))


def cmd_full_pipeline(url: str):
    """Full pipeline: download + transcribe in one shot"""
    video_id = get_video_id(url)
    cache_file = TRANSCRIPTS_DIR / f"{video_id}.json"

    if cache_file.exists():
        with open(cache_file) as f:
            cached = json.load(f)
        cached["from_cache"] = True
        print(json.dumps(cached))
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")
        ok, err = download_audio(url, audio_path)
        if not ok:
            print(json.dumps({"error": err}))
            sys.exit(1)

        result = transcribe_audio(audio_path)
        if "error" in result:
            print(json.dumps(result))
            sys.exit(1)

    result["url"] = url
    result["video_id"] = video_id
    result["from_cache"] = False

    with open(cache_file, "w") as f:
        json.dump(result, f)

    print(json.dumps(result))


def main():
    args = sys.argv[1:]

    if not args:
        print(json.dumps({"error": "Usage: transcribe.py [--download-only|--transcribe-only] <URL or ID>"}))
        sys.exit(1)

    if args[0] == "--download-only":
        if len(args) < 2:
            print(json.dumps({"error": "URL required"}))
            sys.exit(1)
        cmd_download_only(args[1])

    elif args[0] == "--transcribe-only":
        if len(args) < 2:
            print(json.dumps({"error": "video_id required"}))
            sys.exit(1)
        cmd_transcribe_only(args[1])

    else:
        cmd_full_pipeline(args[0])


if __name__ == "__main__":
    main()
