#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Fetch nearby photos from OpenStreetCam API and optionally download them.
Usage:
  uv run scripts/fetch_openstreetcam.py --lat 48.8566 --lng 2.3522 --radius 2000 --output ./assets/osc --max-photos 20
"""
import argparse
import json
import sys
from pathlib import Path

import requests

OSC_BASE = "https://api.openstreetcam.org"
OSC_PHOTO_BASE = "https://api.openstreetcam.org/"
NEARBY_PHOTOS = f"{OSC_BASE}/1.0/list/nearby-photos/"
HEADERS = {"User-Agent": "TravelDestinationBrochure/1.0 (skill)"}


def fetch_nearby_photos(lat: float, lng: float, radius: float, page: int = 1, ipp: int = 50) -> dict:
    data = {"lat": lat, "lng": lng, "radius": radius, "page": page, "ipp": ipp}
    r = requests.post(NEARBY_PHOTOS, data=data, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def download_file(url: str, path: Path) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        r.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception:
        return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch OpenStreetCam photos near a point.")
    ap.add_argument("--lat", type=float, required=True, help="Latitude")
    ap.add_argument("--lng", type=float, required=True, help="Longitude")
    ap.add_argument("--radius", type=float, default=2000, help="Radius in meters (default 2000)")
    ap.add_argument("--output", type=str, default="./assets/osc", help="Output directory")
    ap.add_argument("--max-photos", type=int, default=20, help="Max photos to download (default 20)")
    ap.add_argument("--no-download", action="store_true", help="Only build manifest, do not download images")
    args = ap.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        resp = fetch_nearby_photos(args.lat, args.lng, args.radius, page=1, ipp=min(100, args.max_photos + 10))
    except requests.RequestException as e:
        print(f"OpenStreetCam request failed: {e}", file=sys.stderr)
        sys.exit(1)

    status = resp.get("status", {})
    if status.get("httpCode") != 200:
        print(f"API error: {status.get('apiMessage', resp)}", file=sys.stderr)
        sys.exit(1)

    # Paginated structure: currentPageItems can be list of photos or nested
    raw_items = resp.get("currentPageItems") or resp.get("result") or []
    if isinstance(raw_items, dict):
        items = raw_items.get("data", []) if isinstance(raw_items.get("data"), list) else []
    else:
        items = raw_items if isinstance(raw_items, list) else []

    # Normalize: OSC may return items with name/lth_name/th_name, or nested osv.photos
    photos = []
    for it in items:
        if isinstance(it, dict):
            if "lth_name" in it or "name" in it or "th_name" in it:
                photos.append(it)
            elif "photos" in it:
                photos.extend(it["photos"] if isinstance(it["photos"], list) else [])
        if len(photos) >= args.max_photos:
            break
    photos = photos[: args.max_photos]

    manifest = []
    for i, ph in enumerate(photos):
        # Prefer large thumbnail or full image URL
        url = ph.get("lth_name") or ph.get("name") or ph.get("th_name") or ""
        if not url:
            continue
        # Construct full URL if relative
        if not url.startswith("http"):
            url = OSC_PHOTO_BASE + url
        caption = f"OpenStreetCam photo at lat {ph.get('lat')}, lng {ph.get('lng')}"
        if ph.get("date_added"):
            caption += f" ({ph.get('date_added')})"
        entry = {"index": i, "url": url, "lat": ph.get("lat"), "lng": ph.get("lng"), "caption": caption}
        if not args.no_download:
            ext = "jpg" if "jpg" in url.lower() or "jpeg" in url.lower() else "jpg"
            fname = out_dir / f"osc_{i:04d}.{ext}"
            if download_file(url, fname):
                entry["path"] = str(fname.resolve())
            else:
                entry["path"] = None
        manifest.append(entry)

    manifest_path = out_dir / "osc_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"lat": args.lat, "lng": args.lng, "radius": args.radius, "photos": manifest}, f, indent=2)

    print(json.dumps({"count": len(manifest), "manifest": str(manifest_path), "output_dir": str(out_dir)}, indent=2))


if __name__ == "__main__":
    main()
