#!/usr/bin/env python3
"""
DrawThings Image Generation Script

Generate images using the DrawThings API (Automatic1111-compatible).
"""

import argparse
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip3 install requests", file=sys.stderr)
    sys.exit(1)


PRESETS = {
    "fast": {
        "steps": 8,
        "sampler_name": "UniPC Trailing",
        "cfg_scale": 1.0,
    },
    "quality": {
        "steps": 30,
        "sampler_name": "DPM++ 2M Karras",
        "cfg_scale": 7.5,
    },
    "nft": {
        "steps": 20,
        "sampler_name": "DPM++ 2M Karras",
        "cfg_scale": 7.0,
        "width": 512,
        "height": 512,
    },
}


def generate_image(
    prompt: str,
    negative_prompt: str = "",
    steps: int = 20,
    sampler_name: str = "DPM++ 2M Karras",
    cfg_scale: float = 7.0,
    width: int = 512,
    height: int = 512,
    batch_size: int = 1,
    seed: int = -1,
    api_url: Optional[str] = None,
) -> dict:
    """Generate image(s) using DrawThings API."""
    
    if api_url is None:
        api_url = os.environ.get("DRAWTHINGS_URL", "http://127.0.0.1:7860")
    
    endpoint = f"{api_url.rstrip('/')}/sdapi/v1/txt2img"
    
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "sampler_name": sampler_name,
        "cfg_scale": cfg_scale,
        "width": width,
        "height": height,
        "batch_size": batch_size,
        "seed": seed,
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to DrawThings at {api_url}", file=sys.stderr)
        print("Make sure DrawThings is running and API server is enabled.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out (>300s). Try reducing steps or dimensions.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {e.response.status_code}", file=sys.stderr)
        print(e.response.text, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def save_images(result: dict, output_path: Optional[str] = None, prompt: str = "") -> list[str]:
    """Save generated images to disk."""
    
    images = result.get("images", [])
    if not images:
        print("Error: No images in response", file=sys.stderr)
        sys.exit(1)
    
    saved_paths = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for idx, img_base64 in enumerate(images):
        # Decode base64 image
        img_data = base64.b64decode(img_base64)
        
        # Determine output path
        if output_path:
            if len(images) == 1:
                path = Path(output_path)
            else:
                # Multiple images: append index
                path = Path(output_path)
                path = path.parent / f"{path.stem}_{idx+1}{path.suffix}"
        else:
            # Default naming
            suffix = f"_{idx+1}" if len(images) > 1 else ""
            path = Path(f"drawthings_output_{timestamp}{suffix}.png")
        
        # Create parent directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write image
        path.write_bytes(img_data)
        saved_paths.append(str(path))
        print(f"Saved: {path}")
    
    # Save generation info
    info = result.get("info", {})
    if isinstance(info, str):
        try:
            info = json.loads(info)
        except:
            pass
    
    if info and saved_paths:
        info_path = Path(saved_paths[0]).with_suffix(".json")
        info_data = {
            "prompt": prompt,
            "parameters": info,
            "timestamp": timestamp,
            "files": saved_paths,
        }
        info_path.write_text(json.dumps(info_data, indent=2))
        print(f"Info: {info_path}")
    
    return saved_paths


def main():
    parser = argparse.ArgumentParser(
        description="Generate images with DrawThings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "a cute cat"
  %(prog)s "cyberpunk city" --steps 30 --cfg-scale 8
  %(prog)s "landscape" --preset quality --width 1024 --height 1024
  %(prog)s "character design" --batch-size 5 --output ./outputs/character.png
        """
    )
    
    parser.add_argument("prompt", help="Text prompt describing the image")
    parser.add_argument("--negative-prompt", default="", help="Negative prompt (what to avoid)")
    parser.add_argument("--steps", type=int, default=20, help="Number of diffusion steps (default: 20)")
    parser.add_argument("--sampler", "--sampler-name", dest="sampler_name", 
                        default="DPM++ 2M Karras", help="Sampler algorithm (default: DPM++ 2M Karras)")
    parser.add_argument("--cfg-scale", type=float, default=7.0, 
                        help="Classifier-free guidance scale (default: 7.0)")
    parser.add_argument("--width", type=int, default=512, help="Image width (default: 512)")
    parser.add_argument("--height", type=int, default=512, help="Image height (default: 512)")
    parser.add_argument("--batch-size", type=int, default=1, help="Number of images to generate (default: 1)")
    parser.add_argument("--seed", type=int, default=-1, help="Random seed (-1 for random)")
    parser.add_argument("--output", "-o", help="Output file path (default: auto-generated)")
    parser.add_argument("--api-url", help="DrawThings API URL (default: $DRAWTHINGS_URL or http://127.0.0.1:7860)")
    parser.add_argument("--preset", choices=PRESETS.keys(), help="Use preset configuration")
    parser.add_argument("--json", action="store_true", help="Output raw JSON response")
    
    args = parser.parse_args()
    
    # Apply preset if specified
    if args.preset:
        preset = PRESETS[args.preset]
        for key, value in preset.items():
            # Only override if not explicitly set
            if key == "steps" and args.steps == 20:  # default
                args.steps = value
            elif key == "sampler_name" and args.sampler_name == "DPM++ 2M Karras":  # default
                args.sampler_name = value
            elif key == "cfg_scale" and args.cfg_scale == 7.0:  # default
                args.cfg_scale = value
            elif key == "width" and args.width == 512:  # default
                args.width = value
            elif key == "height" and args.height == 512:  # default
                args.height = value
    
    # Generate
    print(f"Generating {args.batch_size} image(s) with prompt: {args.prompt[:60]}...")
    print(f"Settings: {args.steps} steps, {args.sampler_name}, CFG {args.cfg_scale}, {args.width}x{args.height}")
    
    result = generate_image(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        steps=args.steps,
        sampler_name=args.sampler_name,
        cfg_scale=args.cfg_scale,
        width=args.width,
        height=args.height,
        batch_size=args.batch_size,
        seed=args.seed,
        api_url=args.api_url,
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        save_images(result, args.output, args.prompt)
    
    print("Done!")


if __name__ == "__main__":
    main()
