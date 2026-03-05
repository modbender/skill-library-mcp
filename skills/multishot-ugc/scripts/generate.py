#!/usr/bin/env python3
"""
MULTISHOT-UGC: Generate 10 perspective variations of an image for UGC video production.

Usage:
    uv run generate.py --image <path_or_url> --output-dir <dir> [--text <prompt>] [--resolution 2K] [--aspect-ratio 9:16]
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

# ComfyDeploy API configuration
COMFY_DEPLOY_API_URL = "https://api.comfydeploy.com/api"
DEPLOYMENT_ID = "9ccbb29a-d982-48cc-a465-bae916f2c7fd"

DEFAULT_TEXT = "Explora distintas perspectivas de esta escena"


def get_api_key():
    """Get API key from environment or raise error."""
    api_key = os.environ.get("COMFY_DEPLOY_API_KEY")
    if not api_key:
        raise ValueError(
            "COMFY_DEPLOY_API_KEY environment variable is required. "
            "Set it with: export COMFY_DEPLOY_API_KEY='your-key'"
        )
    return api_key


def upload_image(file_path: str, api_key: str) -> str:
    """Upload a local image file to ComfyDeploy and return the URL."""
    print(f"Uploading image: {file_path}")
    
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.post(
            f"{COMFY_DEPLOY_API_URL}/file/upload",
            headers=headers,
            files=files
        )
        response.raise_for_status()
        
    result = response.json()
    url = result.get("file_url")
    print(f"Uploaded: {url}")
    return url


def is_url(string: str) -> bool:
    """Check if string is a valid URL."""
    try:
        result = urlparse(string)
        return all([result.scheme in ("http", "https"), result.netloc])
    except:
        return False


def queue_multishot(
    image_url: str,
    text: str,
    resolution: str,
    aspect_ratio: str,
    api_key: str
) -> str:
    """Queue the MULTISHOT-UGC workflow and return run_id."""
    print(f"\nQueuing MULTISHOT-UGC generation...")
    print(f"  Resolution: {resolution}")
    print(f"  Aspect Ratio: {aspect_ratio}")
    print(f"  Text: {text[:50]}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "deployment_id": DEPLOYMENT_ID,
        "inputs": {
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "input_image": image_url,
            "text": text
        }
    }
    
    response = requests.post(
        f"{COMFY_DEPLOY_API_URL}/run/deployment/queue",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    
    result = response.json()
    run_id = result.get("run_id")
    print(f"Queued run: {run_id}")
    return run_id


def wait_for_completion(run_id: str, api_key: str, timeout: int = 600) -> dict:
    """Poll for run completion and return the result."""
    print("Waiting for completion...")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    start_time = time.time()
    
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Run did not complete within {timeout} seconds")
        
        response = requests.get(
            f"{COMFY_DEPLOY_API_URL}/run/{run_id}",
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        status = result.get("status")
        
        print(f"Status: {status}... waiting")
        
        if status == "success":
            print("Run completed successfully!")
            return result
        elif status in ("failed", "cancelled"):
            raise RuntimeError(f"Run {status}: {result}")
        
        time.sleep(5)


def download_images(result: dict, output_dir: str) -> list:
    """Download all output images and return list of paths."""
    os.makedirs(output_dir, exist_ok=True)
    
    outputs = result.get("outputs", [])
    downloaded = []
    
    for output in outputs:
        images = output.get("data", {}).get("images", [])
        for img in images:
            url = img.get("url")
            filename = img.get("filename")
            
            if url and filename:
                output_path = os.path.join(output_dir, filename)
                print(f"Downloading: {filename}")
                
                response = requests.get(url)
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                downloaded.append(output_path)
    
    return downloaded


def main():
    parser = argparse.ArgumentParser(
        description="Generate 10 perspective variations of an image for UGC videos"
    )
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Path or URL to the source image"
    )
    parser.add_argument(
        "--output-dir", "-o",
        required=True,
        help="Directory to save output images"
    )
    parser.add_argument(
        "--text", "-t",
        default=DEFAULT_TEXT,
        help=f"Exploration prompt (default: '{DEFAULT_TEXT}')"
    )
    parser.add_argument(
        "--resolution", "-r",
        default="2K",
        choices=["1K", "2K", "4K"],
        help="Output resolution (default: 2K)"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        default="9:16",
        choices=["9:16", "16:9", "1:1", "4:3", "3:4"],
        help="Output aspect ratio (default: 9:16)"
    )
    
    args = parser.parse_args()
    
    try:
        api_key = get_api_key()
        
        # Handle image input (URL or local file)
        if is_url(args.image):
            image_url = args.image
        else:
            if not os.path.exists(args.image):
                raise FileNotFoundError(f"Image not found: {args.image}")
            image_url = upload_image(args.image, api_key)
        
        # Queue the workflow
        run_id = queue_multishot(
            image_url=image_url,
            text=args.text,
            resolution=args.resolution,
            aspect_ratio=args.aspect_ratio,
            api_key=api_key
        )
        
        # Wait for completion
        result = wait_for_completion(run_id, api_key)
        
        # Download images
        downloaded = download_images(result, args.output_dir)
        
        print(f"\n✅ Generated {len(downloaded)} variations in: {args.output_dir}")
        for path in sorted(downloaded):
            print(f"  - {os.path.basename(path)}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
