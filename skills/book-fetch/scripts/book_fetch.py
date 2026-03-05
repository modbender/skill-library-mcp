#!/usr/bin/env python3
"""
book-fetch.py — Search Anna's Archive, download epub/pdf, upload to MEGA.

Usage:
  python3 book_fetch.py "book title"
  python3 book_fetch.py "book title" --format pdf
  python3 book_fetch.py "book title" --dry-run    # search only, no download
  python3 book_fetch.py "book title" --pick -1    # interactive result picker
"""

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, quote_plus

import requests
from bs4 import BeautifulSoup

# ── Config ──────────────────────────────────────────────────────────────
ANNAS_BASE = "https://annas-archive.li"  # .li mirror; .org is DNS-blocked in EU
MEGA_FOLDER = "/Books"                   # destination folder in MEGA
DOWNLOAD_DIR = Path("/tmp/books")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)


# ── Search ───────────────────────────────────────────────────────────────
def search_books(query: str, fmt: str = "epub") -> list[dict]:
    """Search Anna's Archive, return list of results."""
    url = f"{ANNAS_BASE}/search?q={quote_plus(query)}&ext={fmt}&sort=&lang=&content=book_any"
    print(f"🔍 Searching: {url}")

    for attempt in range(3):
        try:
            resp = session.get(url, timeout=40)
            resp.raise_for_status()
            break
        except Exception as e:
            if attempt == 2:
                raise
            print(f"  Retry {attempt+1}/3: {e}")
            time.sleep(3)

    soup = BeautifulSoup(resp.text, "lxml")
    results = []

    # Title/author stored in data-content attributes inside cover divs
    seen = set()
    for item in soup.select("[data-content]"):
        parent_a = item.find_parent("a", href=lambda h: h and "/md5/" in h)
        if not parent_a:
            continue
        md5 = parent_a["href"].split("/md5/")[-1].split("?")[0]
        if md5 in seen or not md5:
            continue
        seen.add(md5)

        siblings = item.parent.select("[data-content]")
        vals = [s.get("data-content", "") for s in siblings]
        title = vals[0] if len(vals) > 0 else "Unknown"
        author = vals[1] if len(vals) > 1 else ""

        results.append({
            "title": title,
            "author": author,
            "size": "",
            "md5": md5,
            "url": urljoin(ANNAS_BASE, f"/md5/{md5}"),
        })

    return results


