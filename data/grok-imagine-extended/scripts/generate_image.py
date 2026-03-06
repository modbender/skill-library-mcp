#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Generate images using xAI Grok Imagine Extended API.

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png"
    uv run generate_image.py --prompt "edit instructions" --filename "output.png" -i source.jpg
    uv run generate_image.py --prompt "scene description" --filename "output.mp4" --video --duration 5
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

IMAGES_URL = "https://api.x.ai/v1/images/generations"
EDITS_URL = "https://api.x.ai/v1/images/edits"
VIDEOS_URL = "https://api.x.ai/v1/videos/generations"
VIDEOS_POLL_URL = "https://api.x.ai/v1/videos"

KEYS_FILE_PATHS = [
    Path.home() / "keys.txt",
]


def load_api_key(provided_key: str | None = None) -> str:
    """Load XAI_API_KEY from argument, env, or keys.txt fallback."""
    if provided_key:
        return provided_key
    key = os.environ.get("XAI_API_KEY")
    if key:
        return key
    for keys_path in KEYS_FILE_PATHS:
        if keys_path.exists():
            try:
                text = keys_path.read_text(encoding="utf-8")
                match = re.search(r"^XAI_API_KEY=(.+)$", text, re.MULTILINE)
                if match:
                    return match.group(1).strip()
            except OSError:
                continue
    print("Error: XAI_API_KEY not found.", file=sys.stderr)
    print("Set XAI_API_KEY env var, provide --api-key, or add to ~/keys.txt", file=sys.stderr)
    sys.exit(1)


def api_request(url: str, api_key: str, body: dict, timeout: int = 120) -> dict:
    """Make a JSON POST request to the xAI API."""
    payload = json.dumps(body).encode("utf-8")
    req = Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "openclaw-grok-imagine/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"API error {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def api_get(url: str, api_key: str, timeout: int = 30) -> dict:
    """Make a GET request to the xAI API."""
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "openclaw-grok-imagine/1.0",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"API error {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def download_file(url: str, output_path: Path) -> None:
    """Download a file from URL to disk."""
    req = Request(url, headers={"User-Agent": "openclaw-grok-imagine/1.0"}, method="GET")
    try:
        with urlopen(req, timeout=120) as resp:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(resp.read())
    except (HTTPError, URLError) as e:
        print(f"Download error: {e}", file=sys.stderr)
        sys.exit(1)


def generate_image(api_key: str, prompt: str, output_path: Path,
                   model: str = "grok-imagine-image",
                   aspect_ratio: str | None = None,
                   resolution: str | None = None,
                   n: int = 1) -> None:
    """Generate image(s) from text prompt."""
    body: dict = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "response_format": "url",
    }
    if aspect_ratio:
        body["aspect_ratio"] = aspect_ratio
    if resolution:
        body["resolution"] = resolution

    print(f"Generating image with {model}...")
    data = api_request(IMAGES_URL, api_key, body)

    images = data.get("data", [])
    if not images:
        print("Error: No images returned.", file=sys.stderr)
        sys.exit(1)

    for i, img in enumerate(images):
        url = img.get("url")
        if not url:
            print(f"Error: Image {i} has no URL.", file=sys.stderr)
            continue

        if n > 1:
            stem = output_path.stem
            suffix = output_path.suffix or ".jpg"
            path = output_path.parent / f"{stem}-{i+1}{suffix}"
        else:
            path = output_path

        download_file(url, path)
        full_path = path.resolve()
        size_kb = path.stat().st_size / 1024
        print(f"\nImage saved: {full_path} ({size_kb:.0f} KB)")
        print(f"MEDIA: {full_path}")

        revised = img.get("revised_prompt", "")
        if revised:
            print(f"Revised prompt: {revised}")


def edit_image(api_key: str, prompt: str, output_path: Path,
               input_images: list[str],
               model: str = "grok-imagine-image",
               n: int = 1) -> None:
    """Edit image(s) using a text prompt."""
    body: dict = {
        "model": model,
        "prompt": prompt,
        "n": n,
    }
    if len(input_images) == 1:
        body["image_url"] = input_images[0]
    else:
        body["images"] = input_images

    print(f"Editing {len(input_images)} image(s) with {model}...")
    data = api_request(EDITS_URL, api_key, body)

    images = data.get("data", [])
    if not images:
        print("Error: No images returned.", file=sys.stderr)
        sys.exit(1)

    for i, img in enumerate(images):
        url = img.get("url")
        if not url:
            continue
        if n > 1:
            stem = output_path.stem
            suffix = output_path.suffix or ".jpg"
            path = output_path.parent / f"{stem}-{i+1}{suffix}"
        else:
            path = output_path

        download_file(url, path)
        full_path = path.resolve()
        size_kb = path.stat().st_size / 1024
        print(f"\nImage saved: {full_path} ({size_kb:.0f} KB)")
        print(f"MEDIA: {full_path}")


