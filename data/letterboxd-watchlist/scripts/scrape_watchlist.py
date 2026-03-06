#!/usr/bin/env python3
"""Scrape a public Letterboxd user's watchlist.

Outputs CSV (title,link) or JSONL (one object per line).

Example:
  uv run scrape_watchlist.py <username> --out watchlist.csv
"""

import argparse
import csv
import html as html_lib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin

BASE = "https://letterboxd.com"

POSTER_RE = re.compile(
    r'data-target-link="(?P<link>/film/[^\"]+/)"[^>]*>\s*'
    r'<div class="poster film-poster">\s*'
    r'<img[^>]+alt="(?P<title>[^\"]+)"',
    re.S,
)


def fetch(url: str, timeout: int = 30, user_agent: str = "Mozilla/5.0") -> str:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def validate_username(username: str) -> str:
    username = username.strip().strip("/")
    if not username:
        raise ValueError("username is required")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", username):
        raise ValueError("username contains invalid characters")
    return username


def scrape_watchlist(
    username: str,
    max_pages: int = 500,
    delay_ms: int = 250,
    timeout: int = 30,
    retries: int = 2,
):
    username = validate_username(username)

    seen = set()
    items = []

    for page in range(1, max_pages + 1):
        url = f"{BASE}/{username}/watchlist/page/{page}/"

        html = None
        for attempt in range(retries + 1):
            try:
                html = fetch(url, timeout=timeout)
                break
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    html = ""
                    break
                if attempt >= retries:
                    raise
                time.sleep(0.5 * (attempt + 1))
            except (urllib.error.URLError, TimeoutError):
                if attempt >= retries:
                    raise
                time.sleep(0.5 * (attempt + 1))

        found = POSTER_RE.findall(html or "")

        if not found:
            break

        for link, title in found:
            title = html_lib.unescape(title).strip()
            full = urljoin(BASE, link)
            key = (title, full)
            if key in seen:
                continue
            seen.add(key)
            items.append({"title": title, "link": full})

        if delay_ms:
            time.sleep(delay_ms / 1000.0)

    return items


def write_csv(path: str, items):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title", "link"])
        w.writeheader()
        w.writerows(items)


def write_jsonl(path: str, items):
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("username", help="Letterboxd username (public profile)")
    ap.add_argument("--out", required=True, help="Output path (.csv or .jsonl)")
    ap.add_argument("--max-pages", type=int, default=500)
    ap.add_argument("--delay-ms", type=int, default=250)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--retries", type=int, default=2)
    args = ap.parse_args(argv)

    items = scrape_watchlist(
        args.username,
        max_pages=args.max_pages,
        delay_ms=args.delay_ms,
        timeout=args.timeout,
        retries=args.retries,
    )

    out = args.out
    if out.lower().endswith(".csv"):
        write_csv(out, items)
    elif out.lower().endswith(".jsonl"):
        write_jsonl(out, items)
    else:
        raise SystemExit("--out must end with .csv or .jsonl")

    print(f"count {len(items)}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
