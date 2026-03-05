#!/usr/bin/env python3
"""ImgBB API Client - Production Ready"""

import argparse
import requests
import json
import os
import sys
from pathlib import Path

API_URL = "https://api.imgbb.com/1/upload"
CONFIG_FILE = os.path.expanduser("~/.imgbb_api_key")

def get_api_key(key_param=None):
    """Get API key from parameter, env, or config file"""
    if key_param:
        return key_param
    
    # Check environment variable
    api_key = os.environ.get("IMGBB_API_KEY")
    if api_key:
        return api_key
    
    # Check config file
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            api_key = f.read().strip()
            if api_key:
                return api_key
    
    return None

def upload_file(image_path, api_key, name=None, expiration=0):
    if not os.path.exists(image_path):
        return {"error": f"File not found: {image_path}"}
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'key': api_key}
        if name: data['name'] = name
        if expiration > 0: data['expiration'] = expiration
        response = requests.post(API_URL, files=files, data=data, timeout=30)
    return response.json()

def upload_url(image_url, api_key, name=None, expiration=0):
    data = {'key': api_key, 'image': image_url}
    if name: data['name'] = name
    if expiration > 0: data['expiration'] = expiration
    response = requests.post(API_URL, data=data, timeout=30)
    return response.json()

def upload_base64(base64_string, api_key, name=None, expiration=0):
    data = {'key': api_key, 'image': base64_string}
    if name: data['name'] = name
    if expiration > 0: data['expiration'] = expiration
    response = requests.post(API_URL, data=data, timeout=30)
    return response.json()

def upload_batch(folder_path, api_key, extension='.jpg'):
    folder = Path(folder_path)
    results = []
    for f in sorted(folder.glob(f"*{extension}")):
        print(f"Uploading {f.name}...")
        result = upload_file(str(f), api_key)
        if result.get('success'):
            results.append({'file': f.name, 'url': result['data']['url'], 'viewer': result['data']['url_viewer']})
        else:
            results.append({'file': f.name, 'error': result.get('error', 'Upload failed')})
    return results

def main():
    parser = argparse.ArgumentParser(description='ImgBB API Client')
    parser.add_argument('image', nargs='?', help='Path to image file')
    parser.add_argument('--key', help='ImgBB API key (or use IMGBB_API_KEY env or ~/.imgbb_api_key)')
    parser.add_argument('--url', help='Upload from URL')
    parser.add_argument('--base64', help='Upload from Base64 string')
    parser.add_argument('--name', help='Custom name')
    parser.add_argument('--expiration', type=int, default=0, help='Expiration in seconds')
    parser.add_argument('--json', action='store_true', help='JSON output')
    parser.add_argument('--batch', metavar='FOLDER', help='Batch upload folder')
    parser.add_argument('--ext', default='.jpg', help='File extension for batch')
    parser.add_argument('--set-key', metavar='KEY', help='Save API key to config file')
    args = parser.parse_args()
    
    # Save API key if requested
    if args.set_key:
        with open(CONFIG_FILE, 'w') as f:
            f.write(args.set_key)
        print(f"✅ API key saved to {CONFIG_FILE}")
        return
    
    # Get API key
    api_key = get_api_key(args.key)
    if not api_key:
        print("❌ No API key found. Use:")
        print("   --key YOUR_API_KEY")
        print("   export IMGBB_API_KEY=YOUR_API_KEY")
        print(f"   echo YOUR_API_KEY > {CONFIG_FILE}")
        sys.exit(1)
    
    # Batch mode
    if args.batch:
        results = upload_batch(args.batch, api_key, args.ext)
        print(f"\n📁 Batch: {len(results)} files")
        for r in results:
            print(f"  {'✅' if 'url' in r else '❌'} {r.get('file', r)}")
        return
    
    # Single upload
    if args.url:
        result = upload_url(args.url, api_key, args.name, args.expiration)
    elif args.base64:
        result = upload_base64(args.base64, api_key, args.name, args.expiration)
    elif args.image:
        result = upload_file(args.image, api_key, args.name, args.expiration)
    else:
        parser.print_help()
        return
    
    if result.get('success'):
        data = result['data']
        if args.json:
            print(json.dumps({
                'url': data.get('url'),
                'viewer': data.get('url_viewer'),
                'thumb': data.get('thumb', {}).get('url')
            }))
        else:
            print(f"✅ {data.get('title')}")
            print(f"   URL: {data.get('url')}")
    else:
        print(f"❌ Error: {result.get('error', 'Upload failed')}")

if __name__ == '__main__':
    main()
