#!/usr/bin/env python3
"""foto_webcam_snapshot.py

Fetch a current snapshot image for a foto-webcam.eu webcam page or from a favorites list.

Usage examples:
  python3 foto_webcam_snapshot.py --url https://www.foto-webcam.eu/webcam/zugspitze/ --out /tmp/zugspitze.jpg
  python3 foto_webcam_snapshot.py --favorites docs/webcams/favorites-muenchen.json --id 4 --out /tmp/webcam4.jpg

Outputs:
  - Writes JPG bytes to --out
  - Prints a single JSON line to stdout: {ok, out, sourceUrl, pageUrl, name, id}

Notes:
  - Uses a browser-like User-Agent.
  - Best-effort HTML parsing via regex.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.parse import urljoin

import requests

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def read_favorites(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_current_image_from_page(page_url: str) -> str:
    r = requests.get(page_url, headers={"User-Agent": UA, "Accept": "text/html"}, timeout=30)
    r.raise_for_status()
    html = r.text

    # Prefer explicit current/<digits>.jpg occurrences
    m = re.search(r"https://www\.foto-webcam\.eu/webcam/[^\s\"']+/current/\d+\.jpg", html)
    if m:
        return m.group(0)

    # Fallback: build from /webcam/<slug>/
    m2 = re.search(r"https://www\.foto-webcam\.eu/webcam/([^/]+)/", page_url)
    if m2:
        slug = m2.group(1)
        return f"https://www.foto-webcam.eu/webcam/{slug}/current/1200.jpg"

    # Generic fallback: search for any jpg
    m3 = re.search(r"https?://[^\s\"']+\.jpg", html, flags=re.IGNORECASE)
    if m3:
        return m3.group(0)

    raise RuntimeError("Could not resolve current image URL")


def download_image(url: str) -> bytes:
    r = requests.get(url, headers={"User-Agent": UA, "Accept": "image/avif,image/webp,image/apng,image/*,*/*"}, timeout=30)
    r.raise_for_status()
    return r.content


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", help="foto-webcam page URL")
    p.add_argument("--favorites", help="favorites json file")
    p.add_argument("--id", type=int, help="favorites id")
    p.add_argument("--out", required=True, help="output jpg path")

    a = p.parse_args()

    page_url = a.url
    fav_name = None
    fav_id = a.id
    source_url = None

    if a.favorites and a.id is not None:
        fav = read_favorites(a.favorites)
        items = fav.get("items") or []
        hit = next((it for it in items if int(it.get("id")) == int(a.id)), None)
        if not hit:
            raise RuntimeError(f"Favorite id not found: {a.id}")
        fav_name = hit.get("name")
        page_url = hit.get("page")
        source_url = hit.get("image")

    if not page_url:
        raise RuntimeError("Missing --url or --favorites+--id")

    if not source_url:
        source_url = resolve_current_image_from_page(page_url)

    data = download_image(source_url)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(data)

    sys.stdout.write(
        json.dumps(
            {
                "ok": True,
                "out": a.out,
                "sourceUrl": source_url,
                "pageUrl": page_url,
                "name": fav_name,
                "id": fav_id,
                "bytes": len(data),
            }
        )
        + "\n"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        sys.stdout.write(json.dumps({"ok": False, "error": str(e)}) + "\n")
        raise