# ── Get download link ─────────────────────────────────────────────────────
def get_download_url(book_url: str) -> str | None:
    """Parse book detail page and resolve to a direct download URL.

    Pipeline:
      Anna's Archive md5 page -> libgen.li ads.php -> get.php (direct link)
    """
    print(f"📖 Fetching book page: {book_url}")
    resp = session.get(book_url, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # 1. libgen.li mirror (no login required)
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        if "libgen.li/ads.php" in href:
            direct = _resolve_libgenli(href)
            if direct:
                return direct

    # 2. Anna's Archive fast download (requires membership)
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        if "/fast_download/" in href and "viewer" not in href:
            return urljoin(ANNAS_BASE, href)

    # 3. Anna's Archive slow download (rate-limited, no login)
    for link in soup.select("a[href]"):
        href = link.get("href", "")
        if "/slow_download/" in href:
            return urljoin(ANNAS_BASE, href)

    return None


def _resolve_libgenli(ads_url: str) -> str | None:
    """Fetch libgen.li ads page and extract the get.php direct link."""
    try:
        resp = session.get(ads_url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if "get.php" in href and "md5=" in href and "key=" in href:
                return urljoin("https://libgen.li/", href)
    except Exception as e:
        print(f"  libgen.li resolve failed: {e}")
    return None


# ── Download ─────────────────────────────────────────────────────────────
def download_file(url: str, dest_dir: Path, filename: str) -> Path | None:
    """Download file with progress bar."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename

    print(f"⬇️  Downloading -> {dest}")
    try:
        resp = session.get(url, stream=True, timeout=60, allow_redirects=True)
        resp.raise_for_status()

        total = int(resp.headers.get("content-length", 0))
        downloaded = 0

        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        print(f"\r  {pct:.1f}% ({downloaded//1024}KB/{total//1024}KB)", end="", flush=True)

        print()
        print(f"✅ Downloaded: {dest} ({dest.stat().st_size // 1024}KB)")
        return dest

    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


# ── MEGA upload ───────────────────────────────────────────────────────────
def upload_to_mega(filepath: Path, mega_folder: str = MEGA_FOLDER) -> bool:
    """Upload file to MEGA (tries megacmd first, falls back to rclone)."""
    if not _cmd_exists("mega-put"):
        print("⚠️  megacmd not found. Trying rclone...")
        return upload_via_rclone(filepath, mega_folder)

    print(f"☁️  Uploading to MEGA:{mega_folder}/ ...")
    result = subprocess.run(
        ["mega-put", str(filepath), f"{mega_folder}/"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"✅ Uploaded to MEGA:{mega_folder}/{filepath.name}")
        return True
    else:
        print(f"❌ MEGA upload failed: {result.stderr}")
        return False


def upload_via_rclone(filepath: Path, mega_folder: str) -> bool:
    """Upload via rclone (requires 'mega' remote configured: rclone config)."""
    if not _cmd_exists("rclone"):
        print("❌ Neither megacmd nor rclone found.")
        print(f"   File saved locally: {filepath}")
        return False

    dest = f"mega:{mega_folder}/"
    print(f"☁️  Uploading via rclone -> {dest}")
    result = subprocess.run(
        ["rclone", "copy", str(filepath), dest, "--progress"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"✅ Uploaded via rclone")
        return True
    else:
        print(f"❌ rclone upload failed: {result.stderr}")
        print(f"   File saved locally: {filepath}")
        return False


def _cmd_exists(cmd: str) -> bool:
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0


# ── Filename sanitizer ────────────────────────────────────────────────────
def safe_filename(title: str, author: str, fmt: str) -> str:
    name = f"{title} - {author}" if author else title
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = name[:120].strip()
    return f"{name}.{fmt}"


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Search Anna's Archive and download books to MEGA")
    parser.add_argument("query", help="Book title or author")
    parser.add_argument("--format", "-f", default="epub", choices=["epub", "pdf", "mobi"], help="Preferred format (default: epub)")
    parser.add_argument("--dry-run", action="store_true", help="Search only, do not download")
    parser.add_argument("--pick", type=int, default=0, help="Pick result index (0=first, -1=interactive)")
    args = parser.parse_args()

    # Search
    results = search_books(args.query, args.format)
    if not results:
        print(f"No {args.format} results, retrying without format filter...")
        results = search_books(args.query, "")

    if not results:
        print("❌ No results found.")
        sys.exit(1)

    # Display
    print(f"\n📚 Found {len(results)} results:")
    for i, r in enumerate(results[:10]):
        print(f"  [{i}] {r['title'][:60]} | {r['author'][:30]}")

    if args.dry_run:
        print("\n(dry-run mode, stopping here)")
        return

    # Pick
    if args.pick == -1:
        pick = int(input("\nPick number: "))
    else:
        pick = min(args.pick, len(results) - 1)

    book = results[pick]
    print(f"\n📗 Selected: {book['title']}")

    # Resolve download URL
    dl_url = get_download_url(book["url"])
    if not dl_url:
        print("❌ Could not find a download link.")
        sys.exit(1)

    print(f"🔗 Download URL: {dl_url[:80]}...")

    # Download
    filename = safe_filename(book["title"], book["author"], args.format)
    filepath = download_file(dl_url, DOWNLOAD_DIR, filename)
    if not filepath:
        sys.exit(1)

    # Upload
    upload_to_mega(filepath)


if __name__ == "__main__":
    main()
