#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using SiliconFlow FLUX or Qwen models.

Usage:
    uv run image_gen.py --prompt "description" --filename "output.png" [--model flux|qwen]
    
Examples:
    uv run image_gen.py --prompt "a cute robot" --filename "robot.png"
    uv run image_gen.py --prompt "山水画" --filename "landscape.png" --model qwen
"""

import argparse
import os
import sys
import random
import time
from pathlib import Path
from io import BytesIO

import requests
from PIL import Image as PILImage


SILICONFLOW_URL = "https://api.siliconflow.cn/v1/images/generations"

MODELS = {
    "flux": "black-forest-labs/FLUX.1-schnell",
    "flux-dev": "black-forest-labs/FLUX.1-dev", 
    "flux-pro": "black-forest-labs/FLUX.1-pro",
    "qwen": "Qwen/Qwen-Image",
    "qwen-edit": "Qwen/Qwen-Image-Edit",
    "qwen-edit-2509": "Qwen/Qwen-Image-Edit-2509",
}


def get_api_key() -> str:
    key = os.environ.get("SILICONFLOW_API_KEY")
    if not key:
        print("Error: SILICONFLOW_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def generate_image(prompt: str, output_path: Path, model: str, api_key: str, size: str = "1024x1024") -> bool:
    model_id = MODELS.get(model, MODELS["flux"])
    
    payload = {
        "model": model_id,
        "prompt": prompt,
        "image_size": size,
        "num_inference_steps": 20,
        "seed": random.randint(1, 999999999)
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🎨 Generating image with {model_id}...")
    start_time = time.time()
    
    try:
        response = requests.post(SILICONFLOW_URL, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        
        if "images" in data and len(data["images"]) > 0:
            image_url = data["images"][0]["url"]
            
            print(f"📥 Downloading image...")
            img_response = requests.get(image_url, timeout=60)
            img_response.raise_for_status()
            
            image = PILImage.open(BytesIO(img_response.content))
            if image.mode == 'RGBA':
                rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])
                rgb_image.save(str(output_path), 'PNG')
            else:
                image.save(str(output_path), 'PNG')
            
            elapsed = time.time() - start_time
            print(f"✅ Image saved: {output_path.resolve()}")
            print(f"⏱️  Generation time: {elapsed:.1f}s")
            print(f"MEDIA: {output_path.resolve()}")
            return True
        else:
            print(f"❌ Unexpected response: {data}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate images with SiliconFlow")
    parser.add_argument("--prompt", "-p", required=True, help="Image description")
    parser.add_argument("--filename", "-f", required=True, help="Output filename")
    parser.add_argument("--model", "-m", choices=list(MODELS.keys()), default="flux",
                        help="Model to use (default: flux)")
    parser.add_argument("--size", "-s", default="1024x1024", help="Image size (default: 1024x1024)")
    
    args = parser.parse_args()
    
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    api_key = get_api_key()
    
    if not generate_image(args.prompt, output_path, args.model, api_key, args.size):
        sys.exit(1)


if __name__ == "__main__":
    main()
