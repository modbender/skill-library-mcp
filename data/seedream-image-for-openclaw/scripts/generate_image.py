#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///

import argparse
import json
import os
import sys
import requests

def generate_image(prompt, model, size, api_key, image_input=None, sequential=False, max_images=1):
    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
    }
    
    if image_input:
        payload["image"] = image_input
        
    if sequential:
        payload["sequential_image_generation"] = "auto"
        payload["sequential_image_generation_options"] = {"max_images": max_images}
    else:
        payload["sequential_image_generation"] = "disabled"

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if "data" in result and len(result["data"]) > 0:
            for item in result["data"]:
                if "url" in item:
                    print(f"MEDIA_URL: {item['url']}")
                elif "b64_json" in item:
                    # In a real scenario, we might want to save this to a file, 
                    # but for this skill we follow the pattern of providing a URL if possible.
                    print("ERROR: Received base64 data but expected URL.")
        else:
            print(f"ERROR: No image data in response. Full response: {json.dumps(result)}")
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response body: {e.response.text}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate images using Volcengine Seedream API.")
    parser.add_argument("--prompt", required=True, help="Text prompt for image generation")
    parser.add_argument("--model", default="doubao-seedream-4-5-251128", help="Model ID or Endpoint ID")
    parser.add_argument("--size", default="2048x2048", help="Image size (e.g., 2K, 4K, 2048x2048)")
    parser.add_argument("--api-key", help="Volcengine API Key")
    parser.add_argument("--image", help="Input image URL or base64 (optional)")
    parser.add_argument("--sequential", action="store_true", help="Enable sequential image generation (group)")
    parser.add_argument("--max-images", type=int, default=1, help="Max images for sequential generation (1-15)")

    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("VOLC_API_KEY")
    if not api_key:
        print("ERROR: API key is required. Provide via --api-key or VOLC_API_KEY environment variable.")
        sys.exit(1)
        
    generate_image(
        prompt=args.prompt,
        model=args.model,
        size=args.size,
        api_key=api_key,
        image_input=args.image,
        sequential=args.sequential,
        max_images=args.max_images
    )

if __name__ == "__main__":
    main()
