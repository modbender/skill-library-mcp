#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SiliconFlow Video Generation Script
Supports both Text-to-Video and Image-to-Video
Compatible with OpenClaw Agent Skills
"""

import os
import sys
import json
import argparse
import subprocess
import time

# API Configuration
API_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "Wan-AI/Wan2.2-T2V-A14B"

def get_api_key():
    """Get API key from environment or OpenClaw config"""
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if api_key:
        return api_key
    
    try:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        providers = config.get("models", {}).get("providers", {})
        siliconflow = providers.get("siliconflow", {})
        api_key = siliconflow.get("apiKey")
        if api_key and api_key != "ollama":
            return api_key
    except Exception:
        pass
    
    return None

def submit_video_job(prompt, image_url=None, model=None):
    """Submit video generation job"""
    api_key = get_api_key()
    if not api_key:
        return {"success": False, "error": "SILICONFLOW_API_KEY not found"}
    
    model = model or DEFAULT_MODEL
    
    data = {
        "model": model,
        "prompt": prompt
    }
    
    # Add image_url for image-to-video
    if image_url:
        data["image_url"] = image_url
    
    curl_cmd = [
        "curl", "-s", "-X", "POST",
        f"{API_BASE_URL}/video/submit",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data),
        "--max-time", "30"
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {"success": False, "error": f"API request failed: {result.stderr}"}
        
        response = json.loads(result.stdout)
        
        # Check for API error
        if "code" in response and response["code"] != 200:
            return {"success": False, "error": response.get("message", "Unknown error")}
        
        return {"success": True, "request_id": response.get("requestId")}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_video(prompt, image_url=None, model=None, output_path=None):
    """Generate video (text-to-video or image-to-video)"""
    mode = "Image-to-Video" if image_url else "Text-to-Video"
    print(json.dumps({
        "message": f"Submitting {mode} job...",
        "prompt": prompt,
        "image_url": image_url
    }, ensure_ascii=False))
    
    # Submit job
    submit_result = submit_video_job(prompt, image_url, model)
    if not submit_result.get("success"):
        print(json.dumps(submit_result))
        sys.exit(1)
    
    request_id = submit_result.get("request_id")
    print(json.dumps({
        "success": True,
        "message": "Job submitted successfully",
        "mode": mode,
        "request_id": request_id,
        "model": model or DEFAULT_MODEL,
        "prompt": prompt,
        "image_url": image_url,
        "note": "Video generation is async. Use request_id to check status."
    }, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(
        description="Generate videos using SiliconFlow API (Wan2.2)",
        epilog="Examples:\n"
               "  %(prog)s \"A woman walking in garden\"\n"
               "  %(prog)s \"Camera zooming in\" --image-url https://example.com/image.jpg\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("prompt", help="Video generation prompt")
    parser.add_argument("--image-url", "-i", help="Image URL for image-to-video mode")
    parser.add_argument("--model", "-m", help="Model to use", default=DEFAULT_MODEL)
    parser.add_argument("--output", "-o", help="Output file path (optional)")
    
    args = parser.parse_args()
    generate_video(args.prompt, args.image_url, args.model, args.output)

if __name__ == "__main__":
    main()
