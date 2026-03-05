# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Image Upscaling

Upscale images using Venice's /image/upscale endpoint.
Returns binary PNG directly.
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


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def load_image_as_base64(image_path: str) -> str:
    """Load an image file and convert to base64."""
    path = Path(image_path)
    if not path.exists():
        print(f"Error: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    image_bytes = path.read_bytes()
    return base64.b64encode(image_bytes).decode("utf-8")


def upscale_image(
    image: str,
    output: str | None = None,
    scale: float = 2,
    enhance: bool = False,
    enhance_creativity: float | None = None,
    enhance_prompt: str | None = None,
    replication: float | None = None,
) -> Path:
    """Upscale an image using Venice AI.
    
    Returns binary PNG directly from the API.
    """
    api_key = get_api_key()

    # Validate scale
    if not 1 <= scale <= 4:
        print(f"Warning: Invalid scale {scale}. Using 2.", file=sys.stderr)
        scale = 2
    
    # Scale of 1 requires enhance=true
    if scale == 1 and not enhance:
        print("Note: Scale of 1 requires enhance=true, enabling enhance.", file=sys.stderr)
        enhance = True

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Handle image input (file path or URL)
    if image.startswith("http://") or image.startswith("https://"):
        image_input = image
    else:
        # It's a file path, convert to base64
        image_input = load_image_as_base64(image)

    payload: dict = {
        "image": image_input,
        "scale": scale,
        "enhance": enhance,  # API accepts boolean or string "true"/"false"
    }

    # Optional parameters
    if enhance_creativity is not None:
        payload["enhanceCreativity"] = enhance_creativity
    if enhance_prompt:
        payload["enhancePrompt"] = enhance_prompt
    if replication is not None:
        payload["replication"] = replication

    print(f"Upscaling image {scale}x (enhance={enhance})...", file=sys.stderr)

    try:
        with httpx.Client(timeout=180.0) as client:
            response = client.post(
                f"{VENICE_BASE_URL}/image/upscale",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # Response is binary PNG directly
            if not output:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                output = f"upscaled-{timestamp}.png"
            
            output_path = Path(output).resolve()
            output_path.write_bytes(response.content)
            
            print(f"Upscaled image saved to: {output_path}", file=sys.stderr)
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
        description="Upscale images using Venice AI"
    )
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Input image path or URL"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output filename (default: upscaled-{timestamp}.png)"
    )
    parser.add_argument(
        "--scale", "-s",
        type=float,
        default=2,
        help="Scale factor 1-4 (default: 2). Scale of 1 requires --enhance"
    )
    parser.add_argument(
        "--enhance", "-e",
        action="store_true",
        help="Enhance image using Venice's image engine during upscaling"
    )
    parser.add_argument(
        "--enhance-creativity",
        type=float,
        help="Enhancement creativity 0-1 (higher = more AI changes, 1 = new image)"
    )
    parser.add_argument(
        "--enhance-prompt",
        help="Style to apply during enhancement (e.g., 'gold', 'marble', 'cinematic')"
    )
    parser.add_argument(
        "--replication",
        type=float,
        help="How strongly to preserve lines/noise 0-1 (higher = less AI hallucination)"
    )

    args = parser.parse_args()
    
    upscale_image(
        image=args.image,
        output=args.output,
        scale=args.scale,
        enhance=args.enhance,
        enhance_creativity=args.enhance_creativity,
        enhance_prompt=args.enhance_prompt,
        replication=args.replication,
    )


if __name__ == "__main__":
    main()
