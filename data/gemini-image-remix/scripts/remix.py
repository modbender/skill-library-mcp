#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Gemini Image Remix - Generate or remix images using Gemini 2.5 Flash Image.
"""

import argparse
import os
import sys
from pathlib import Path


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("GEMINI_API_KEY")


def main():
    parser = argparse.ArgumentParser(
        description="Gemini Image Remix - Generate or Remix images using Gemini 2.5 Flash"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Prompt for generation or modification")
    parser.add_argument("--filename", "-f", required=True, help="Output filename")
    parser.add_argument("--input-image", "-i", action="append", dest="input_images", help="Input image(s) to modify")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="1K")
    parser.add_argument("--aspect-ratio", "-a", choices=["1:1", "4:3", "3:4", "16:9", "9:16"], help="Aspect ratio (e.g., 1:1, 16:9)")
    parser.add_argument("--model", "-m", default="gemini-2.5-flash-image", help="Model to use (e.g., gemini-2.5-flash-image, gemini-3-pro-image-preview)")
    parser.add_argument("--api-key", "-k", help="Gemini API key")

    args = parser.parse_args()
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No GEMINI_API_KEY found.", file=sys.stderr)
        sys.exit(1)

    from google import genai
    from google.genai import types
    from PIL import Image as PILImage

    client = genai.Client(api_key=api_key)
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    input_images = []
    output_resolution = args.resolution
    if args.input_images:
        max_input_dim = 0
        for img_path in args.input_images:
            img = PILImage.open(img_path)
            input_images.append(img)
            width, height = img.size
            max_input_dim = max(max_input_dim, width, height)
        
        if args.resolution == "1K" and max_input_dim > 0:
            if max_input_dim >= 3000: output_resolution = "4K"
            elif max_input_dim >= 1500: output_resolution = "2K"

    # For Gemini 2.5 Flash / Gemini 3 Flash, the multimodal contents are built similarly.
    contents = [*input_images, args.prompt] if input_images else args.prompt

    try:
        image_config = types.ImageConfig(image_size=output_resolution)
        if args.aspect_ratio:
            image_config.aspect_ratio = args.aspect_ratio

        response = client.models.generate_content(
            model=args.model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=image_config
            )
        )

        image_saved = False
        for part in response.parts:
            if part.inline_data:
                from io import BytesIO
                image_data = part.inline_data.data
                image = PILImage.open(BytesIO(image_data))
                if image.mode == 'RGBA':
                    rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    image = rgb_image
                image.save(str(output_path), 'PNG')
                image_saved = True

        if image_saved:
            print(f"MEDIA: {output_path.resolve()}")
        else:
            print("Error: No image generated.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
