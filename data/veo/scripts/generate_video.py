#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
# ]
# ///
"""
Generate videos using Google's Veo API.

Usage:
    uv run generate_video.py --prompt "your video description" --filename "output.mp4" [--duration 8] [--aspect-ratio 16:9] [--model MODEL]
    uv run generate_video.py --prompt "your video description" --filename "output.mp4" --input-image "/path/to/image.png" [--duration 8] [--aspect-ratio 16:9] [--model MODEL]
    uv run generate_video.py --prompt "your video description" --filename "output.mp4" -i img1.png -i img2.png -i img3.png [--duration 8] [--aspect-ratio 16:9]
"""

import argparse
import os
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Generate video using Google Veo API"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Video description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., output.mp4)"
    )
    parser.add_argument(
        "--input-image", "-i",
        action="append",
        default=[],
        help="Input image file for image-to-video generation (repeatable, up to 3)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=8,
        help="Video duration in seconds (default: 8)"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=["16:9", "9:16", "1:1"],
        default="16:9",
        help="Aspect ratio (default: 16:9)"
    )
    parser.add_argument(
        "--model", "-m",
        default="veo-3.1-generate-preview",
        help="Veo model to use (default: veo-3.1-generate-preview)"
    )

    args = parser.parse_args()

    # Import after parsing to fail fast if google-genai isn't installed
    from google import genai
    from google.genai import types

    # Initialize client (relies on GEMINI_API_KEY env var)
    client = genai.Client()

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating video with model {args.model}...")
    print(f"  Prompt: {args.prompt}")
    print(f"  Duration: {args.duration}s")
    print(f"  Aspect ratio: {args.aspect_ratio}")
    for img in args.input_image:
        print(f"  Input image: {img}")

    # Validate input images
    if args.input_image and len(args.input_image) > 3:
        print("Error: Maximum 3 reference images allowed", file=sys.stderr)
        sys.exit(1)

    try:
        # Handle reference images
        reference_images = []
        if args.input_image:
            for image_path_str in args.input_image:
                image_path = Path(image_path_str)
                if not image_path.exists():
                    print(f"Error: Image file not found: {image_path}", file=sys.stderr)
                    sys.exit(1)

                print(f"Loading image: {image_path}")
                with open(image_path, "rb") as f:
                    image_data = f.read()

                # Create image object
                image_obj = types.Image(
                    imageBytes=image_data,
                    mimeType="image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
                )

                # Create VideoGenerationReferenceImage
                ref_image = types.VideoGenerationReferenceImage(
                    image=image_obj,
                    reference_type="asset"
                )
                reference_images.append(ref_image)

        # Generate video
        if reference_images:
            print("Generating video with reference images...")
            operation = client.models.generate_videos(
                model=args.model,
                prompt=args.prompt,
                config=types.GenerateVideosConfig(
                    duration_seconds=args.duration,
                    aspect_ratio=args.aspect_ratio,
                    reference_images=reference_images,
                )
            )
        else:
            # Text-to-video
            operation = client.models.generate_videos(
                model=args.model,
                prompt=args.prompt,
                config=types.GenerateVideosConfig(
                    duration_seconds=args.duration,
                    aspect_ratio=args.aspect_ratio,
                )
            )

        print(f"Operation started: {operation.name}")

        # Poll until done
        while not operation.done:
            print("Waiting for video generation to complete...")
            time.sleep(10)
            # Refresh operation state
            operation = client.operations.get(operation)

        print("Video generation complete!")
        print(f"Response type: {type(operation.response)}")
        print(f"Response dir: {[m for m in dir(operation.response) if not m.startswith('_')]}")

        # Get the generated video
        if not operation.response.generated_videos:
            print(f"Error: No generated_videos in response. Response: {operation.response}", file=sys.stderr)
            sys.exit(1)

        generated_video = operation.response.generated_videos[0]

        # Download the video
        print(f"Downloading video...")
        client.files.download(file=generated_video.video)
        generated_video.video.save(str(output_path))

        # Verify and report
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"\nVideo saved: {output_path} ({size_mb:.2f} MB)")
            print(f"MEDIA: {output_path}")
        else:
            print("Error: Video file was not saved.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating video: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
