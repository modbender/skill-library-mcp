#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Generate or edit images using OpenRouter's image generation via /chat/completions.

Examples:
    uv run generate_image.py --prompt "A red fox in snow" --filename "fox.png" --aspect-ratio 16:9 --image-size 2K
    uv run generate_image.py --prompt "Make it watercolor" --filename "fox-edit.png" --input-image "fox.png"
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path
from urllib import error, request


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
ASPECT_RATIO_CHOICES = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
IMAGE_SIZE_CHOICES = ["1K", "2K", "4K"]


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("OPENROUTER_API_KEY")


def load_input_image_data_url(image_path: str) -> str:
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input image not found: {image_path}")

    data = path.read_bytes()
    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type:
        mime_type = "application/octet-stream"

    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_payload(args: argparse.Namespace) -> dict:
    if args.input_image:
        data_url = load_input_image_data_url(args.input_image)
        content: str | list[dict] = [
            {"type": "text", "text": args.prompt},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]
    else:
        # Match OpenRouter's basic image-generation examples for text-to-image.
        content = args.prompt

    payload: dict = {
        "model": args.model,
        "modalities": ["image", "text"],
        "messages": [{"role": "user", "content": content}],
    }

    image_config: dict = {}
    if args.aspect_ratio:
        image_config["aspect_ratio"] = args.aspect_ratio
    if args.image_size:
        image_config["image_size"] = args.image_size
    if args.image_config_json:
        try:
            extra = json.loads(args.image_config_json)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid --image-config-json: {exc}") from exc
        if not isinstance(extra, dict):
            raise ValueError("--image-config-json must decode to a JSON object")
        image_config.update(extra)

    if image_config:
        payload["image_config"] = image_config

    return payload


def build_headers(args: argparse.Namespace, api_key: str) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    site_url = args.site_url or os.environ.get("OPENROUTER_SITE_URL")
    app_name = args.app_name or os.environ.get("OPENROUTER_APP_NAME")
    if site_url:
        headers["HTTP-Referer"] = site_url
    if app_name:
        headers["X-Title"] = app_name

    return headers


def extract_text_message(message: dict) -> str | None:
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
        if parts:
            return "\n".join(parts)

    return None


def extract_first_image_data(response_json: dict) -> tuple[bytes, str | None]:
    choices = response_json.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("No choices in response")

    first = choices[0] or {}
    message = first.get("message") or {}
    images = message.get("images")
    if not isinstance(images, list) or not images:
        raise ValueError("No image found in response (message.images missing)")

    first_image = images[0] or {}
    image_url_obj = first_image.get("image_url") or {}
    url = image_url_obj.get("url")
    if not isinstance(url, str) or not url:
        raise ValueError("No image URL found in response image object")

    if not url.startswith("data:"):
        raise ValueError("Image URL is not a data URL; remote URLs are not handled by this script")

    header, _, payload = url.partition(",")
    if not payload or ";base64" not in header:
        raise ValueError("Unsupported data URL format in image response")

    mime_type = None
    if header.startswith("data:"):
        mime_type = header[5:].split(";")[0] or None

    try:
        image_bytes = base64.b64decode(payload)
    except Exception as exc:
        raise ValueError(f"Failed to decode base64 image data: {exc}") from exc

    return image_bytes, mime_type


def api_request(payload: dict, headers: dict[str, str]) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(OPENROUTER_URL, data=body, headers=headers, method="POST")

    try:
        with request.urlopen(req, timeout=180) as resp:
            raw = resp.read()
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {details}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error: {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        text = raw.decode("utf-8", errors="replace")
        raise RuntimeError(f"Invalid JSON response: {text[:500]}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or edit images using OpenRouter image generation"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt or edit instructions")
    parser.add_argument("--filename", "-f", required=True, help="Output filename/path")
    parser.add_argument("--input-image", "-i", help="Optional input image path for editing")
    parser.add_argument("--model", "-m", required=True, help="OpenRouter model ID (required)")
    parser.add_argument(
        "--aspect-ratio",
        choices=ASPECT_RATIO_CHOICES,
        help="image_config.aspect_ratio (e.g. 1:1, 16:9)",
    )
    parser.add_argument(
        "--image-size",
        choices=IMAGE_SIZE_CHOICES,
        help="image_config.image_size (OpenRouter docs: 1K, 2K, 4K)",
    )
    parser.add_argument("--image-config-json", help="JSON object merged into image_config")
    parser.add_argument("--api-key", "-k", help="OpenRouter API key (overrides OPENROUTER_API_KEY)")
    parser.add_argument("--site-url", help="Optional HTTP-Referer header (or OPENROUTER_SITE_URL env var)")
    parser.add_argument("--app-name", help="Optional X-Title header (or OPENROUTER_APP_NAME env var)")

    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set OPENROUTER_API_KEY environment variable", file=sys.stderr)
        return 1

    try:
        payload = build_payload(args)
    except FileNotFoundError as exc:
        print(f"Error loading input image: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    headers = build_headers(args, api_key)

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    mode_label = "Editing image" if args.input_image else "Generating image"
    print(f"{mode_label} via OpenRouter...")
    print(f"Model: {args.model}")
    if "image_config" in payload:
        print(f"Image config: {json.dumps(payload['image_config'])}")

    try:
        response_json = api_request(payload, headers)
    except RuntimeError as exc:
        print(f"Error generating image: {exc}", file=sys.stderr)
        return 1

    choices = response_json.get("choices") or []
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message") or {}
        text = extract_text_message(message)
        if text:
            print(f"Model response: {text}")

    try:
        image_bytes, mime_type = extract_first_image_data(response_json)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output_path.write_bytes(image_bytes)
    full_path = output_path.resolve()
    print(f"Image saved: {full_path}")
    if mime_type:
        print(f"Detected MIME type: {mime_type}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
