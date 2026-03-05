#!/usr/bin/env python3
"""Transcribe audio files via Step ASR HTTP SSE API."""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error

API_URL = "https://api.stepfun.com/v1/audio/asr/sse"

FORMAT_MAP = {
    ".pcm": ("pcm", "pcm_s16le"),
    ".raw": ("pcm", "pcm_s16le"),
    ".wav": ("wav", "pcm_s16le"),
    ".mp3": ("mp3", ""),
    ".ogg": ("ogg", ""),
    ".opus": ("ogg", ""),
}


def detect_format(filepath, override_type):
    """Detect audio format from file extension or use override."""
    if override_type:
        codec = "pcm_s16le" if override_type == "pcm" else ""
        return override_type, codec
    ext = os.path.splitext(filepath)[1].lower()
    return FORMAT_MAP.get(ext, ("pcm", "pcm_s16le"))


def build_request_body(audio_b64, args):
    """Build the JSON request body for the Step ASR API."""
    fmt_type, codec = detect_format(args.audio_file, args.format_type)

    format_config = {
        "type": fmt_type,
        "rate": args.sample_rate,
        "bits": 16,
        "channel": 1,
    }
    if codec:
        format_config["codec"] = codec

    transcription_config = {
        "model": args.model,
        "language": args.language,
        "full_rerun_on_commit": not args.no_rerun,
        "enable_itn": not args.no_itn,
    }
    if args.prompt:
        transcription_config["prompt"] = args.prompt

    return {
        "audio": {
            "data": audio_b64,
            "input": {
                "transcription": transcription_config,
                "format": format_config,
            },
        }
    }


def parse_sse_line(line):
    """Parse a single SSE data line, return parsed JSON or None."""
    line = line.strip()
    if not line.startswith("data:"):
        return None
    payload = line[len("data:"):].strip()
    if not payload or payload == "[DONE]":
        return None
    return json.loads(payload)


def transcribe(args):
    """Main transcription logic."""
    api_key = os.environ.get("STEPFUN_API_KEY", "")
    if not api_key:
        print("Error: STEPFUN_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.audio_file):
        print(f"Error: File not found: {args.audio_file}", file=sys.stderr)
        sys.exit(1)

    # Read and base64-encode audio
    with open(args.audio_file, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode("ascii")

    body = build_request_body(audio_b64, args)
    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    full_text = ""
    usage = {}

    try:
        for raw_line in resp:
            line = raw_line.decode("utf-8", errors="replace")
            event = parse_sse_line(line)
            if event is None:
                continue

            event_type = event.get("type", "")

            if event_type == "transcript.text.delta":
                delta = event.get("delta", "")
                if not args.no_stream and not args.json:
                    sys.stdout.write(delta)
                    sys.stdout.flush()

            elif event_type == "transcript.text.done":
                full_text = event.get("text", "")
                usage = event.get("usage", {})

            elif event_type == "error":
                msg = event.get("message", "Unknown error")
                print(f"\nAPI error: {msg}", file=sys.stderr)
                sys.exit(1)
    finally:
        resp.close()

    # Final output
    if not args.no_stream and not args.json:
        print()  # newline after streaming deltas

    if args.json:
        result = {"text": full_text, "usage": usage}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.no_stream:
        print(full_text)

    # Save to file
    if args.out:
        out_dir = os.path.dirname(os.path.abspath(args.out))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            if args.json:
                json.dump({"text": full_text, "usage": usage}, f, ensure_ascii=False, indent=2)
            else:
                f.write(full_text)
        print(f"Saved to: {args.out}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio via Step ASR streaming API (HTTP SSE)."
    )
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument(
        "--language", default="zh",
        help="Language code: zh (Chinese) or en (English). Default: zh",
    )
    parser.add_argument(
        "--model", default="step-asr",
        help="ASR model name. Default: step-asr",
    )
    parser.add_argument(
        "--out", default="",
        help="Save transcription to this file path",
    )
    parser.add_argument(
        "--prompt", default="",
        help="Hint text to improve accuracy for domain-specific terms",
    )
    parser.add_argument(
        "--format-type", default="",
        help="Audio format type: pcm, mp3, ogg (auto-detected from file extension)",
    )
    parser.add_argument(
        "--sample-rate", type=int, default=16000,
        help="Audio sample rate in Hz. Default: 16000",
    )
    parser.add_argument(
        "--no-stream", action="store_true",
        help="Disable streaming output, only print final result",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output result as JSON (includes usage statistics)",
    )
    parser.add_argument(
        "--no-itn", action="store_true",
        help="Disable inverse text normalization",
    )
    parser.add_argument(
        "--no-rerun", action="store_true",
        help="Disable second-pass error correction",
    )
    args = parser.parse_args()
    transcribe(args)


if __name__ == "__main__":
    main()
