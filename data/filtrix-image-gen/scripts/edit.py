#!/usr/bin/env python3
"""
Filtrix Image Editor — unified multi-provider image-to-image editing.
Providers: openai (gpt-image-1), gemini (gemini-2.5-flash-image / gemini-3-pro-image-preview), fal (seedream4/4.5)

Usage:
  python edit.py --provider gemini --image input.png --prompt "make it look like a watercolor painting"
  python edit.py --provider openai --image photo.jpg --prompt "remove the background" --mask mask.png
  python edit.py --provider fal --image photo.png --prompt "change hair color to blue" --model seedream45

Environment variables required per provider:
  openai: OPENAI_API_KEY
  gemini: GOOGLE_API_KEY
  fal:    FAL_KEY
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Size / aspect-ratio mappings
# ---------------------------------------------------------------------------

GEMINI_ASPECT_MAP = {
    "1024x1024": "1:1",
    "1536x1024": "16:9",
    "1024x1536": "9:16",
    "3:2": "3:2", "4:3": "4:3", "16:9": "16:9", "21:9": "21:9",
    "9:16": "9:16", "3:4": "3:4", "1:1": "1:1",
}

FAL_SIZE_MAP = {
    "1024x1024": {"width": 1024, "height": 1024},
    "1536x1024": {"width": 1536, "height": 1024},
    "1024x1536": {"width": 1024, "height": 1536},
    "4096x4096": {"width": 4096, "height": 4096},
    "3840x2160": {"width": 3840, "height": 2160},
    "2160x3840": {"width": 2160, "height": 3840},
}

FAL_MODELS = {
    "seedream4": "fal-ai/bytedance/seedream/v4/edit",
    "seedream45": "fal-ai/bytedance/seedream/v4.5/edit",
}


def _read_image_b64(path: str) -> tuple[str, str]:
    """Read image file and return (base64_data, mime_type)."""
    data = Path(path).read_bytes()
    mime = mimetypes.guess_type(path)[0] or "image/png"
    return base64.b64encode(data).decode(), mime


# ---------------------------------------------------------------------------
# Provider: OpenAI (gpt-image-1 edit)
# ---------------------------------------------------------------------------

def edit_openai(prompt: str, image: str, mask: str | None, **_) -> bytes:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    # Build multipart form data
    boundary = "----FormBoundary" + os.urandom(8).hex()
    body_parts = []

    def add_field(name: str, value: str):
        body_parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        )

    def add_file(name: str, filepath: str):
        filename = Path(filepath).name
        mime = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
        data = Path(filepath).read_bytes()
        body_parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        )
        body_parts.append(data)
        body_parts.append(b"\r\n")

    add_field("model", "gpt-image-1")
    add_field("prompt", prompt)
    add_field("quality", "high")
    add_file("image[]", image)
    if mask:
        add_file("mask", mask)

    body_parts.append(f"--{boundary}--\r\n")

    # Combine parts into bytes
    body = b""
    for part in body_parts:
        body += part.encode() if isinstance(part, str) else part

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/edits",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        raise RuntimeError(f"OpenAI API error {e.code}: {err_body}")

    b64 = result.get("data", [{}])[0].get("b64_json")
    if not b64:
        url = result.get("data", [{}])[0].get("url")
        if url:
            with urllib.request.urlopen(url) as img_resp:
                return img_resp.read()
        raise RuntimeError("No image data in OpenAI edit response")

    return base64.b64decode(b64)


# ---------------------------------------------------------------------------
# Provider: Gemini (image edit via multimodal content)
# ---------------------------------------------------------------------------

def edit_gemini(prompt: str, image: str, resolution: str | None = None,
                size: str | None = None, model: str | None = None, **_) -> bytes:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")

    model = model or "gemini-2.5-flash-image"
    img_b64, mime = _read_image_b64(image)

    # Build content parts: text + image
    contents = [{
        "parts": [
            {"text": prompt},
            {"inlineData": {"mimeType": mime, "data": img_b64}},
        ]
    }]

    # Build config
    config: dict = {
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
        }
    }

    image_config: dict = {}
    if resolution and resolution in ("1K", "2K", "4K"):
        image_config["imageSize"] = resolution
    if size:
        aspect = GEMINI_ASPECT_MAP.get(size)
        if aspect:
            image_config["aspectRatio"] = aspect
    if image_config:
        config["generationConfig"]["imageConfig"] = image_config

    payload = json.dumps({"contents": contents, **config}).encode()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        raise RuntimeError(f"Gemini API error {e.code}: {err_body}")

    candidates = body.get("candidates", [])
    if not candidates:
        raise RuntimeError("No candidates in Gemini response")

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        inline = part.get("inlineData", {})
        if inline.get("data"):
            return base64.b64decode(inline["data"])

    finish = candidates[0].get("finishReason", "")
    if finish == "IMAGE_SAFETY":
        raise RuntimeError("Blocked by Gemini safety filter. Try a different prompt.")

    raise RuntimeError("No image data in Gemini edit response")


# ---------------------------------------------------------------------------
# Provider: fal.ai (SeedReam edit)
# ---------------------------------------------------------------------------

def edit_fal(prompt: str, image: str, model: str | None = None,
             size: str | None = None, seed: int | None = None, **_) -> bytes:
    api_key = os.environ.get("FAL_KEY")
    if not api_key:
        raise RuntimeError("FAL_KEY not set")

    model_id = FAL_MODELS.get(model or "seedream45")
    if not model_id:
        model_id = model

    # Convert image to data URI
    img_b64, mime = _read_image_b64(image)
    data_uri = f"data:{mime};base64,{img_b64}"

    dims = FAL_SIZE_MAP.get(size or "1024x1024", {"width": 1024, "height": 1024})

    arguments = {
        "prompt": prompt,
        "image_size": {"width": dims["width"], "height": dims["height"]},
        "num_images": 1,
        "max_images": 1,
        "enable_safety_checker": False,
        "enhance_prompt_mode": "standard",
        "sync_mode": True,
        "image_urls": [data_uri],
    }
    if seed is not None:
        arguments["seed"] = seed

    url = f"https://fal.run/{model_id}"
    payload = json.dumps(arguments).encode()
    req = urllib.request.Request(
        url, data=payload,
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

    images = body.get("images", [])
    if not images:
        raise RuntimeError(f"No images in fal response: {json.dumps(body)[:500]}")

    img_url = images[0].get("url", "")

    # Handle data URI (sync_mode) or HTTP URL
    if img_url.startswith("data:"):
        b64_data = img_url.split(",", 1)[1]
        return base64.b64decode(b64_data)
    else:
        with urllib.request.urlopen(img_url) as img_resp:
            return img_resp.read()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

PROVIDERS = {
    "openai": edit_openai,
    "gemini": edit_gemini,
    "fal": edit_fal,
}

def main():
    parser = argparse.ArgumentParser(description="Edit images via AI providers (image-to-image)")
    parser.add_argument("--provider", required=True, choices=list(PROVIDERS.keys()),
                        help="AI provider to use")
    parser.add_argument("--image", required=True, help="Input image file path")
    parser.add_argument("--prompt", required=True, help="Edit instruction prompt")
    parser.add_argument("--mask", default=None, help="Mask image (openai only)")
    parser.add_argument("--size", default=None,
                        help="Output size (WxH or aspect ratio like 16:9)")
    parser.add_argument("--model", default=None, help="Override default model")
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (fal only)")
    parser.add_argument("--resolution", default=None, choices=["1K", "2K", "4K"],
                        help="Output resolution (gemini only, requires gemini-3-pro-image-preview)")
    args = parser.parse_args()

    # Validate input image exists
    if not Path(args.image).exists():
        print(f"ERROR: Input image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    # Default output path
    if not args.output:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"/tmp/filtrix_edit_{args.provider}_{ts}.png"

    # Build kwargs
    kwargs = {
        "prompt": args.prompt,
        "image": args.image,
        "model": args.model,
        "size": args.size,
    }
    if args.provider == "openai":
        kwargs["mask"] = args.mask
    if args.provider == "gemini":
        kwargs["resolution"] = args.resolution
    if args.provider == "fal":
        kwargs["seed"] = args.seed

    provider_fn = PROVIDERS[args.provider]

    try:
        image_bytes = provider_fn(**kwargs)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)

    print(f"OK: {out_path} ({len(image_bytes)} bytes)")


if __name__ == "__main__":
    main()
