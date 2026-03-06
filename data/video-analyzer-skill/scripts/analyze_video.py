#!/usr/bin/env python3
"""Video Analyzer for OpenClaw — download, transcribe, and analyze videos."""

import argparse
import subprocess
import sys
import hashlib
import re
from pathlib import Path

# --- Configuration ---
MODELS_DIR = Path("/opt/homebrew/share/whisper-cpp")
WHISPER_MODELS = {
    "normal": "ggml-base.bin",       # 142MB - multilingual, fast (~1 min for 30 min video)
    "max": "ggml-large-v3-turbo.bin" # 3GB - multilingual, best quality (~5 min for 30 min video)
}
WHISPER_BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/"

REQUIRED_BINS = ["yt-dlp", "ffmpeg", "whisper-cli"]


def check_dependencies():
    """Verify all required binaries are installed."""
    missing = []
    for bin_name in REQUIRED_BINS:
        result = subprocess.run(
            ["which", bin_name], capture_output=True, text=True
        )
        if result.returncode != 0:
            missing.append(bin_name)
    if missing:
        print(f"Error: Missing required tools: {', '.join(missing)}", file=sys.stderr)
        print("Install with: brew install " + " ".join(
            "ggerganov/ggerganov/whisper-cpp" if b == "whisper-cli" else b
            for b in missing
        ), file=sys.stderr)
        sys.exit(1)


