#!/usr/bin/env python3
"""
123pan-upload: Upload files to 123pan direct link folder
Usage: python upload.py --file /path/to/file [--folder FOLDER_ID] [--link-type TYPE]
"""

import os
import sys
import json
import hashlib
import base64
import requests
import argparse
from pathlib import Path
from typing import List, Tuple

API_BASE = "https://open-api.123pan.com"

# Load config from config.json if exists
CONFIG = {}
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH) as f:
            CONFIG = json.load(f)
    except Exception:
        pass

def get_config(key, env_key=None, default=None):
    if key in CONFIG: return CONFIG[key]
    return os.environ.get(env_key, default) if env_key else default


def get_user_id_from_token() -> int:
    """Extract user ID from access token."""
    token = get_config("access_token", "PAN123_ACCESS_TOKEN", "")
    try:
        # JWT payload is the second part
        parts = token.split(".")
        if len(parts) >= 2:
            # Add padding if needed
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding
            data = json.loads(base64.b64decode(payload))
            return data.get("id", 0)
    except Exception:
        pass
    return 0


def get_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_headers():
    """Get API request headers."""
    token = get_config("access_token", "PAN123_ACCESS_TOKEN")
    if not token:
        raise ValueError("PAN123_ACCESS_TOKEN environment variable is required")
    return {
        "Authorization": f"Bearer {token}",
        "Platform": "open_platform",
        "Content-Type": "application/json"
    }


def get_upload_headers():
    """Get headers for upload domain requests."""
    token = get_config("access_token", "PAN123_ACCESS_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Platform": "open_platform"
    }


