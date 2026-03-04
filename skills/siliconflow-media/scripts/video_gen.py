#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
# ]
# ///
"""
Generate videos using SiliconFlow Wan models.

Usage:
    # Text to video
    uv run video_gen.py --prompt "description" --filename "output.mp4"
    
    # Image to video
    uv run video_gen.py --prompt "description" --image "input.png" --filename "output.mp4"
    
Examples:
    uv run video_gen.py --prompt "a cat walking in a garden" --filename "cat.mp4"
    uv run video_gen.py --prompt "make this image come alive" --image "photo.png" --filename "animated.mp4"
"""

import argparse
import os
import sys
import time
import base64
from pathlib import Path

import requests


SILICONFLOW_URL = "https://api.siliconflow.cn/v1/video/generations"

MODELS = {
    "t2v": "Wan-AI/Wan2.2-T2V-A14B",  # Text to video
    "i2v": "Wan-AI/Wan2.2-I2V-A14B",  # Image to video
}


def get_api_key() -> str:
    key = os.environ.get("SILICONFLOW_API_KEY")
    if not key:
        print("Error: SILICONFLOW_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_video(prompt: str, output_path: Path, api_key: str, image_path: str = None) -> bool:
    if image_path:
        model = MODELS["i2v"]
        print(f"🎬 Generating video from image using {model}...")
    else:
        model = MODELS["t2v"]
        print(f"🎬 Generating video from text using {model}...")
    
    payload = {
        "model": model,
        "prompt": prompt,
    }
    
    if image_path:
        payload["image"] = encode_image_to_base64(image_path)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    print("⏳ Submitting generation request...")
    
    try:
        response = requests.post(SILICONFLOW_URL, json=payload, headers=headers, timeout=300)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for direct video URL
        if "videos" in data and len(data["videos"]) > 0:
            video_url = data["videos"][0].get("url")
            if video_url:
                print(f"📥 Downloading video...")
                video_response = requests.get(video_url, timeout=300)
                video_response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(video_response.content)
                
                elapsed = time.time() - start_time
                print(f"✅ Video saved: {output_path.resolve()}")
                print(f"⏱️  Total time: {elapsed:.1f}s")
                print(f"MEDIA: {output_path.resolve()}")
                return True
        
        # Check for async task
        if "id" in data:
            task_id = data["id"]
            print(f"⏳ Task submitted, polling for result... (task_id: {task_id})")
            
            status_url = f"https://api.siliconflow.cn/v1/video/generations/{task_id}"
            max_wait = 600  # 10 minutes max
            
            while time.time() - start_time < max_wait:
                time.sleep(10)
                
                status_response = requests.get(status_url, headers=headers, timeout=30)
                status_response.raise_for_status()
                status_data = status_response.json()
                
                status = status_data.get("status", "unknown")
                elapsed = time.time() - start_time
                print(f"  [{elapsed:.0f}s] Status: {status}")
                
                if status == "succeeded" and "videos" in status_data:
                    video_url = status_data["videos"][0].get("url")
                    if video_url:
                        print(f"📥 Downloading video...")
                        video_response = requests.get(video_url, timeout=300)
                        video_response.raise_for_status()
                        
                        with open(output_path, "wb") as f:
                            f.write(video_response.content)
                        
                        elapsed = time.time() - start_time
                        print(f"✅ Video saved: {output_path.resolve()}")
                        print(f"⏱️  Total time: {elapsed:.1f}s")
                        print(f"MEDIA: {output_path.resolve()}")
                        return True
                
                elif status == "failed":
                    print(f"❌ Video generation failed: {status_data}", file=sys.stderr)
                    return False
            
            print("❌ Timeout waiting for video", file=sys.stderr)
            return False
        
        print(f"❌ Unexpected response: {data}", file=sys.stderr)
        return False
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate videos with SiliconFlow")
    parser.add_argument("--prompt", "-p", required=True, help="Video description")
    parser.add_argument("--filename", "-f", required=True, help="Output filename (e.g., video.mp4)")
    parser.add_argument("--image", "-i", help="Input image for image-to-video")
    
    args = parser.parse_args()
    
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    api_key = get_api_key()
    
    if not generate_video(args.prompt, output_path, api_key, args.image):
        sys.exit(1)


if __name__ == "__main__":
    main()