def run_cmd(cmd, check=True):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        if check:
            print(f"Error running: {cmd}", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
            sys.exit(1)
        return ""


def quote_url(url):
    """Shell-safe quote for URLs."""
    # Replace single quotes to prevent shell injection
    return url.replace("'", "'\\''")


def download_model_if_needed(model_filename):
    """Download whisper model to Homebrew share dir if missing."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / model_filename

    if not model_path.exists():
        print(f"Downloading Whisper model '{model_filename}' (this only happens once)...", file=sys.stderr)
        url = WHISPER_BASE_URL + model_filename
        run_cmd(f'curl -L "{url}" -o "{model_path}"')
    return str(model_path)


def parse_vtt_to_timestamped(vtt_path, txt_path):
    """Convert VTT subtitle file to [MM:SS] timestamped text."""
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = []
    last_text = ""

    for block in content.split('\n\n'):
        block = block.strip()
        if not block or block.startswith('WEBVTT'):
            continue

        block_lines = block.split('\n')
        timestamp_line = None
        text_lines = []

        for line in block_lines:
            if '-->' in line:
                timestamp_line = line
            elif timestamp_line is not None:
                # Text line after timestamp
                cleaned = re.sub(r'<[^>]+>', '', line).strip()
                if cleaned and not cleaned.isdigit():
                    text_lines.append(cleaned)

        if timestamp_line and text_lines:
            text = ' '.join(text_lines)
            # Deduplicate (YouTube auto-subs repeat a lot)
            if text == last_text:
                continue
            last_text = text

            # Extract start time HH:MM:SS
            match = re.match(r'(\d{2}):(\d{2}):(\d{2})', timestamp_line)
            if match:
                hours, mins, secs = match.groups()
                timestamp = f"[{mins}:{secs}]" if hours == "00" else f"[{hours}:{mins}:{secs}]"
                lines.append(f"{timestamp} {text}")

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def parse_srt_to_timestamped(srt_path, txt_path):
    """Convert SRT subtitle file to [MM:SS] timestamped text."""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.strip().split('\n\n')
    lines = []

    for block in blocks:
        block_lines = block.strip().split('\n')
        if len(block_lines) < 3:
            continue

        # Line 0: sequence number, Line 1: timestamp, Line 2+: text
        timestamp_line = block_lines[1]
        text = ' '.join(block_lines[2:]).strip()

        match = re.match(r'(\d{2}):(\d{2}):(\d{2})', timestamp_line)
        if match and text:
            hours, mins, secs = match.groups()
            timestamp = f"[{mins}:{secs}]" if hours == "00" else f"[{hours}:{mins}:{secs}]"
            lines.append(f"{timestamp} {text}")

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def handle_transcript(url, quality, lang):
    """Two-tier transcript extraction."""
    safe_url = quote_url(url)
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    tmp_dir = Path(f"/tmp/video_analyzer_{url_hash}")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing: {url}", file=sys.stderr)

    # ---------------------------------------------------------
    # LEVEL 1: Fast Track (yt-dlp native subtitles)
    # ---------------------------------------------------------
    print("Level 1: Attempting to extract native subtitles...", file=sys.stderr)
    subs_out = tmp_dir / "subs"
    cmd_subs = f"yt-dlp --write-auto-subs --write-subs --sub-langs '{lang}' --skip-download -o '{subs_out}' '{safe_url}'"
    run_cmd(cmd_subs, check=False)

    vtt_files = list(tmp_dir.glob("*.vtt"))
    if vtt_files:
        print("Native subtitles found! Processing...", file=sys.stderr)
        txt_file = tmp_dir / "transcript.txt"
        parse_vtt_to_timestamped(vtt_files[0], txt_file)
        print(f"SUCCESS: Transcript saved to:\n{txt_file}")
        return

    # ---------------------------------------------------------
    # LEVEL 2: Deep Fallback (Whisper local)
    # ---------------------------------------------------------
    print("Level 1 failed (no subs found or unsupported platform).", file=sys.stderr)
    print("Level 2: Falling back to local Whisper transcription...", file=sys.stderr)

    audio_raw = tmp_dir / "audio"
    audio_wav = tmp_dir / "audio.wav"

    # 1. Download audio (let yt-dlp pick the best format)
    print("Downloading audio track...", file=sys.stderr)
    run_cmd(f"yt-dlp -f 'bestaudio[ext=m4a]/bestaudio/best' -o '{audio_raw}.%(ext)s' '{safe_url}'")

    # Find whatever file yt-dlp actually downloaded
    audio_files = [f for f in tmp_dir.glob("audio.*") if f.suffix != '.wav']
    if not audio_files:
        print("Error: Failed to download audio.", file=sys.stderr)
        sys.exit(1)
    audio_downloaded = audio_files[0]

    # 2. Convert to WAV 16kHz mono (required by whisper-cpp)
    print("Converting to 16kHz WAV...", file=sys.stderr)
    run_cmd(f"ffmpeg -i '{audio_downloaded}' -ar 16000 -ac 1 -c:a pcm_s16le '{audio_wav}' -y")

    # 3. Check/Download Model
    model_filename = WHISPER_MODELS.get(quality, WHISPER_MODELS["normal"])
    model_path = download_model_if_needed(model_filename)

    # 4. Transcribe → SRT for precise timestamps
    print(f"Transcribing using {model_filename}... (this may take a moment)", file=sys.stderr)
    srt_out = tmp_dir / "transcript"
    lang_flag = f"-l {lang}" if lang != 'en' else ""

    run_cmd(f"whisper-cli -m '{model_path}' -f '{audio_wav}' {lang_flag} --output-srt --output-file '{srt_out}'")

    srt_file = tmp_dir / "transcript.srt"
    final_txt = tmp_dir / "transcript.txt"

    if srt_file.exists():
        parse_srt_to_timestamped(srt_file, final_txt)
        print(f"SUCCESS: Transcript saved to:\n{final_txt}")
    else:
        print("Error: Transcription failed.", file=sys.stderr)
        sys.exit(1)


def handle_download(url, action):
    """Download video or audio to Desktop."""
    safe_url = quote_url(url)
    desktop = Path.home() / "Desktop"

    if action == "download-video":
        print("Downloading best video quality to Desktop...", file=sys.stderr)
        cmd = f"yt-dlp -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' -o '{desktop}/%(title)s.%(ext)s' '{safe_url}'"
    else:
        print("Downloading best audio quality to Desktop...", file=sys.stderr)
        cmd = f"yt-dlp -f 'bestaudio[ext=m4a]/bestaudio/best' -o '{desktop}/%(title)s.%(ext)s' '{safe_url}'"

    out = run_cmd(cmd)

    # Extract destination path from yt-dlp output
    dest = ""
    for line in out.split('\n'):
        if "Destination:" in line:
            dest = line.split("Destination:")[1].strip()
        elif "has already been downloaded" in line:
            dest = line.split("[download]")[1].split("has already")[0].strip()

    print(f"SUCCESS: Downloaded to:\n{dest}")


if __name__ == "__main__":
    check_dependencies()

    parser = argparse.ArgumentParser(description="Video Analyzer for OpenClaw")
    parser.add_argument("--url", required=True, help="Video URL")
    parser.add_argument("--action", required=True, choices=["transcript", "download-video", "download-audio"])
    parser.add_argument("--quality", choices=["normal", "max"], default="normal",
                        help="Whisper model: normal (fast) or max (best quality)")
    parser.add_argument("--lang", default="en", help="Language code (e.g., 'en', 'it')")

    args = parser.parse_args()

    if args.action == "transcript":
        handle_transcript(args.url, args.quality, args.lang)
    else:
        handle_download(args.url, args.action)
