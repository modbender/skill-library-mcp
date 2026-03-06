#!/usr/bin/env python3
"""Fast image analysis using NVIDIA Kimi K2.5."""

import sys
import os
import base64
import json
import requests

INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "moonshotai/kimi-k2.5"

def get_api_key(key_or_path=None):
    if not key_or_path:
        path = os.path.expanduser("~/.config/nvidia-kimi-api-key")
        if os.path.exists(path):
            with open(path) as f:
                return f.read().strip()
        return None
    if os.path.exists(key_or_path):
        with open(key_or_path) as f:
            return f.read().strip()
    return key_or_path

def setup_instructions():
    print("=" * 50)
    print("NVIDIA KIMI VISION - SETUP REQUIRED")
    print("=" * 50)
    print("\n1. Go to https://build.nvidia.com")
    print("2. Sign up / Log in")
    print("3. Search for 'Kimi K2.5'")
    print("4. Get your free API key")
    print("\nTo save your key permanently:")
    print("  echo 'your-api-key-here' > ~/.config/nvidia-kimi-api-key")
    print("\nOr pass it directly as the 3rd argument:")
    print("  python3 scripts/analyze_image.py <image> <prompt> <api_key>")
    print("=" * 50)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/analyze_image.py <image_path> <prompt> [api_key]")
        print("\nExample:")
        print("  python3 scripts/analyze_image.py photo.jpg 'What is this?'")
        print("  python3 scripts/analyze_image.py photo.jpg 'What is this?' sk-your-key")
        sys.exit(1)
    
    image_path = sys.argv[1]
    prompt = sys.argv[2]
    api_key = get_api_key() if len(sys.argv) < 4 else sys.argv[3]
    
    if not api_key:
        print("Error: No API key found\n")
        setup_instructions()
        sys.exit(1)
    
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        sys.exit(1)
    
    # Read and encode
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    
    ext = os.path.splitext(image_path)[1].lower()
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
        ]}],
        "max_tokens": 2048
    }
    
    print("Sending to Kimi...", flush=True)
    
    try:
        r = requests.post(
            INVOKE_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=300  # 5 min max
        )
    except requests.exceptions.Timeout:
        print("Timeout - API took too long")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    if r.status_code != 200:
        print(f"API error {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    
    result = r.json()
    msg = result.get("choices", [{}])[0].get("message", {})
    
    reasoning = msg.get("reasoning", "")
    content = msg.get("content", "")
    
    if reasoning:
        print(f"[Thinking] {reasoning[:200]}...", flush=True)
    print(content, flush=True)

if __name__ == "__main__":
    main()
