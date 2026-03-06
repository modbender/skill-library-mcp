# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Background Removal

Remove backgrounds from images using Venice's /image/background-remove endpoint.
Returns binary PNG with transparent background.
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


def remove_background(
    image: str,
    output: str | None = None,
) -> Path:
    """Remove background from an image using Venice AI.
    
    Returns binary PNG with transparent background.
    """
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Handle image input - API supports image (base64) or image_url
    payload: dict = {}
    
    if image.startswith("http://") or image.startswith("https://"):
        payload["image_url"] = image
    else:
        payload["image"] = load_image_as_base64(image)

    print("Removing background...", file=sys.stderr)

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{VENICE_BASE_URL}/image/background-remove",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # Response is binary PNG with transparent background
            if not output:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                output = f"no-background-{timestamp}.png"
            
            output_path = Path(output).resolve()
            output_path.write_bytes(response.content)
            
            print(f"Image saved to: {output_path}", file=sys.stderr)
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
        description="Remove background from images using Venice AI"
    )
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Input image path or URL"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output filename (default: no-background-{timestamp}.png)"
    )

    args = parser.parse_args()
    
    remove_background(
        image=args.image,
        output=args.output,
    )


if __name__ == "__main__":
    main()
