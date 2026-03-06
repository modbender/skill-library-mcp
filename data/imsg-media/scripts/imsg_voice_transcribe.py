#!/usr/bin/env python3
"""
imsg-media: iMessage multimedia attachment pipeline.

Commands:
  fetch       Find latest audio or image attachment for a sender
  transcribe  Transcribe an audio file via Silicon Flow ASR
  auto        Fetch + transcribe audio in one step

For images, use `fetch` to get the path, then open with the agent's `read` tool.

Usage:
  imsg_voice_transcribe.py fetch --identifier "sender@example.com" [--limit 50] [--type audio|image|any]
  imsg_voice_transcribe.py transcribe --file /path/to/audio.m4a [--raw]
  imsg_voice_transcribe.py auto --identifier "sender@example.com" [--limit 50] [--raw]
"""

import argparse
import json
import os
import subprocess
import sys
import time

import requests


# ── constants ─────────────────────────────────────────────────────────────────

AUDIO_EXTENSIONS = {".m4a", ".caf", ".wav", ".mp3", ".aiff", ".aif", ".ogg", ".flac"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".gif", ".webp", ".bmp", ".tiff"}

AUDIO_CONTENT_TYPES = {
    "m4a": "audio/mp4",
    "caf": "audio/mp4",
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "aiff": "audio/aiff",
    "aif": "audio/aiff",
}


