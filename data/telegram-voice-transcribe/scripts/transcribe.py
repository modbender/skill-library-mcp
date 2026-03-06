#!/usr/bin/env python3
"""
telegram-voice-transcribe — Transcribe Telegram voice messages.

Modes:
  --local          Use local Whisper (free, no API key needed)
  (default)        Use OpenAI Whisper API (requires OPENAI_API_KEY)

Usage examples:
  python3 transcribe.py --file-id <id> --local
  python3 transcribe.py --file audio.ogg --local --model small
  python3 transcribe.py --file-id <id>                    # API mode
  python3 transcribe.py --url https://...

Output: JSON  {"transcript": "...", "duration_s": 4.2, "language": "es"}
"""

import argparse
import json
import os
import sys
import tempfile
import urllib.request
import urllib.error

TELEGRAM_API = "https://api.telegram.org"


# ── Helpers ────────────────────────────────────────────────────────────────────

def download_telegram_file(file_id: str, bot_token: str) -> str:
    url = f"{TELEGRAM_API}/bot{bot_token}/getFile?file_id={file_id}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Telegram getFile error: {e.code} {e.reason}")
    if not data.get("ok"):
        raise RuntimeError(f"Telegram error: {data.get('description', 'unknown')}")
    file_path = data["result"]["file_path"]
    ext = os.path.splitext(file_path)[1] or ".ogg"
    file_url = f"{TELEGRAM_API}/file/bot{bot_token}/{file_path}"
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    urllib.request.urlretrieve(file_url, tmp.name)
    return tmp.name


def download_url(url: str) -> str:
    ext = os.path.splitext(url.split("?")[0])[1] or ".ogg"
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    urllib.request.urlretrieve(url, tmp.name)
    return tmp.name


# ── Transcription backends ─────────────────────────────────────────────────────

def transcribe_local(audio_path: str, language: str | None, model_name: str) -> dict:
    """Transcribe using local Whisper (free, CPU/GPU)."""
    # Register static-ffmpeg binary if system ffmpeg not found
    import shutil
    if not shutil.which("ffmpeg"):
        try:
            import static_ffmpeg
            static_ffmpeg.add_paths()
        except ImportError:
            pass  # will fail later with a clear whisper error

    try:
        import whisper
    except ImportError:
        raise RuntimeError(
            "openai-whisper not installed. Run: pip3 install openai-whisper"
        )
    print(f"[whisper] Loading model '{model_name}'...", file=sys.stderr)
    model = whisper.load_model(model_name)
    opts = {}
    if language:
        opts["language"] = language
    print(f"[whisper] Transcribing {audio_path}...", file=sys.stderr)
    result = model.transcribe(audio_path, **opts)
    return {
        "transcript": result["text"].strip(),
        "language": result.get("language"),
        "duration_s": round(sum(s.get("end", 0) for s in result.get("segments", [])), 1) or 0,
    }


def transcribe_api(audio_path: str, language: str | None, api_key: str) -> dict:
    """Transcribe using OpenAI Whisper API ($0.006/min)."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip3 install openai")
    client = OpenAI(api_key=api_key)
    kwargs = {"model": "whisper-1", "response_format": "verbose_json"}
    if language:
        kwargs["language"] = language
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(file=f, **kwargs)
    return {
        "transcript": result.text.strip(),
        "language": getattr(result, "language", None),
        "duration_s": round(getattr(result, "duration", 0), 1),
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Transcribe Telegram voice messages.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--file-id", help="Telegram voice file_id")
    src.add_argument("--file",    help="Local audio file path")
    src.add_argument("--url",     help="Direct audio URL")

    parser.add_argument("--local",      action="store_true", help="Use local Whisper (free)")
    parser.add_argument("--model",      default="small",     help="Local model: tiny/base/small/medium/large (default: small)")
    parser.add_argument("--language",   default=None,        help="ISO language hint e.g. 'es', 'en'")
    parser.add_argument("--bot-token",  default=os.getenv("TELEGRAM_BOT_TOKEN"))
    parser.add_argument("--openai-key", default=os.getenv("OPENAI_API_KEY"))
    args = parser.parse_args()

    tmp_path = None
    try:
        # Resolve audio path
        if args.file_id:
            if not args.bot_token:
                raise RuntimeError("TELEGRAM_BOT_TOKEN required for --file-id mode")
            tmp_path = download_telegram_file(args.file_id, args.bot_token)
            audio_path = tmp_path
        elif args.url:
            tmp_path = download_url(args.url)
            audio_path = tmp_path
        else:
            audio_path = args.file
            if not os.path.exists(audio_path):
                raise RuntimeError(f"File not found: {audio_path}")

        # Transcribe
        if args.local:
            result = transcribe_local(audio_path, args.language, args.model)
        else:
            if not args.openai_key:
                raise RuntimeError("OPENAI_API_KEY not set (or use --local for free mode)")
            result = transcribe_api(audio_path, args.language, args.openai_key)

        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    main()
