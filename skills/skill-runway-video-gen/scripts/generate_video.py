#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""Runway Gen4 Turbo — image-to-video generator."""

import argparse
import json
import os
import sys
import time
import requests


def get_api_key():
    key = os.environ.get("RUNWAY_API_KEY")
    if key:
        return key
    cfg_path = os.path.expanduser("~/tiktok-api.json")
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            data = json.load(f)
        key = data.get("runway", {}).get("apiKey")
        if key:
            return key
    print("ERROR: No Runway API key found. Set RUNWAY_API_KEY env var or add runway.apiKey to ~/tiktok-api.json", file=sys.stderr)
    sys.exit(1)


def encode_image(image_path):
    import base64
    ext = os.path.splitext(image_path)[1].lower().lstrip(".")
    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    mime = mime_map.get(ext, "image/jpeg")
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def main():
    parser = argparse.ArgumentParser(description="Runway Gen4 Turbo image-to-video")
    parser.add_argument("--image", required=True, help="Path to source image")
    parser.add_argument("--prompt", default="", help="Motion description prompt")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    parser.add_argument("--duration", type=int, choices=[5, 10], default=10, help="Video duration (5 or 10 seconds)")
    parser.add_argument("--ratio", default="720:1280", help="Aspect ratio (default: 720:1280 vertical)")
    args = parser.parse_args()

    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Runway-Version": "2024-11-06",
        "Content-Type": "application/json",
    }

    print(f"[runway] Encoding image: {args.image}")
    image_data = encode_image(args.image)

    payload = {
        "model": "gen4_turbo",
        "promptImage": image_data,
        "promptText": args.prompt,
        "duration": args.duration,
        "ratio": args.ratio,
    }

    print(f"[runway] Submitting job — {args.duration}s @ {args.ratio} ...")
    resp = requests.post(
        "https://api.dev.runwayml.com/v1/image_to_video",
        headers=headers,
        json=payload,
        timeout=30,
    )
    if not resp.ok:
        print(f"ERROR: {resp.status_code} — {resp.text}", file=sys.stderr)
        sys.exit(1)

    task_id = resp.json().get("id")
    if not task_id:
        print(f"ERROR: No task ID in response: {resp.text}", file=sys.stderr)
        sys.exit(1)

    print(f"[runway] Task ID: {task_id} — polling ...")

    poll_url = f"https://api.dev.runwayml.com/v1/tasks/{task_id}"
    while True:
        time.sleep(8)
        r = requests.get(poll_url, headers=headers, timeout=15)
        if not r.ok:
            print(f"ERROR: Poll failed {r.status_code}: {r.text}", file=sys.stderr)
            sys.exit(1)
        data = r.json()
        status = data.get("status", "UNKNOWN")
        progress = data.get("progressRatio", 0)
        print(f"[runway] Status: {status} ({int(progress * 100)}%)")

        if status == "SUCCEEDED":
            outputs = data.get("output", [])
            if not outputs:
                print("ERROR: No output URL in response", file=sys.stderr)
                sys.exit(1)
            video_url = outputs[0]
            print(f"[runway] Downloading video from {video_url[:60]}...")
            video_resp = requests.get(video_url, timeout=60)
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, "wb") as f:
                f.write(video_resp.content)
            print(f"[runway] ✅ Saved to {args.output}")
            break
        elif status == "FAILED":
            err = data.get("failure", data.get("error", "unknown"))
            print(f"ERROR: Task failed — {err}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
