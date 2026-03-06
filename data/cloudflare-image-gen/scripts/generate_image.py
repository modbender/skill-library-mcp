#!/usr/bin/env python3
"""
Cloudflare Workers AI Image Generation Script
Generates images using @cf/black-forest-labs/flux-1-schnell model
"""

import json
import base64
import argparse
import os
import subprocess

ACCOUNT_ID = "1e89d3ce76cbfef3b5c340e3984b7a52"
TOKEN = "aCTA2KaKa1n3ayFDL-LPmZ-JgUC0HHgA5Msy18Bk"
MODEL = "@cf/black-forest-labs/flux-1-schnell"

def generate_image(prompt, output_path=None):
    """Generate an image using Cloudflare Workers AI"""
    
    if output_path is None:
        output_path = f"/home/ubuntu/.openclaw/workspace/{prompt.replace(' ', '_')[:30]}.png"
    
    # Call Cloudflare API
    cmd = f'''curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{MODEL}" \
      -H "Authorization: Bearer {TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{json.dumps({"prompt": prompt})}' > /tmp/cf_response.json'''
    
    subprocess.run(cmd, shell=True)
    
    with open('/tmp/cf_response.json', 'r') as f:
        data = json.load(f)
    
    if 'result' in data and 'image' in data.get('result', {}):
        img_data = data['result']['image']
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(img_data))
        return output_path
    else:
        raise Exception(f"API Error: {data.get('errors', 'Unknown error')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate images with Cloudflare Workers AI')
    parser.add_argument('prompt', help='Image description/prompt')
    parser.add_argument('-o', '--output', help='Output file path', default=None)
    
    args = parser.parse_args()
    
    try:
        output = generate_image(args.prompt, args.output)
        print(f"Image saved to: {output}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
