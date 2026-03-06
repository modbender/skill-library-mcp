#!/usr/bin/env python3
"""
🦞 Gradient AI — Image Generation

Generate images from text prompts using DigitalOcean's Gradient
Serverless Inference API.

Usage:
    python3 gradient_image.py --prompt "A lobster trading stocks"
    python3 gradient_image.py --prompt "Sunset over Wall Street" --output sunset.png
    python3 gradient_image.py --prompt "Logo design" --json

Docs: https://docs.digitalocean.com/products/gradient-ai-platform/how-to/use-serverless-inference/
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Optional

import requests

INFERENCE_BASE_URL = "https://inference.do-ai.run/v1"
IMAGE_GENERATION_URL = f"{INFERENCE_BASE_URL}/images/generations"

DEFAULT_IMAGE_MODEL = "dall-e-3"


def generate_image(
    prompt: str,
    model: str = DEFAULT_IMAGE_MODEL,
    api_key: Optional[str] = None,
    n: int = 1,
    size: str = "1024x1024",
) -> dict:
    """Generate images from a text prompt.

    Calls POST /v1/images/generations to create images.

    Args:
        prompt: Text description of the image to generate.
        model: Image generation model ID.
        api_key: Gradient Model Access Key. Falls back to GRADIENT_API_KEY.
        n: Number of images to generate.
        size: Image dimensions (e.g., '1024x1024').

    Returns:
        dict with 'success', 'images' (list of dicts with url/b64_json), and 'message'.
    """
    api_key = api_key or os.environ.get("GRADIENT_API_KEY", "")

    if not api_key:
        return {"success": False, "images": [], "message": "No GRADIENT_API_KEY configured."}

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
        }

        resp = requests.post(IMAGE_GENERATION_URL, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()

        data = resp.json()
        images = data.get("data", [])

        return {
            "success": True,
            "images": images,
            "message": f"Generated {len(images)} image(s). 🦞",
        }
    except requests.RequestException as e:
        return {"success": False, "images": [], "message": f"API request failed: {str(e)}"}


def save_image(image_data: dict, output_path: str) -> dict:
    """Save a generated image to disk.

    Handles both URL-based and base64-encoded image responses.
    The output path is validated to prevent path traversal attacks.

    Args:
        image_data: Image dict from generate_image() — has 'url' or 'b64_json'.
        output_path: Where to save the file (must stay within cwd).

    Returns:
        dict with 'success', 'path', and 'message'.
    """
    try:
        # Resolve to absolute path and validate against path traversal
        cwd = Path.cwd().resolve()
        output = (cwd / output_path).resolve()

        if not str(output).startswith(str(cwd)):
            return {
                "success": False,
                "path": "",
                "message": f"Path traversal denied: '{output_path}' escapes working directory.",
            }

        output.parent.mkdir(parents=True, exist_ok=True)

        if "b64_json" in image_data:
            img_bytes = base64.b64decode(image_data["b64_json"])
            output.write_bytes(img_bytes)
        elif "url" in image_data:
            resp = requests.get(image_data["url"], timeout=30)
            resp.raise_for_status()
            output.write_bytes(resp.content)
        else:
            return {"success": False, "path": "", "message": "No image data (expected 'url' or 'b64_json')."}

        return {
            "success": True,
            "path": str(output),
            "message": f"Saved to {output}",
        }
    except Exception as e:
        return {"success": False, "path": "", "message": f"Save failed: {str(e)}"}


# ─── CLI Interface ────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="🦞 Generate images with Gradient AI"
    )
    parser.add_argument("--prompt", required=True, help="Text prompt for image generation")
    parser.add_argument("--model", default=DEFAULT_IMAGE_MODEL, help="Image model ID")
    parser.add_argument("--output", default=None, help="Save image to this path")
    parser.add_argument("--size", default="1024x1024", help="Image size (e.g., 1024x1024)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = generate_image(
        prompt=args.prompt,
        model=args.model,
        size=args.size,
    )

    if not result["success"]:
        print(f"Error: {result['message']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    elif args.output and result["images"]:
        save_result = save_image(result["images"][0], args.output)
        if save_result["success"]:
            print(f"🖼️  {save_result['message']}")
        else:
            print(f"Error: {save_result['message']}", file=sys.stderr)
            sys.exit(1)
    elif result["images"]:
        # Print URL or indicate base64
        for i, img in enumerate(result["images"]):
            if "url" in img:
                print(f"Image {i + 1}: {img['url']}")
            elif "b64_json" in img:
                print(f"Image {i + 1}: [base64 data, {len(img['b64_json'])} chars] — use --output to save")
    else:
        print("No images were generated.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
