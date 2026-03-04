#!/usr/bin/env python3
"""
DALL-E 3 Generator - Generate frames for Muffin video project
Usage: python3 dalle_generator.py --prompt "your prompt" [--filename output.png]
"""

import os
import sys
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

# API setup
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment")

# Output folder
ASSETS_DIR = Path(__file__).parent / "assets" / "frames"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def generate_frame(prompt, filename=None):
    """Generate a single frame using DALL-E 3"""
    try:
        url = "https://api.openai.com/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1920x1080",
            "quality": "hd"
        }
        
        print(f"🎨 Generating: {prompt[:60]}...")
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            image_url = data["data"][0]["url"]
            
            # Download image
            img_response = requests.get(image_url)
            img = Image.open(BytesIO(img_response.content))
            
            if filename is None:
                import time
                timestamp = int(time.time())
                filename = f"dalle_frame_{timestamp}.png"
            
            filepath = ASSETS_DIR / filename
            img.save(filepath)
            print(f"✓ Saved: {filepath}")
            return filepath
        else:
            print(f"✗ API error: {response.status_code}")
            print(f"  {response.json()}")
            return None
            
    except Exception as e:
        print(f"✗ Generation error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 dalle_generator.py '<prompt>' [output.png]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    filename = sys.argv[2] if len(sys.argv) > 2 else None
    generate_frame(prompt, filename)
