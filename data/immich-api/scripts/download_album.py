"""
Immich API Client - Download Album
Usage: python download_album.py --url URL --api-key KEY --album-id ID --output ./downloads
"""
import argparse
import os
import requests
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_file(url: str, api_key: str, output_path: Path, session: requests.Session):
    """Download a single file."""
    headers = {"x-api-key": api_key}
    try:
        resp = session.get(url, headers=headers, stream=True)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

def download_album(url: str, api_key: str, album_id: str, output_dir: str, original: bool = False):
    """Download all assets from an album."""
    headers = {"x-api-key": api_key}
    base_url = url.rstrip("/")
    session = requests.Session()
    
    # Get album info
    resp = session.get(f"{base_url}/api/albums/{album_id}", headers=headers)
    if resp.status_code != 200:
        print(f"Album not found: {album_id}")
        return
        
    album = resp.json()
    album_name = album.get("albumName", "unknown")
    assets = album.get("assets", [])
    
    print(f"Album: {album_name}")
    print(f"Assets: {len(assets)}")
    
    # Create output directory
    output_path = Path(output_dir) / album_name
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Determine endpoint
    endpoint = "original" if original else "thumbnail"
    
    # Download assets
    downloaded = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        
        for asset in assets:
            asset_id = asset.get("id")
            if not asset_id:
                continue
                
            # Get original filename or use asset ID
            filename = asset.get("originalFileName", f"{asset_id}.jpg")
            file_path = output_path / filename
            
            if file_path.exists():
                print(f"✓ {filename} (already exists)")
                continue
                
            # Build download URL
            if original:
                download_url = f"{base_url}/api/assets/{asset_id}/original"
            else:
                download_url = f"{base_url}/api/assets/{asset_id}/thumbnail?format=jpeg"
            
            future = executor.submit(download_file, download_url, api_key, file_path, session)
            futures[future] = filename
            
        for future in as_completed(futures):
            filename = futures[future]
            if future.result():
                downloaded += 1
                print(f"✓ {filename}")
            else:
                print(f"✗ {filename}")
    
    print(f"\nDownloaded {downloaded}/{len(assets)} files to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download album from Immich")
    parser.add_argument("--url", required=True, help="Immich URL")
    parser.add_argument("--api-key", required=True, help="API Key")
    parser.add_argument("--album-id", required=True, help="Album ID")
    parser.add_argument("--output", default="./downloads", help="Output directory")
    parser.add_argument("--original", action="store_true", help="Download original files (larger)")
    args = parser.parse_args()
    
    download_album(args.url, args.api_key, args.album_id, args.output, args.original)
