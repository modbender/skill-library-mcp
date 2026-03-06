#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SiliconFlow Image Generation Script
Compatible with OpenClaw Agent Skills
"""

import os
import sys
import json
import argparse
import subprocess

# API Configuration
API_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "black-forest-labs/FLUX.1-schnell"
DEFAULT_SIZE = "1024x1024"

def get_api_key():
    """Get API key from environment or OpenClaw config"""
    # Try environment first
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if api_key:
        return api_key
    
    # Try OpenClaw config
    try:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        providers = config.get("models", {}).get("providers", {})
        siliconflow = providers.get("siliconflow", {})
        api_key = siliconflow.get("apiKey")
        if api_key and api_key != "ollama":  # Skip placeholder
            return api_key
    except Exception:
        pass
    
    return None

def generate_image(prompt, model=None, size=None, output_path=None):
    """Generate image using SiliconFlow API via curl"""
    api_key = get_api_key()
    if not api_key:
        print(json.dumps({
            "success": False,
            "error": "SILICONFLOW_API_KEY not found. Please set SILICONFLOW_API_KEY environment variable."
        }))
        sys.exit(1)
    
    model = model or DEFAULT_MODEL
    size = size or DEFAULT_SIZE
    
    # Prepare request data
    data = {
        "model": model,
        "prompt": prompt,
        "size": size
    }
    
    # Use curl to avoid Python encoding issues
    curl_cmd = [
        "curl", "-s", "-X", "POST",
        f"{API_BASE_URL}/images/generations",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data),
        "--max-time", "120"
    ]
    
    try:
        # Make API request
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(json.dumps({
                "success": False,
                "error": f"API request failed: {result.stderr}"
            }))
            sys.exit(1)
        
        response = json.loads(result.stdout)
        
        # Extract image URL
        image_url = response.get("data", [{}])[0].get("url")
        if not image_url:
            print(json.dumps({
                "success": False,
                "error": "No image URL in response",
                "response": response
            }))
            sys.exit(1)
        
        # Download image if output path specified
        if output_path:
            download_cmd = ["curl", "-s", "-L", "--max-time", "60", "-o", output_path, image_url]
            download_result = subprocess.run(download_cmd, capture_output=True)
            if download_result.returncode != 0:
                print(json.dumps({
                    "success": False,
                    "error": "Failed to download image"
                }))
                sys.exit(1)
        
        # Output result as JSON
        output = {
            "success": True,
            "prompt": prompt,
            "model": model,
            "image_url": image_url,
            "local_path": output_path if output_path else None
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate images using SiliconFlow API")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("--model", "-m", help="Model to use", default=DEFAULT_MODEL)
    parser.add_argument("--size", "-s", help="Image size (e.g., 1024x1024)", default=DEFAULT_SIZE)
    parser.add_argument("--output", "-o", help="Output file path")
    
    args = parser.parse_args()
    generate_image(args.prompt, args.model, args.size, args.output)

if __name__ == "__main__":
    main()