def get_upload_domain():
    """Get upload domain from API."""
    resp = requests.get(
        f"{API_BASE}/upload/v2/file/domain",
        headers=get_headers(),
        timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Failed to get upload domain: {data}")
    return data["data"][0]


def create_file(file_path: str, folder_id: int) -> dict:
    """Create file and get upload info."""
    file_path = Path(file_path)
    filename = file_path.name
    file_size = file_path.stat().st_size
    etag = get_md5(str(file_path))
    
    resp = requests.post(
        f"{API_BASE}/upload/v2/file/create",
        headers=get_headers(),
        json={
            "parentFileID": folder_id,
            "filename": filename,
            "etag": etag,
            "size": file_size,
            "duplicate": 1
        },
        timeout=30
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Create file failed: {result.get('message', 'Unknown error')}")
    
    return {
        "file_id": result["data"].get("fileID"),
        "preupload_id": result["data"].get("preuploadID"),
        "reuse": result["data"].get("reuse", False),
        "slice_size": result["data"].get("sliceSize", 16777216),
        "servers": result["data"].get("servers", [])
    }


def get_upload_url(preupload_id: str, slice_no: int) -> str:
    """Get presigned URL for a slice."""
    resp = requests.post(
        f"{API_BASE}/upload/v1/file/get_upload_url",
        headers=get_headers(),
        json={
            "preuploadID": preupload_id,
            "sliceNo": slice_no
        },
        timeout=30
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Get upload URL failed: {result.get('message', 'Unknown error')}")
    
    return result["data"]["presignedURL"]


def upload_slice(presigned_url: str, data: bytes) -> bool:
    """Upload a single slice."""
    resp = requests.put(
        presigned_url,
        data=data,
        headers={"Content-Type": "application/octet-stream"},
        timeout=300
    )
    return resp.status_code == 200


def complete_upload(preupload_id: str) -> dict:
    """Complete the upload."""
    resp = requests.post(
        f"{API_BASE}/upload/v2/file/upload_complete",
        headers=get_headers(),
        json={"preuploadID": preupload_id},
        timeout=30
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Complete upload failed: {result.get('message', 'Unknown error')}")
    
    return result["data"]


def chunked_upload(file_path: str, folder_id: int) -> dict:
    """Upload large file using chunks."""
    file_path = Path(file_path)
    filename = file_path.name
    file_size = file_path.stat().st_size
    
    create_result = create_file(str(file_path), folder_id)
    
    if create_result["reuse"]:
        return {
            "file_id": create_result["file_id"],
            "filename": filename,
            "size": file_size
        }
    
    preupload_id = create_result["preupload_id"]
    slice_size = create_result["slice_size"]
    
    total_slices = (file_size + slice_size - 1) // slice_size
    print(f"Uploading {filename}: {file_size} bytes, {total_slices} slices", file=sys.stderr)
    
    with open(file_path, "rb") as f:
        for slice_no in range(1, total_slices + 1):
            data = f.read(slice_size)
            if not data:
                break
            
            presigned_url = get_upload_url(preupload_id, slice_no)
            
            if not upload_slice(presigned_url, data):
                raise Exception(f"Failed to upload slice {slice_no}/{total_slices}")
            
            print(f"  Slice {slice_no}/{total_slices} uploaded", file=sys.stderr)
    
    complete_result = complete_upload(preupload_id)
    
    return {
        "file_id": complete_result["fileID"],
        "filename": filename,
        "size": file_size
    }


def single_upload(file_path: str, folder_id: int) -> dict:
    """Single-step upload for small files (<1GB)."""
    file_path = Path(file_path)
    filename = file_path.name
    file_size = file_path.stat().st_size
    etag = get_md5(str(file_path))
    
    upload_domain = get_upload_domain()
    url = f"{upload_domain}/upload/v2/file/single/create"
    
    headers = get_upload_headers()
    
    data = {
        "parentFileID": folder_id,
        "filename": filename,
        "etag": etag,
        "size": file_size,
        "duplicate": 1
    }
    
    with open(file_path, "rb") as f:
        files = {"file": (filename, f)}
        resp = requests.post(url, headers=headers, data=data, files=files, timeout=300)
    
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Upload failed: {result.get('message', 'Unknown error')}")
    
    return {
        "file_id": result["data"]["fileID"],
        "filename": filename,
        "size": file_size
    }


def get_direct_link(file_id: int) -> str:
    """Get direct link for a file."""
    resp = requests.get(
        f"{API_BASE}/api/v1/direct-link/url",
        headers=get_headers(),
        params={"fileID": file_id},
        timeout=30
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Failed to get direct link: {result.get('message', 'Unknown error')}")
    
    return result["data"]["url"]


def create_share_link(file_id: int, filename: str) -> str:
    """Create share link for a file."""
    resp = requests.post(
        f"{API_BASE}/api/v1/share/create",
        headers=get_headers(),
        json={
            "shareName": filename,
            "shareExpire": 0,
            "fileIDList": str(file_id)
        },
        timeout=30
    )
    resp.raise_for_status()
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"Failed to create share link: {result.get('message', 'Unknown error')}")
    
    share_key = result["data"]["shareKey"]
    return f"https://www.123pan.com/s/{share_key}"


def get_short_direct_link(file_id: int) -> str:
    """Generate short direct link using fileID only."""
    user_id = get_user_id_from_token()
    if not user_id:
        # Fallback to getting from API
        direct_link = get_direct_link(file_id)
        # Extract user_id from URL: https://{user_id}.v.123pan.cn/...
        parts = direct_link.split(".")
        if parts:
            user_id = parts[0].split("//")[-1]
    return f"https://{user_id}.v.123pan.cn/{user_id}/{file_id}"


def upload_and_get_link(file_path: str, folder_id: int = None, link_type: str = "short_direct") -> dict:
    """Upload file and get link.
    
    link_type options:
    - short_direct: Short direct link (default, recommended)
    - share: Share page link (requires login/redirect)
    - direct: Full direct link with filename
    """
    if folder_id is None:
        folder_id = int(get_config("folder_id", "PAN123_DIRECT_FOLDER_ID", "0"))
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = file_path.stat().st_size
    
    if file_size < 1024 * 1024 * 1024:
        result = single_upload(str(file_path), folder_id)
    else:
        result = chunked_upload(str(file_path), folder_id)
    
    file_id = result["file_id"]
    filename = result["filename"]
    
    if link_type == "share":
        link = create_share_link(file_id, filename)
        link_type_str = "share_link"
    elif link_type == "direct":
        link = get_direct_link(file_id)
        link_type_str = "direct_link"
    else:  # short_direct (default)
        link = get_short_direct_link(file_id)
        link_type_str = "short_direct_link"
    
    return {
        "success": True,
        "file_id": file_id,
        "filename": filename,
        "size": result["size"],
        "link": link,
        "link_type": link_type_str
    }


def main():
    parser = argparse.ArgumentParser(description="Upload files to 123pan")
    parser.add_argument("--file", required=True, help="Path to file to upload")
    parser.add_argument("--folder", type=int, help="Target folder ID")
    parser.add_argument("--link-type", choices=["short_direct", "share", "direct"], 
                       default="short_direct", help="Type of link to return")
    args = parser.parse_args()
    
    try:
        result = upload_and_get_link(args.file, args.folder, args.link_type)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
