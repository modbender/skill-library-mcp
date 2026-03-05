#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.0.0",
#     "requests",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using APIYI API.

Usage:
    # Slash command mode (args are the prompt)
    uv run generate_image.py "a cute cat" -f cat.png
    
    # Natural language mode
    uv run generate_image.py --prompt "a cute cat" --filename "cat.png"
"""

import argparse
import os
import sys
from pathlib import Path


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("APIYI_API_KEY")


def generate_image(prompt: str, output_path: Path, resolution: str):
    """Generate image using APIYI API."""
    from openai import OpenAI
    import requests
    from PIL import Image as PILImage
    from io import BytesIO

    api_key = os.environ.get("APIYI_API_KEY")
    if not api_key:
        raise ValueError("APIYI_API_KEY environment variable not set")

    # Map resolution to APIYI size format
    size_map = {
        "1K": "1024x1024",
        "2K": "2048x2048",
        "4K": "4096x4096"
    }
    size = size_map.get(resolution, "1024x1024")

    print(f"Generating image with APIYI API (resolution: {resolution}, size: {size})...")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.apiyi.com/v1"
    )

    response = client.images.generate(
        model="nano-banana-pro",
        prompt=prompt,
        n=1,
        size=size,
        quality="hd"
    )

    # Download and save image
    if response.data and len(response.data) > 0:
        image_url = response.data[0].url
        print(f"Image URL: {image_url}")
        
        # Download image
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        
        image = PILImage.open(BytesIO(img_response.content))
        if image.mode == 'RGBA':
            rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            rgb_image.save(str(output_path), 'PNG')
        else:
            image.convert('RGB').save(str(output_path), 'PNG')
        return True

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using APIYI API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Slash command:  uv run generate_image.py "a cute cat" -f cat.png
  Long form:      uv run generate_image.py --prompt "a cute cat" --filename cat.png
  With resolution: uv run generate_image.py "a sunset" -f sunset.png -r 2K
        """
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Image description (positional, for slash command mode)"
    )
    parser.add_argument(
        "--prompt", "-p",
        dest="prompt_opt",
        help="Image description/prompt (option form)"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., sunset-mountains.png)"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="APIYI API key (overrides APIYI_API_KEY env var)"
    )

    args = parser.parse_args()
    
    # Merge positional and optional prompt
    if args.prompt_opt:
        prompt = args.prompt_opt
    elif args.prompt:
        prompt = args.prompt
    else:
        print("Error: No prompt provided.", file=sys.stderr)
        print("Usage: generate_image.py <prompt> -f <filename>", file=sys.stderr)
        print("   or: generate_image.py --prompt <prompt> --filename <filename>", file=sys.stderr)
        sys.exit(1)

    # Validate API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set APIYI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Set up output path
    output_filename = Path(args.filename)
    if output_filename.is_absolute():
        # Explicit absolute path - use as-is (caller's responsibility)
        output_path = output_filename
        print(f"Using explicit output path: {output_path}")
    else:
        # Relative path - output to current working directory (caller's workspace)
        workspace_root = Path.cwd()
        output_path = workspace_root / args.filename
        print(f"Using workspace output: {output_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate image
    try:
        success = generate_image(prompt, output_path, args.resolution)

        if success:
            full_path = output_path.resolve()
            print(f"\nImage saved: {full_path}")
            print(f"MEDIA: {full_path}")
        else:
            print("Error: No image was generated.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
