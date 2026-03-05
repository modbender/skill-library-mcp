#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Search Wikimedia Commons for images and optionally download them.
Usage:
  uv run scripts/fetch_commons.py --query "Paris landmarks" --output ./assets/commons --max-images 15
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

import requests

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "TravelDestinationBrochure/1.0 (skill)"}


def search_commons(query: str, limit: int = 20) -> list[str]:
    """Return list of File: page titles."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,
        "srlimit": limit,
        "format": "json",
    }
    r = requests.get(COMMONS_API, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    items = data.get("query", {}).get("search", [])
    return [x["title"] for x in items]


def get_imageinfo(titles: list[str]) -> dict:
    """Get image URLs and extmetadata for given File: titles."""
    params = {
        "action": "query",
        "titles": "|".join(titles),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime",
        "iiurlwidth": 1200,
        "format": "json",
    }
    r = requests.get(COMMONS_API, params=params, headers=HEADERS, timeout=30)
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


def safe_filename(title: str, index: int) -> str:
    """From File:Example name.jpg -> example_name.jpg."""
    name = title.replace("File:", "").strip()
    name = re.sub(r"[^\w\-_.]", "_", name)[:80]
    if not name:
        name = f"commons_{index}"
    if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        name += ".jpg"
    return name


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch Wikimedia Commons images by search query.")
    ap.add_argument("--query", type=str, required=True, help='Search query, e.g. "Paris landmarks"')
    ap.add_argument("--output", type=str, default="./assets/commons", help="Output directory")
    ap.add_argument("--max-images", type=int, default=15, help="Max images to download (default 15)")
    ap.add_argument("--no-download", action="store_true", help="Only build manifest, do not download images")
    args = ap.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        titles = search_commons(args.query, limit=args.max_images)
    except requests.RequestException as e:
        print(f"Commons search failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not titles:
        print(f"No images found for: {args.query}", file=sys.stderr)
        sys.exit(1)

    try:
        info_resp = get_imageinfo(titles)
    except requests.RequestException as e:
        print(f"Commons imageinfo failed: {e}", file=sys.stderr)
        sys.exit(1)

    pages = info_resp.get("query", {}).get("pages", {})
    manifest = []
    for i, (pid, p) in enumerate(pages.items()):
        if i >= args.max_images:
            break
        if pid == "-1" or "missing" in p:
            continue
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        url = ii.get("url") or ii.get("thumburl") or ""
        if not url:
            continue
        extmeta = ii.get("extmetadata") or {}
        desc = (extmeta.get("ImageDescription") or {}).get("value") or ""
        obj = (extmeta.get("ObjectName") or {}).get("value") or ""
        caption = (obj or desc or p.get("title", "")).replace("File:", "").strip()
        if len(caption) > 500:
            caption = caption[:497] + "..."
        title = p.get("title", "File:unknown.jpg")
        entry = {"index": i, "title": title, "url": url, "caption": caption or title}
        if not args.no_download:
            fname = out_dir / safe_filename(title, i)
            if download_file(url, fname):
                entry["path"] = str(fname.resolve())
            else:
                entry["path"] = None
        manifest.append(entry)

    manifest_path = out_dir / "commons_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"query": args.query, "images": manifest}, f, indent=2)

    print(json.dumps({"count": len(manifest), "manifest": str(manifest_path), "output_dir": str(out_dir)}, indent=2))


if __name__ == "__main__":
    main()
