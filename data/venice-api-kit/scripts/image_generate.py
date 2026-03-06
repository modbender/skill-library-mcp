# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Image Generation

Generate images using Venice's /image/generate endpoint.
API docs: https://docs.venice.ai
"""

import argparse
import base64
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"

# Standard sizes supported by Venice (OpenAI-compatible endpoint)
VALID_SIZES = [
    "auto", "256x256", "512x512", "1024x1024",
    "1536x1024", "1024x1536", "1792x1024", "1024x1792"
]

# Output formats
VALID_FORMATS = ["jpeg", "png", "webp"]


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def list_styles(api_key: str) -> list[dict]:
    """List available image styles."""
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{VENICE_BASE_URL}/image/styles", headers=headers)
            response.raise_for_status()
            data = response.json()
            styles = data.get("data", data.get("styles", []))
            
            print("\nAvailable Image Styles:\n")
            for style in styles:
                style_id = style.get("id", "unknown")
                name = style.get("name", style_id)
                print(f"  {style_id}: {name}")
            print()
            return styles
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        sys.exit(1)


def generate_image(
    prompt: str,
    output: str | None = None,
    model: str = "flux-2-max",
    width: int = 1024,
    height: int = 1024,
    output_format: str = "webp",
    negative_prompt: str | None = None,
    seed: int | None = None,
    cfg_scale: float | None = None,
    steps: int | None = None,
    safe_mode: bool = True,
    hide_watermark: bool = False,
    embed_exif: bool = False,
) -> Path:
    """Generate an image using Venice AI's full /image/generate endpoint."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Build payload with all supported parameters
    payload: dict = {
        "model": model,
        "prompt": prompt[:7500],  # Max 7500 chars per API spec
        "width": width,
        "height": height,
        "format": output_format,
        "safe_mode": safe_mode,
        "hide_watermark": hide_watermark,
        "embed_exif_metadata": embed_exif,
    }

    # Optional parameters
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt[:7500]
    if seed is not None:
        payload["seed"] = seed
    if cfg_scale is not None:
        payload["cfg_scale"] = cfg_scale
    if steps is not None:
        payload["steps"] = steps

    print(f"Generating image with {model}...", file=sys.stderr)
    print(f"Size: {width}x{height}, Format: {output_format}", file=sys.stderr)
    print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", file=sys.stderr)

    try:
        with httpx.Client(timeout=180.0) as client:
            response = client.post(
                f"{VENICE_BASE_URL}/image/generate",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Response format: { id, images: [base64_string, ...], timing }
            images = data.get("images", [])
            if not images:
                print("Error: No images in response", file=sys.stderr)
                sys.exit(1)
            
            # Get the first image (base64 encoded)
            image_b64 = images[0]
            image_bytes = base64.b64decode(image_b64)
            
            # Generate output filename if not provided
            if not output:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                ext = output_format if output_format != "jpeg" else "jpg"
                output = f"venice-image-{timestamp}.{ext}"
            
            output_path = Path(output).resolve()
            output_path.write_bytes(image_bytes)
            
            # Log timing info if available
            timing = data.get("timing", {})
            if timing:
                total_ms = timing.get("total", 0)
                print(f"Generation time: {total_ms}ms", file=sys.stderr)
            
            print(f"Image saved to: {output_path}", file=sys.stderr)
            # MEDIA line for OpenClaw auto-attach
            print(f"MEDIA:{output_path}")
            
            return output_path

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"Details: {error_data}", file=sys.stderr)
        except Exception:
            print(f"Response: {e.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Venice AI"
    )
    parser.add_argument(
        "--prompt", "-p",
        help="Description of the image to generate (max 7500 chars)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output filename (default: auto-generated)"
    )
    parser.add_argument(
        "--model", "-m",
        default="flux-2-max",
        help="Model to use (default: flux-2-max)"
    )
    parser.add_argument(
        "--width", "-W",
        type=int,
        default=1024,
        help="Image width in pixels (default: 1024, max: 1280)"
    )
    parser.add_argument(
        "--height", "-H",
        type=int,
        default=1024,
        help="Image height in pixels (default: 1024, max: 1280)"
    )
    parser.add_argument(
        "--format", "-f",
        dest="output_format",
        choices=VALID_FORMATS,
        default="webp",
        help="Output format (default: webp)"
    )
    parser.add_argument(
        "--negative-prompt",
        help="What to avoid in the image"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed for reproducible generation (-999999999 to 999999999)"
    )
    parser.add_argument(
        "--cfg-scale",
        type=float,
        help="CFG scale 0-20 (higher = more prompt adherence)"
    )
    parser.add_argument(
        "--steps",
        type=int,
        help="Number of inference steps (model-dependent)"
    )
    parser.add_argument(
        "--unsafe",
        action="store_true",
        help="Disable safe mode (may return unblurred adult content)"
    )
    parser.add_argument(
        "--hide-watermark",
        action="store_true",
        help="Hide Venice watermark (may be ignored for some content)"
    )
    parser.add_argument(
        "--embed-exif",
        action="store_true",
        help="Embed prompt info in image EXIF metadata"
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List available styles and exit"
    )

    args = parser.parse_args()
    
    if args.list_styles:
        list_styles(get_api_key())
        return
    
    if not args.prompt:
        parser.error("--prompt is required (unless using --list-styles)")
    
    generate_image(
        prompt=args.prompt,
        output=args.output,
        model=args.model,
        width=args.width,
        height=args.height,
        output_format=args.output_format,
        negative_prompt=args.negative_prompt,
        seed=args.seed,
        cfg_scale=args.cfg_scale,
        steps=args.steps,
        safe_mode=not args.unsafe,
        hide_watermark=args.hide_watermark,
        embed_exif=args.embed_exif,
    )


if __name__ == "__main__":
    main()
