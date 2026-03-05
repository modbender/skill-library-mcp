"""
Shared RSS feed parsing for super-transcribe backends.
"""

from __future__ import annotations

import sys

from .exitcodes import EXIT_BAD_INPUT


def fetch_rss_episodes(
    rss_url: str, latest: int = 5, quiet: bool = False
) -> list[tuple[str, str]]:
    """Parse a podcast RSS feed and return audio enclosure URLs.
    Returns list of (url, title) tuples, newest-first.
    """
    import urllib.request
    import xml.etree.ElementTree as ET

    if not quiet:
        print(f"📡 Fetching RSS feed: {rss_url}", file=sys.stderr)

    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "super-transcribe/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read()
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"Error fetching RSS feed: {e}", file=sys.stderr)
        sys.exit(EXIT_BAD_INPUT)

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"Error parsing RSS XML: {e}", file=sys.stderr)
        sys.exit(EXIT_BAD_INPUT)

    items = root.findall(".//item")
    if not items:
        print("Error: No <item> elements found in RSS feed", file=sys.stderr)
        sys.exit(EXIT_BAD_INPUT)

    episodes = []
    for item in items:
        enclosure = item.find("enclosure")
        if enclosure is None:
            continue
        url = (enclosure.get("url") or "").strip()
        if not url:
            continue
        title_el = item.find("title")
        title = (title_el.text or url).strip() if title_el is not None else url
        episodes.append((url, title))

    if not episodes:
        print("Error: No audio <enclosure> elements found in RSS feed", file=sys.stderr)
        sys.exit(EXIT_BAD_INPUT)

    total = len(episodes)
    take = min(latest, total) if latest else total
    if not quiet:
        print(f"   Found {total} episode(s) — processing {take}", file=sys.stderr)

    return episodes[:take] if latest else episodes
