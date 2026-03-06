#!/usr/bin/env python3
"""
Seedream 4.5 Image Generation Script
Supports text-to-image and image-to-image generation via Volcengine Ark API.
"""

import os
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

API_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
DEFAULT_MODEL = "doubao-seedream-4-5-251128"

# Recommended sizes for different aspect ratios
RECOMMENDED_SIZES = {
    "1:1": "2048x2048",
    "4:3": "2304x1728",
    "3:4": "1728x2304",
    "16:9": "2560x1440",
    "9:16": "1440x2560",
    "3:2": "2496x1664",
    "2:3": "1664x2496",
    "21:9": "3024x1296",
}


def get_api_key():
    """Get API key from environment variable."""
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        print("Error: ARK_API_KEY environment variable not set.", file=sys.stderr)
        print("Please set it with: export ARK_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(1)
    return api_key


def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 format."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    suffix = path.suffix.lower().lstrip(".")
    mime_map = {
        "jpg": "jpeg", "jpeg": "jpeg", "png": "png",
        "webp": "webp", "bmp": "bmp", "tiff": "tiff", "gif": "gif"
    }
    mime_type = mime_map.get(suffix, "jpeg")
    
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    
    return f"data:image/{mime_type};base64,{encoded}"


def generate_image(
    prompt: str,
    images: list = None,
    size: str = "2K",
    model: str = DEFAULT_MODEL,
    watermark: bool = False,
    sequential: str = "disabled",
    max_images: int = 1,
    response_format: str = "url",
    optimize_prompt: str = None,
    output_dir: str = None,
) -> dict:
    """
    Generate images using Seedream API.
    
    Args:
        prompt: Text prompt for image generation
        images: List of reference image paths or URLs
        size: Output size - "2K", "4K", or specific like "2048x2048"
        model: Model ID to use
        watermark: Add AI watermark
        sequential: "auto" for multi-image, "disabled" for single
        max_images: Max images when sequential="auto"
        response_format: "url" or "b64_json"
        optimize_prompt: "standard" or "fast" for prompt optimization
        output_dir: Directory to save downloaded images
    
    Returns:
        API response dict with generated image info
    """
    api_key = get_api_key()
    
    # Build request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "watermark": watermark,
        "response_format": response_format,
        "sequential_image_generation": sequential,
    }
    
    # Add reference images if provided
    if images:
        encoded_images = []
        for img in images:
            if img.startswith(("http://", "https://")):
                encoded_images.append(img)
            else:
                encoded_images.append(encode_image_to_base64(img))
        
        if len(encoded_images) == 1:
            payload["image"] = encoded_images[0]
        else:
            payload["image"] = encoded_images
    
    # Configure multi-image generation
    if sequential == "auto":
        payload["sequential_image_generation_options"] = {
            "max_images": max_images
        }
    
    # Configure prompt optimization
    if optimize_prompt:
        payload["optimize_prompt_options"] = {
            "mode": optimize_prompt
        }
    
    # Make API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    request_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_ENDPOINT, data=request_data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"API Error ({e.code}): {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    
    # Download images if output_dir specified and format is URL
    if output_dir and response_format == "url" and "data" in result:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []
        
        for i, item in enumerate(result["data"]):
            if "url" in item:
                filename = f"seedream_{timestamp}_{i+1}.jpg"
                filepath = output_path / filename
                try:
                    urllib.request.urlretrieve(item["url"], filepath)
                    saved_files.append(str(filepath))
                    print(f"Saved: {filepath}")
                except Exception as e:
                    print(f"Failed to download image {i+1}: {e}", file=sys.stderr)
            elif "error" in item:
                print(f"Image {i+1} failed: {item['error']}", file=sys.stderr)
        
        result["saved_files"] = saved_files
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Seedream 4.5 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Text to image
  python generate_image.py -p "A cat sitting on a windowsill" -o ./output
  
  # Image editing with reference
  python generate_image.py -p "Change the cat to a dog" -i input.jpg -o ./output
  
  # Multi-image fusion
  python generate_image.py -p "Combine style of image 1 with subject of image 2" -i style.jpg subject.jpg
  
  # Generate image sequence
  python generate_image.py -p "Four seasons of a garden" --sequential auto --max-images 4
        """
    )
    
    parser.add_argument("-p", "--prompt", required=True, help="Text prompt for generation")
    parser.add_argument("-i", "--images", nargs="+", help="Reference image paths or URLs (max 14)")
    parser.add_argument("-s", "--size", default="2K", help="Output size: 2K, 4K, or WxH (e.g., 2048x2048)")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help="Model ID")
    parser.add_argument("-o", "--output", help="Output directory for saving images")
    parser.add_argument("-w", "--watermark", action="store_true", help="Add AI watermark")
    parser.add_argument("--sequential", choices=["auto", "disabled"], default="disabled",
                        help="Enable multi-image generation")
    parser.add_argument("--max-images", type=int, default=4, help="Max images for sequential mode")
    parser.add_argument("--format", choices=["url", "b64_json"], default="url",
                        help="Response format")
    parser.add_argument("--optimize", choices=["standard", "fast"],
                        help="Enable prompt optimization")
    parser.add_argument("--json", action="store_true", help="Output full JSON response")
    
    args = parser.parse_args()
    
    result = generate_image(
        prompt=args.prompt,
        images=args.images,
        size=args.size,
        model=args.model,
        watermark=args.watermark,
        sequential=args.sequential,
        max_images=args.max_images,
        response_format=args.format,
        optimize_prompt=args.optimize,
        output_dir=args.output,
    )
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Pretty print results
        if "data" in result:
            print(f"\n✅ Generated {len(result['data'])} image(s):\n")
            for i, item in enumerate(result["data"], 1):
                if "url" in item:
                    print(f"  [{i}] URL: {item['url']}")
                    if "size" in item:
                        print(f"      Size: {item['size']}")
                elif "error" in item:
                    print(f"  [{i}] Error: {item['error']}")
        
        if "usage" in result:
            usage = result["usage"]
            print(f"\n📊 Usage: {usage.get('generated_images', 0)} images, {usage.get('output_tokens', 0)} tokens")
        
        if "saved_files" in result:
            print(f"\n💾 Saved to: {', '.join(result['saved_files'])}")


if __name__ == "__main__":
    main()
