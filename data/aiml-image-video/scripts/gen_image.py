#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import time
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://api.aimlapi.com/v1"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate images via AIMLAPI /images/generations")
    parser.add_argument("--prompt", required=True, help="Text prompt for the image")
    parser.add_argument("--model", default="aimlapi/openai/gpt-image-1", help="Model reference")
    parser.add_argument("--image-url", help="Input image URL or local path for I2I")
    parser.add_argument("--size", default="1024x1024", help="Image size, e.g., 1024x1024")
    parser.add_argument("--count", type=int, default=1, help="Number of images to generate")
    parser.add_argument("--out-dir", default="./out/images", help="Output directory")
    parser.add_argument("--extra-json", default=None, help="Extra JSON to merge into the payload")
    parser.add_argument("--timeout", type=int, default=120, help="Request timeout in seconds")
    parser.add_argument("--output-format", default="png", help="File extension for outputs (no dot)")
    parser.add_argument("--apikey-file", default=None, help="Path to a file containing the API key")
    parser.add_argument("--retry-max", type=int, default=3, help="Retry attempts on failure")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="Retry delay (seconds)")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="User-Agent header")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

def get_base64(path_or_url: str) -> str:
    p = pathlib.Path(path_or_url)
    if p.exists() and p.is_file():
        import base64
        ext = p.suffix.lower().replace('.', '')
        if ext == 'jpg': ext = 'jpeg'
        encoded = base64.b64encode(p.read_bytes()).decode()
        return f"data:image/{ext};base64,{encoded}"
    return path_or_url

def load_extra(extra_json: str | None) -> dict[str, Any]:
    if not extra_json: return {}
    try:
        data = json.loads(extra_json)
        allowed = {"quality", "style", "response_format", "user"}
        return {k: v for k, v in data.items() if k in allowed}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid --extra-json: {exc}")

def load_api_key(args: argparse.Namespace) -> str:
    api_key = os.getenv("AIMLAPI_API_KEY")
    if api_key: return api_key
    if args.apikey_file:
        key = pathlib.Path(args.apikey_file).read_text(encoding="utf-8").strip()
        if key: return key
    raise SystemExit("Missing AIMLAPI_API_KEY")

def request_json(url, payload, api_key, timeout, retry_max, retry_delay, user_agent, verbose):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": user_agent,
    }, method="POST")
    attempt = 0
    while True:
        try:
            if verbose: print(f"[debug] POST {url} attempt {attempt + 1}")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            if attempt < retry_max:
                attempt += 1
                time.sleep(retry_delay)
                continue
            raise SystemExit(f"Request failed: {exc}")

def main() -> None:
    args = parse_args()
    api_key = load_api_key(args)
    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "n": args.count,
        "size": args.size,
        **load_extra(args.extra_json),
    }
    if args.image_url:
        img_data = get_base64(args.image_url)
        if "flux" in args.model.lower(): payload["image_url"] = img_data
        else: payload["image"] = img_data

    url = f"{DEFAULT_BASE_URL.rstrip('/')}/images/generations"
    response = request_json(url, payload, api_key, args.timeout, args.retry_max, args.retry_delay, args.user_agent, args.verbose)
    data = response.get("data", [])
    if not data: raise SystemExit(f"No result: {response}")

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(data, start=1):
        url_value = item.get("url")
        file_path = out_dir / f"image-{int(time.time())}-{index}.png"
        req = urllib.request.Request(url_value, headers={"User-Agent": args.user_agent})
        with urllib.request.urlopen(req) as res:
            file_path.write_bytes(res.read())
    print(f"SUCCESS: {out_dir}")

if __name__ == "__main__":
    main()
