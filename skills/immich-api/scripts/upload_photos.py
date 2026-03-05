"""
Immich API Client - Upload Photos
Usage: python upload_photos.py --url URL --api-key KEY --album "Album Name" --folder /path/to/photos
"""
import argparse
import os
import requests
import sys
from pathlib import Path

def upload_photos(url: str, api_key: str, folder: str, album_id: str = None):
    """Upload all photos from a folder to Immich."""
    headers = {"x-api-key": api_key}
    base_url = url.rstrip("/")
    
    # Get or create album
    if album_id:
        album = {"albumId": album_id}
    else:
        # List albums or create new one
        album_name = Path(folder).name
        resp = requests.get(f"{base_url}/api/albums", headers=headers)
        albums = resp.json()
        album = next((a for a in albums if a.get("albumName") == album_name), None)
        
        if not album:
            resp = requests.post(f"{base_url}/api/albums", 
                                headers=headers,
                                json={"albumName": album_name})
            album = resp.json()
            print(f"Created album: {album['id']}")
        else:
            album = album[0] if album else None
            
    album_id = album.get("id") if album else None
    
    # Upload files
    folder_path = Path(folder)
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".mp4", ".mov"}
    
    files = list(folder_path.glob("*.*"))
    files = [f for f in files if f.suffix.lower() in image_extensions]
    
    print(f"Found {len(files)} media files to upload")
    
    uploaded = 0
    for file_path in files:
        try:
            with open(file_path, "rb") as f:
                files_data = {"file": (file_path.name, f)}
                data = {}
                if album_id:
                    data["albumId"] = album_id
                    
                resp = requests.post(f"{base_url}/api/assets", 
                                   headers=headers,
                                   files=files_data,
                                   data=data)
                
                if resp.status_code in (200, 201):
                    uploaded += 1
                    print(f"✓ {file_path.name}")
                else:
                    print(f"✗ {file_path.name}: {resp.status_code}")
        except Exception as e:
            print(f"✗ {file_path.name}: {e}")
            
    print(f"\nUploaded {uploaded}/{len(files)} files")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload photos to Immich")
    parser.add_argument("--url", required=True, help="Immich URL")
    parser.add_argument("--api-key", required=True, help="API Key")
    parser.add_argument("--folder", required=True, help="Folder with photos")
    parser.add_argument("--album-id", help="Album ID (optional)")
    args = parser.parse_args()
    
    upload_photos(args.url, args.api_key, args.folder, args.album_id)
