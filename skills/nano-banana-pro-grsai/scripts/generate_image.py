#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Generate/edit images using grsai.com Nano Banana Pro API.

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png" [--resolution 1K|2K|4K] [--api-key KEY]
"""

import argparse
import base64
import json
import os
import struct
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


GRSAI_API_URL = "https://grsaiapi.com/v1/draw/nano-banana"
GRSAI_RESULT_URL = "https://grsaiapi.com/v1/draw/result"

# Fallback model chain: try each in order on failure (pro variants only, cheapest first)
FALLBACK_MODELS = [
    "nano-banana-pro",
    "nano-banana-pro-vt",
    "nano-banana-pro-cl",
    "nano-banana-pro-vip",
]

# Errors that indicate a transient failure — worth retrying
TRANSIENT_KEYWORDS = ("timeout", "network", "connection", "unavailable", "overload", "retry", "rate limit")

# Errors that indicate a permanent failure — skip to next model
PERMANENT_KEYWORDS = ("moderation", "nsfw", "invalid", "unauthorized", "forbidden", "not exist")


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("GRSAI_API_KEY")


def http_post(url: str, data: dict, api_key: str) -> dict:
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def is_transient_error(msg: str) -> bool:
    msg_lower = msg.lower()
    return any(kw in msg_lower for kw in TRANSIENT_KEYWORDS)


def is_permanent_error(msg: str) -> bool:
    msg_lower = msg.lower()
    return any(kw in msg_lower for kw in PERMANENT_KEYWORDS)


def submit_task(payload: dict, api_key: str) -> str:
    """Submit a generation task, return task_id."""
    response = http_post(GRSAI_API_URL, payload, api_key)
    if response.get("code") != 0:
        raise RuntimeError(response.get("msg", "Unknown error"))
    return response["data"]["id"]


def poll_result(task_id: str, api_key: str, poll_interval: float = 3.0, timeout: int = 300) -> dict:
    """Poll for task result until succeeded, failed, or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = http_post(GRSAI_RESULT_URL, {"id": task_id}, api_key)
        if result.get("code") != 0:
            raise RuntimeError(f"Result API error: {result.get('msg')}")
        data = result["data"]
        status = data.get("status")
        progress = data.get("progress", 0)
        print(f"  Progress: {progress}% ({status})")
        if status == "succeeded":
            return data
        if status == "failed":
            reason = (data.get("failure_reason", "") + " " + data.get("error", "")).strip()
            raise RuntimeError(reason or "unknown failure")
        time.sleep(poll_interval)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def try_generate(payload: dict, api_key: str, model: str, max_retries: int = 3) -> dict:
    """
    Try to generate with one model, retrying transient errors with exponential backoff.
    Returns result dict on success, raises RuntimeError/TimeoutError otherwise.
    """
    attempt_payload = {**payload, "model": model}
    delay = 4.0
    last_error: Exception = RuntimeError("no attempts made")

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[{model}] Attempt {attempt}/{max_retries}: submitting task...")
            task_id = submit_task(attempt_payload, api_key)
            print(f"[{model}] Task created: {task_id}")
            return poll_result(task_id, api_key)

        except TimeoutError as e:
            last_error = e
            print(f"[{model}] Attempt {attempt} timed out: {e}")

        except RuntimeError as e:
            msg = str(e)
            last_error = e
            if is_permanent_error(msg):
                print(f"[{model}] Permanent error (will not retry): {msg}")
                raise
            print(f"[{model}] Attempt {attempt} failed (transient): {msg}")

        if attempt < max_retries:
            print(f"[{model}] Retrying in {delay:.0f}s...")
            time.sleep(delay)
            delay = min(delay * 2, 60)

    raise last_error


def detect_png_dimensions(data: bytes) -> tuple[int, int] | None:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return width, height
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate/edit images using grsai.com Nano Banana Pro API"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image description/prompt")
    parser.add_argument("--filename", "-f", required=True, help="Output filename (e.g., output.png)")
    parser.add_argument("--input-image", "-i", help="Optional input image path for editing/modification")
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K",
    )
    parser.add_argument("--api-key", "-k", help="grsai API key (overrides GRSAI_API_KEY env var)")
    parser.add_argument(
        "--aspect-ratio", "-a",
        default="auto",
        help="Aspect ratio: auto (default), 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 5:4, 4:5, 21:9",
    )
    parser.add_argument(
        "--model", "-m",
        default=FALLBACK_MODELS[0],
        help=f"Model to use (default: {FALLBACK_MODELS[0]}). Falls back to other models on failure.",
    )

    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GRSAI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle input image - convert to base64 for the API
    urls = []
    output_resolution = args.resolution
    if args.input_image:
        input_path = Path(args.input_image)
        if not input_path.exists():
            print(f"Error: Input image not found: {args.input_image}", file=sys.stderr)
            sys.exit(1)
        img_data = input_path.read_bytes()
        ext = input_path.suffix.lower().lstrip(".")
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "jpeg")
        b64 = base64.b64encode(img_data).decode("utf-8")
        urls = [f"data:image/{mime};base64,{b64}"]
        print(f"Loaded input image: {args.input_image}")

        # Auto-detect resolution from PNG dimensions if user didn't specify
        if args.resolution == "1K":
            dims = detect_png_dimensions(img_data)
            if dims:
                width, height = dims
                max_dim = max(width, height)
                if max_dim >= 3000:
                    output_resolution = "4K"
                elif max_dim >= 1500:
                    output_resolution = "2K"
                print(f"Auto-detected resolution: {output_resolution} (from input {width}x{height})")

    payload: dict = {
        "prompt": args.prompt,
        "aspectRatio": args.aspect_ratio,
        "imageSize": output_resolution,
        "webHook": "-1",
    }
    if urls:
        payload["urls"] = urls

    action = "Editing image" if urls else "Generating image"
    print(f"{action} — resolution={output_resolution}, aspect={args.aspect_ratio}")

    # Build model fallback chain starting from requested model
    requested = args.model
    chain = [requested] + [m for m in FALLBACK_MODELS if m != requested]

    result = None
    for model in chain:
        try:
            result = try_generate(payload, api_key, model)
            break
        except RuntimeError as e:
            msg = str(e)
            if is_permanent_error(msg):
                print(f"Permanent error, aborting: {msg}", file=sys.stderr)
                sys.exit(1)
            next_model = next((m for m in chain if m != model and chain.index(m) > chain.index(model)), None)
            if next_model:
                print(f"[{model}] All retries exhausted. Falling back to {next_model}...")
            else:
                print(f"All models failed. Last error: {msg}", file=sys.stderr)
                sys.exit(1)
        except TimeoutError as e:
            next_model = next((m for m in chain if m != model and chain.index(m) > chain.index(model)), None)
            if next_model:
                print(f"[{model}] Timed out. Falling back to {next_model}...")
            else:
                print(f"All models timed out: {e}", file=sys.stderr)
                sys.exit(1)

    if result is None:
        print("Error: generation failed across all models.", file=sys.stderr)
        sys.exit(1)

    image_url = result["results"][0]["url"]
    content = result["results"][0].get("content", "")
    if content:
        print(f"Model response: {content}")

    print("Downloading image...")
    try:
        with urllib.request.urlopen(image_url, timeout=60 * 2) as resp:
            output_path.write_bytes(resp.read())
    except Exception as e:
        print(f"Error downloading image: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nImage saved: {output_path.resolve()}")


if __name__ == "__main__":
    main()
