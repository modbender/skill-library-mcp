#!/usr/bin/env python3
"""
Pixverse Video Generation Script
Usage: python generate_video.py --prompt "your prompt" --output video.mp4
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path

# Pixverse API endpoint (需要验证实际端点)
BASE_URL = "https://api.pixverse.ai/v1"

def get_api_key():
    """Get API key from environment"""
    api_key = os.environ.get("PIXVERSE_API_KEY")
    if not api_key:
        print("Error: PIXVERSE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return api_key

def generate_video(prompt, aspect_ratio="16:9", duration=4, style="realistic", image_url=None):
    """Generate video using Pixverse API"""
    api_key = get_api_key()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "duration": duration,
        "style": style
    }
    
    if image_url:
        payload["image_url"] = image_url
    
    print(f"Generating video with prompt: {prompt}", file=sys.stderr)
    
    # Submit generation task
    response = requests.post(
        f"{BASE_URL}/generate",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        print(f"Error: API returned {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)
    
    data = response.json()
    task_id = data.get("task_id") or data.get("id")
    
    if not task_id:
        print(f"Error: No task_id in response", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        sys.exit(1)
    
    print(f"Task created: {task_id}", file=sys.stderr)
    
    # Poll for completion
    max_attempts = 60  # 5 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        time.sleep(5)
        attempt += 1
        
        status_response = requests.get(
            f"{BASE_URL}/tasks/{task_id}",
            headers=headers
        )
        
        if status_response.status_code != 200:
            print(f"Warning: Status check failed", file=sys.stderr)
            continue
        
        status_data = status_response.json()
        status = status_data.get("status")
        
        print(f"Status: {status} (attempt {attempt}/{max_attempts})", file=sys.stderr)
        
        if status == "completed":
            video_url = status_data.get("video_url") or status_data.get("result", {}).get("url")
            if video_url:
                return video_url
            else:
                print("Error: Video completed but no URL found", file=sys.stderr)
                print(json.dumps(status_data, indent=2), file=sys.stderr)
                sys.exit(1)
        
        elif status == "failed":
            error = status_data.get("error", "Unknown error")
            print(f"Error: Video generation failed: {error}", file=sys.stderr)
            sys.exit(1)
    
    print("Error: Timeout waiting for video generation", file=sys.stderr)
    sys.exit(1)

def download_video(url, output_path):
    """Download video from URL"""
    print(f"Downloading video to {output_path}", file=sys.stderr)
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Video saved: {output_path}", file=sys.stderr)
    print(f"MEDIA: {os.path.abspath(output_path)}")

def main():
    parser = argparse.ArgumentParser(description="Generate videos with Pixverse")
    parser.add_argument("--prompt", required=True, help="Text prompt for video generation")
    parser.add_argument("--output", "-o", default="output.mp4", help="Output video file")
    parser.add_argument("--aspect-ratio", default="16:9", choices=["16:9", "9:16", "1:1"])
    parser.add_argument("--duration", type=int, default=4, help="Duration in seconds (2-8)")
    parser.add_argument("--style", default="realistic", 
                       choices=["realistic", "anime", "3d", "cinematic"])
    parser.add_argument("--image", help="Optional: Start from image URL")
    
    args = parser.parse_args()
    
    # Validate duration
    if not 2 <= args.duration <= 8:
        print("Error: Duration must be between 2 and 8 seconds", file=sys.stderr)
        sys.exit(1)
    
    # Generate video
    video_url = generate_video(
        prompt=args.prompt,
        aspect_ratio=args.aspect_ratio,
        duration=args.duration,
        style=args.style,
        image_url=args.image
    )
    
    # Download video
    download_video(video_url, args.output)

if __name__ == "__main__":
    main()
