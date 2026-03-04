#!/usr/bin/env python3
"""
Filtrix Image Generator — unified multi-provider image generation.
Providers: openai (gpt-image-1), gemini (gemini-2.5-flash-image), fal (seedream3)

Usage:
  python generate.py --provider openai --prompt "a cat in space" --size 1024x1024 --output /tmp/out.png
  python generate.py --provider gemini --prompt "sunset over mountains" --size 1536x1024
  python generate.py --provider fal --prompt "cyberpunk city" --model seedream3 --output ./image.png

Environment variables required per provider:
  openai: OPENAI_API_KEY
  gemini: GOOGLE_API_KEY
  fal:    FAL_KEY
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Size / aspect-ratio mappings
# ---------------------------------------------------------------------------

OPENAI_SIZES = {"1024x1024", "1536x1024", "1024x1536", "auto"}

GEMINI_ASPECT_MAP = {
    "1024x1024": "1:1",
    "1536x1024": "16:9",
    "1024x1536": "9:16",
    "3:2": "3:2",
    "4:3": "4:3",
    "16:9": "16:9",
    "21:9": "21:9",
    "9:16": "9:16",
    "3:4": "3:4",
    "1:1": "1:1",
}

FAL_SIZE_MAP = {
    "1024x1024": {"width": 1024, "height": 1024},
    "1536x1024": {"width": 1536, "height": 1024},
    "1024x1536": {"width": 1024, "height": 1536},
}

# ---------------------------------------------------------------------------
# Provider: OpenAI (gpt-image-1)
# ---------------------------------------------------------------------------

def generate_openai(prompt: str, size: str, model: str | None) -> bytes:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    safe_size = size if size in OPENAI_SIZES else "1024x1024"
    model = model or "gpt-image-1"

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "size": safe_size,
        "n": 1,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        raise RuntimeError(f"OpenAI API error {e.code}: {err_body}")

    b64 = body.get("data", [{}])[0].get("b64_json")
    if not b64:
        # Try URL fallback
        url = body.get("data", [{}])[0].get("url")
        if url:
            with urllib.request.urlopen(url) as img_resp:
                return img_resp.read()
        raise RuntimeError("No image data in OpenAI response")

    return base64.b64decode(b64)


# ---------------------------------------------------------------------------
# Provider: Gemini (gemini-2.5-flash-image)
# ---------------------------------------------------------------------------

def generate_gemini(prompt: str, size: str, model: str | None, resolution: str | None = None) -> bytes:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")

    # Default to Flash (cheaper). Use --model gemini-3-pro-image-preview for higher quality.
    model = model or "gemini-2.5-flash-image"
    aspect = GEMINI_ASPECT_MAP.get(size, "1:1")

    image_config: dict = {"aspectRatio": aspect}
    # Gemini 3 Pro supports imageSize for higher resolutions (1K, 2K, 4K)
    if resolution and resolution in ("1K", "2K", "4K"):
        image_config["imageSize"] = resolution

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": image_config,
        },
    }).encode()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        raise RuntimeError(f"Gemini API error {e.code}: {err_body}")

    # Extract image from response
    candidates = body.get("candidates", [])
    if not candidates:
        raise RuntimeError("No candidates in Gemini response")

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        inline = part.get("inlineData", {})
        if inline.get("data"):
            return base64.b64decode(inline["data"])

    # Check for safety block
    finish = candidates[0].get("finishReason", "")
    if finish == "IMAGE_SAFETY":
        raise RuntimeError("Blocked by Gemini safety filter. Try a different prompt.")

    raise RuntimeError("No image data in Gemini response")


# ---------------------------------------------------------------------------
# Provider: fal.ai (SeedReam, etc.)
# ---------------------------------------------------------------------------

FAL_MODELS = {
    "seedream4": "fal-ai/bytedance/seedream/v4/text-to-image",
    "seedream45": "fal-ai/bytedance/seedream/v4.5/text-to-image",
    "flux-pro": "fal-ai/flux-pro/v1.1",
    "flux-dev": "fal-ai/flux/dev",
    "recraft-v3": "fal-ai/recraft-v3",
}

def generate_fal(prompt: str, size: str, model: str | None, seed: int | None) -> bytes:
    api_key = os.environ.get("FAL_KEY")
    if not api_key:
        raise RuntimeError("FAL_KEY not set")

    model_id = FAL_MODELS.get(model or "seedream45")
    if not model_id:
        model_id = model  # Allow raw fal model IDs

    dims = FAL_SIZE_MAP.get(size, {"width": 1024, "height": 1024})

    arguments = {
        "prompt": prompt,
        "image_size": {"width": dims["width"], "height": dims["height"]},
        "num_images": 1,
    }
    if seed is not None:
        arguments["seed"] = seed

    # Use synchronous endpoint (waits for result)
    url = f"https://fal.run/{model_id}"
    payload = json.dumps(arguments).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        raise RuntimeError(f"fal.ai API error {e.code}: {err_body}")

    # Extract image URL from response
    images = body.get("images", [])
    if not images:
        raise RuntimeError(f"No images in fal response: {json.dumps(body)[:500]}")

    img_url = images[0].get("url")
    if not img_url:
        raise RuntimeError("No image URL in fal response")

    with urllib.request.urlopen(img_url) as img_resp:
        return img_resp.read()


def _poll_fal(api_key: str, model_id: str, request_id: str, max_wait: int = 120) -> str:
    """Poll fal.ai queue until result is ready."""
    import time
    status_url = f"https://queue.fal.run/{model_id}/requests/{request_id}/status"
    result_url = f"https://queue.fal.run/{model_id}/requests/{request_id}"

    for _ in range(max_wait // 2):
        req = urllib.request.Request(status_url, headers={"Authorization": f"Key {api_key}"})
        with urllib.request.urlopen(req) as resp:
            status = json.loads(resp.read())

        if status.get("status") == "COMPLETED":
            req = urllib.request.Request(result_url, headers={"Authorization": f"Key {api_key}"})
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
            return result.get("images", [{}])[0].get("url", "")

        if status.get("status") in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"fal.ai job failed: {status}")

        time.sleep(2)

    raise RuntimeError("fal.ai job timed out")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

PROVIDERS = {
    "openai": generate_openai,
    "gemini": generate_gemini,
    "fal": generate_fal,
}

def main():
    parser = argparse.ArgumentParser(description="Generate images via AI providers")
    parser.add_argument("--provider", required=True, choices=list(PROVIDERS.keys()),
                        help="AI provider to use")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--size", default="1024x1024",
                        help="Image size (1024x1024, 1536x1024, 1024x1536)")
    parser.add_argument("--model", default=None,
                        help="Override default model for the provider")
    parser.add_argument("--output", default=None,
                        help="Output file path (default: auto-generated in /tmp)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed (fal provider only)")
    parser.add_argument("--resolution", default=None, choices=["1K", "2K", "4K"],
                        help="Output resolution (gemini provider only, requires gemini-3-pro-image-preview)")
    args = parser.parse_args()

    # Default output path
    if not args.output:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"/tmp/filtrix_{args.provider}_{ts}.png"

    # Generate
    provider_fn = PROVIDERS[args.provider]
    kwargs = {"prompt": args.prompt, "size": args.size, "model": args.model}
    if args.provider == "fal":
        kwargs["seed"] = args.seed
    if args.provider == "gemini":
        kwargs["resolution"] = args.resolution

    try:
        image_bytes = provider_fn(**kwargs)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Save
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)

    print(f"OK: {out_path} ({len(image_bytes)} bytes)")


if __name__ == "__main__":
    main()
