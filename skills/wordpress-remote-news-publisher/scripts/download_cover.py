#!/usr/bin/env python3
"""
Download cover image from Unsplash API.

Usage: download_cover.py [keyword] [output_path]
"""
import sys
import os
import requests
from datetime import datetime

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} [keyword] [output_path]", file=sys.stderr)
        sys.exit(1)
    
    query = sys.argv[1]
    output_path = sys.argv[2]
    
    api_key = os.environ.get('UNSPLASH_ACCESS_KEY')
    if not api_key:
        print("ERROR: UNSPLASH_ACCESS_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    # Request random photo from Unsplash
    url = 'https://api.unsplash.com/photos/random'
    params = {
        'query': query,
        'orientation': 'landscape',
        'content_filter': 'high'
    }
    headers = {
        'Authorization': f'Client-ID {api_key}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch image from Unsplash: {e}", file=sys.stderr)
        sys.exit(1)
    
    if 'urls' not in data:
        print(f"ERROR: Unexpected API response format", file=sys.stderr)
        sys.exit(1)
    
    # Download the image
    try:
        image_url = data['urls']['regular']
        img_response = requests.get(image_url, timeout=60)
        img_response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(img_response.content)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to download image: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Save metadata for attribution
    photographer_name = data.get('user', {}).get('name', 'Unknown')
    photographer_username = data.get('user', {}).get('username', 'unknown')
    unsplash_url = data.get('links', {}).get('html', f'https://unsplash.com/@{photographer_username}')
    
    meta_path = '/tmp/cover_meta.txt'
    with open(meta_path, 'w') as f:
        f.write(f"Photo by {photographer_name} on Unsplash\n")
        f.write(f"URL: {unsplash_url}\n")
        f.write(f"Downloaded: {datetime.utcnow().isoformat()}Z\n")
    
    print(f"Image downloaded: {output_path}")
    print(f"Photographer: {photographer_name}")
    print(f"Metadata saved: {meta_path}")

if __name__ == '__main__':
    main()