def generate_video(api_key: str, prompt: str, output_path: Path,
                   duration: int = 5,
                   aspect_ratio: str = "16:9",
                   resolution: str = "720p",
                   image_url: str | None = None,
                   poll_interval: int = 10,
                   max_wait: int = 600) -> None:
    """Generate video from text/image prompt (async with polling)."""
    body: dict = {
        "model": "grok-imagine-video",
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }
    if image_url:
        body["image_url"] = image_url

    print(f"Submitting video generation ({duration}s, {resolution}, {aspect_ratio})...")
    data = api_request(VIDEOS_URL, api_key, body)

    request_id = data.get("request_id")
    if not request_id:
        print(f"Error: No request_id returned. Response: {json.dumps(data)}", file=sys.stderr)
        sys.exit(1)

    print(f"Request ID: {request_id}")
    print(f"Polling every {poll_interval}s (max {max_wait}s)...")

    elapsed = 0
    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval

        status_data = api_get(f"{VIDEOS_POLL_URL}/{request_id}", api_key)
        status = status_data.get("status", "unknown")
        print(f"  [{elapsed}s] Status: {status}")

        if status == "done":
            video = status_data.get("video", {})
            video_url = video.get("url")
            if not video_url:
                print("Error: Video done but no URL.", file=sys.stderr)
                sys.exit(1)

            download_file(video_url, output_path)
            full_path = output_path.resolve()
            size_mb = output_path.stat().st_size / (1024 * 1024)
            video_duration = video.get("duration", duration)
            print(f"\nVideo saved: {full_path} ({size_mb:.1f} MB, {video_duration}s)")
            print(f"MEDIA: {full_path}")
            return

        elif status == "expired":
            print("Error: Video generation expired/failed.", file=sys.stderr)
            sys.exit(1)

    print(f"Error: Timed out after {max_wait}s.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images/videos using xAI Grok Imagine Extended",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s --prompt "a cyberpunk city at night" --filename city.png
  %(prog)s --prompt "make it a watercolor" --filename edit.png -i source.jpg
  %(prog)s --prompt "a cat walking" --filename cat.mp4 --video --duration 5
  %(prog)s --prompt "animate this photo" --filename anim.mp4 --video -i photo.jpg
""",
    )
    parser.add_argument("--prompt", "-p", required=True, help="Text description/prompt")
    parser.add_argument("--filename", "-f", required=True, help="Output filename")
    parser.add_argument(
        "--input-image", "-i",
        action="append", dest="input_images", metavar="IMAGE",
        help="Input image path/URL for editing. Up to 3 for images, 1 for video.",
    )
    parser.add_argument(
        "--model", "-m",
        default="grok-imagine-image",
        help="Model: grok-imagine-image (default), grok-imagine-image-pro, grok-2-image-1212",
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        help="Aspect ratio: 1:1, 16:9, 9:16, 4:3, 3:4, etc.",
    )
    parser.add_argument(
        "--resolution", "-r",
        help="Image: 1k or 2k. Video: 480p or 720p.",
    )
    parser.add_argument("--n", type=int, default=1, help="Number of images (1-10, default 1)")
    parser.add_argument("--video", action="store_true", help="Generate video instead of image")
    parser.add_argument("--duration", "-d", type=int, default=5, help="Video duration 1-15s (default 5)")
    parser.add_argument("--api-key", "-k", help="XAI API key (overrides env/keys.txt)")

    args = parser.parse_args()
    api_key = load_api_key(args.api_key)
    output_path = Path(args.filename)

    if args.video:
        image_url = args.input_images[0] if args.input_images else None
        generate_video(
            api_key, args.prompt, output_path,
            duration=args.duration,
            aspect_ratio=args.aspect_ratio or "16:9",
            resolution=args.resolution or "720p",
            image_url=image_url,
        )
    elif args.input_images:
        if len(args.input_images) > 3:
            print("Error: Max 3 input images for editing.", file=sys.stderr)
            sys.exit(1)
        edit_image(
            api_key, args.prompt, output_path,
            input_images=args.input_images,
            model=args.model,
            n=args.n,
        )
    else:
        generate_image(
            api_key, args.prompt, output_path,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            n=args.n,
        )


if __name__ == "__main__":
    main()
