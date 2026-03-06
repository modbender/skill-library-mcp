#!/usr/bin/env python3
"""
Download 78 card images from the same source as tarot_game (tarotCards.ts IMG_ROOT).
Use --images-dir with generate_spread_image to show real card art and avoid 403 placeholders.

Usage:
  python -m tarot_skill.scripts.download_card_images [--output-dir ./cards] [--force]
Run from tarot_skill repo root or games; requires data/cards.json (npm run export-cards).
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

# Same path and headers as generate_spread_image
_SCRIPT_DIR = Path(__file__).resolve().parent
_PKG_DIR = _SCRIPT_DIR.parent
_ROOT = _PKG_DIR.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tarot_skill.spread_layouts import get_card_image_url

TIMEOUT = 15
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.sacred-texts.com/tarot/pkt/",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
}


def main() -> None:
