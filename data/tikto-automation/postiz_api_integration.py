import os
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

POSTIZ_API_KEY = os.getenv("POSTIZ_API_KEY")
POSTIZ_API_URL = os.getenv("POSTIZ_API_URL", "https://api.postiz.com/v1")


class PostizError(Exception):
    pass


def _auth_headers() -> Dict[str, str]:
    if not POSTIZ_API_KEY:
        raise PostizError("POSTIZ_API_KEY is not set in environment")
    return {"Authorization": f"Bearer {POSTIZ_API_KEY}"}


def upload_media_to_postiz(file_path: str) -> Dict[str, Any]:
    """Uploads a local image file to Postiz and returns the parsed JSON response.

    Returns a dict with at least an `id` or `url` depending on API.
    """
    p = Path(file_path)
    if not p.exists():
        raise PostizError(f"file not found: {file_path}")

    url = f"{POSTIZ_API_URL}/media/upload"
    headers = _auth_headers()
    with p.open('rb') as fh:
        files = {'file': fh}
        resp = requests.post(url, headers=headers, files=files)
    try:
        resp.raise_for_status()
    except Exception as e:
        raise PostizError(f"upload failed: {e} - {resp.text}")
    return resp.json()


def create_tiktok_draft(media_ids: List[str], caption: str, privacy_level: str = "SELF_ONLY") -> Dict[str, Any]:
    url = f"{POSTIZ_API_URL}/tiktok/create_draft"
    headers = _auth_headers()
    headers.update({"Content-Type": "application/json"})
    payload = {
        "type": "carousel",
        "media_ids": media_ids,
        "caption": caption,
        "privacy_level": privacy_level,
    }
    resp = requests.post(url, headers=headers, json=payload)
    try:
        resp.raise_for_status()
    except Exception as e:
        raise PostizError(f"create_draft failed: {e} - {resp.text}")
    return resp.json()


def upload_images_and_create_draft(image_paths: List[str], caption: str) -> Dict[str, Any]:
    """Convenience: upload list of local images and create a draft. Returns draft response."""
    media_ids = []
    for p in image_paths:
        r = upload_media_to_postiz(p)
        # try common keys for media id
        mid = r.get('media_id') or r.get('id') or r.get('result', {}).get('id')
        if not mid:
            # if API returned a full object, append raw
            mid = r
        media_ids.append(mid)
    return create_tiktok_draft(media_ids, caption)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Upload images to Postiz and create a TikTok draft')
    parser.add_argument('images', nargs='+')
    parser.add_argument('--caption', default='')
    args = parser.parse_args()
    print(upload_images_and_create_draft(args.images, args.caption))