# ── helpers ───────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    key = os.environ.get("SILICON_FLOW_KEY", "")
    if key:
        return key
    env_file = os.path.expanduser("~/.openclaw/.env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SILICON_FLOW_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def classify(path: str) -> str:
    """Return 'audio', 'image', or 'other'."""
    _, ext = os.path.splitext(path.lower())
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    return "other"


def run_imsg(args: list, timeout: int = 30) -> list[dict]:
    """Run an imsg command and parse JSONL output. Returns list of dicts."""
    try:
        result = subprocess.run(
            ["imsg"] + args + ["--json"],
            capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError:
        raise RuntimeError("imsg CLI not found. Install via: npm install -g imsg")
    except subprocess.TimeoutExpired:
        raise RuntimeError("imsg timed out")

    if result.returncode != 0:
        err = result.stderr.strip()
        if "permissionDenied" in err or "permission" in err.lower():
            raise RuntimeError(
                "permissionDenied: Full Disk Access required. "
                "Grant FDA in System Settings → Privacy & Security."
            )
        raise RuntimeError(err or "imsg command failed")

    records = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return records


def find_chat_id(identifier: str) -> int | None:
    """Find chat rowid for a given identifier string."""
    chats = run_imsg(["chats"])
    for chat in chats:
        if chat.get("identifier") == identifier:
            return chat.get("id")
    return None


# ── fetch ─────────────────────────────────────────────────────────────────────

def cmd_fetch(identifier: str, limit: int, want_type: str) -> dict:
    """Find the most recent attachment of the given type for a sender."""
    # Step 1: resolve identifier → chat_id
    chat_id = find_chat_id(identifier)
    if chat_id is None:
        return {
            "error": f"No chat found for identifier: {identifier}",
            "hint": "Run 'imsg chats --json' to list available chats"
        }

    # Step 2: fetch history with attachments
    try:
        messages = run_imsg(["history", "--chat-id", str(chat_id), "--limit", str(limit), "--attachments"])
    except RuntimeError as e:
        return {"error": str(e)}

    found = []
    for msg in messages:
        for att in (msg.get("attachments") or []):
            # imsg uses 'original_path' (absolute) or 'filename' (may use ~)
            path = att.get("original_path") or att.get("filename") or ""
            if not path:
                continue
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                continue
            att_type = classify(path)
            if want_type == "any" or att_type == want_type:
                found.append({
                    "file": path,
                    "type": att_type,
                    "message_id": msg.get("id") or msg.get("rowid"),
                    "date": msg.get("created_at") or msg.get("date"),
                    "chat_id": chat_id,
                })

    if not found:
        return {
            "error": f"No {want_type} attachments found (scanned {limit} messages)",
            "hint": "Try --limit 100, check Full Disk Access, or ask user to resend"
        }

    return found[-1]  # most recent


# ── transcribe ────────────────────────────────────────────────────────────────

def cmd_transcribe(audio_file: str) -> dict:
    """Transcribe audio via Silicon Flow SenseVoiceSmall."""
    if not os.path.exists(audio_file):
        return {"error": f"File not found: {audio_file}"}

    if classify(audio_file) != "audio":
        return {"error": f"Not an audio file: {audio_file}", "hint": "For images, use the agent read tool after fetch"}

    api_key = get_api_key()
    if not api_key:
        return {
            "error": "SILICON_FLOW_KEY not set",
            "hint": "Add SILICON_FLOW_KEY=sk-... to ~/.openclaw/.env. Sign up at https://siliconflow.cn"
        }

    ext = audio_file.rsplit(".", 1)[-1].lower()
    content_type = AUDIO_CONTENT_TYPES.get(ext, "audio/mp4")

    try:
        t0 = time.time()
        resp = requests.post(
            "https://api.siliconflow.cn/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (os.path.basename(audio_file), open(audio_file, "rb"), content_type)},
            data={"model": "FunAudioLLM/SenseVoiceSmall", "language": "zh"},
            timeout=120,
        )
        elapsed = round(time.time() - t0, 2)
        resp.raise_for_status()
        body = resp.json()
        return {
            "text": body.get("text", "").strip(),
            "duration": body.get("duration", 0),
            "elapsed": elapsed,
            "file": audio_file,
        }
    except requests.exceptions.Timeout:
        return {"error": "Request timed out — audio may be too large or network slow"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "Failed to parse API response"}


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="iMessage media pipeline: fetch audio/image attachments and transcribe/analyze"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_f = sub.add_parser("fetch", help="Find latest attachment for a sender")
    p_f.add_argument("--identifier", "-i", required=True, help="Sender email or phone (from 'imsg chats')")
    p_f.add_argument("--limit", "-l", type=int, default=50, help="Messages to scan (default 50)")
    p_f.add_argument("--type", "-t", choices=["audio", "image", "any"], default="any")

    p_t = sub.add_parser("transcribe", help="Transcribe an audio file")
    p_t.add_argument("--file", "-f", required=True)
    p_t.add_argument("--raw", "-r", action="store_true", help="Output plain text only")
    p_t.add_argument("--api-key", "-k", help="Silicon Flow API key (overrides env)")

    p_a = sub.add_parser("auto", help="Fetch + transcribe audio in one step")
    p_a.add_argument("--identifier", "-i", required=True)
    p_a.add_argument("--limit", "-l", type=int, default=50)
    p_a.add_argument("--raw", "-r", action="store_true")
    p_a.add_argument("--api-key", "-k", help="Silicon Flow API key (overrides env)")

    args = parser.parse_args()

    if hasattr(args, "api_key") and args.api_key:
        os.environ["SILICON_FLOW_KEY"] = args.api_key

    if args.command == "fetch":
        result = cmd_fetch(args.identifier, args.limit, args.type)
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1 if "error" in result else 0)

    elif args.command == "transcribe":
        result = cmd_transcribe(args.file)
        if "error" in result:
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(1)
        print(result["text"] if args.raw else json.dumps(result, ensure_ascii=False))

    elif args.command == "auto":
        fetch_result = cmd_fetch(args.identifier, args.limit, "audio")
        if "error" in fetch_result:
            print(json.dumps(fetch_result, ensure_ascii=False))
            sys.exit(1)

        tr_result = cmd_transcribe(fetch_result["file"])
        if "error" in tr_result:
            print(json.dumps(tr_result, ensure_ascii=False))
            sys.exit(1)

        print(tr_result["text"] if args.raw else json.dumps(tr_result, ensure_ascii=False))


if __name__ == "__main__":
    main()
