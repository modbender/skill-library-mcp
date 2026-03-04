# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Image Editing

Edit images using Venice's /image/edit endpoint.
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

# Available edit models from swagger
AVAILABLE_MODELS = [
    "qwen-edit",           # default
    "flux-2-max-edit",
    "gpt-image-1-5-edit",
    "nano-banana-pro-edit",
    "seedream-v4-edit",
]

AVAILABLE_ASPECT_RATIOS = [
    "auto", "1:1", "3:2", "16:9", "21:9", "9:16", "2:3", "3:4"
]


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


def edit_image(
    image: str,
    prompt: str,
    output: str | None = None,
    model_id: str = "qwen-edit",
    aspect_ratio: str | None = None,
) -> Path:
    """Edit an image using Venice AI.
    
    Returns binary PNG directly from the API.
    """
    api_key = get_api_key()

    if model_id not in AVAILABLE_MODELS:
        print(f"Warning: Unknown model '{model_id}'. Available: {', '.join(AVAILABLE_MODELS)}", file=sys.stderr)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Handle image input (file path or URL)
    if image.startswith("http://") or image.startswith("https://"):
        image_input = image
    else:
        image_input = load_image_as_base64(image)

    payload: dict = {
        "image": image_input,
        "prompt": prompt[:32768],  # Max 32768 chars per API spec
        "modelId": model_id,  # NOTE: API uses modelId, not model!
    }

    if aspect_ratio:
        if aspect_ratio not in AVAILABLE_ASPECT_RATIOS:
            print(f"Warning: Invalid aspect ratio '{aspect_ratio}'", file=sys.stderr)
        else:
            payload["aspect_ratio"] = aspect_ratio

    print(f"Editing image with {model_id}...", file=sys.stderr)
    print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", file=sys.stderr)

    try:
        with httpx.Client(timeout=180.0) as client:
            response = client.post(
                f"{VENICE_BASE_URL}/image/edit",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # Response is binary PNG directly
            if not output:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                output = f"edited-{timestamp}.png"
            
            output_path = Path(output).resolve()
            output_path.write_bytes(response.content)
            
            # Log model info from headers if available
            model_name = response.headers.get("x-venice-model-name", model_id)
            print(f"Edited with: {model_name}", file=sys.stderr)
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
        description="Edit images using Venice AI"
    )
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Input image path or URL"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Edit instructions (e.g., 'remove the tree', 'change sky to sunset')"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output filename (default: edited-{timestamp}.png)"
    )
    parser.add_argument(
        "--model", "-m",
        dest="model_id",
        default="qwen-edit",
        choices=AVAILABLE_MODELS,
        help="Model to use (default: qwen-edit)"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=AVAILABLE_ASPECT_RATIOS,
        help="Output aspect ratio (default: same as input)"
    )

    args = parser.parse_args()
    
    edit_image(
        image=args.image,
        prompt=args.prompt,
        output=args.output,
        model_id=args.model_id,
        aspect_ratio=args.aspect_ratio,
    )


if __name__ == "__main__":
    main()
