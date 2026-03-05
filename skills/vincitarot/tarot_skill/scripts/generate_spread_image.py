#!/usr/bin/env python3
"""
Generate tarot spread image from reading result (includes upright/reversed).
Usage:
  python -m tarot_skill.scripts.generate_spread_image --input reading.json [--output out/spread.png]
  [--images-dir ./cards]  optional: local dir with {id}.jpg to skip network
  cat reading.json | python -m tarot_skill.scripts.generate_spread_image --output out/spread.png
"""

import argparse
import io
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

# Ensure package is importable (run from tarot_skill or games root)
_SCRIPT_DIR = Path(__file__).resolve().parent
_PKG_DIR = _SCRIPT_DIR.parent
_ROOT = _PKG_DIR.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tarot_skill.spread_layouts import SPREAD_LAYOUTS, get_card_image_url

TIMEOUT = 15
PLACEHOLDER_BG = (45, 45, 68)
PLACEHOLDER_BORDER = (107, 107, 138)
PLACEHOLDER_TEXT = (196, 181, 253)


EXPECTED_CARD_COUNT = 78


def _ensure_card_images_once(cards_dir: Path) -> None:
    """On first run, if fewer than 78 card images exist locally, try to download once (same source as tarot_game)."""
    if cards_dir.exists():
        n = len(list(cards_dir.glob("*.jpg")))
        if n >= EXPECTED_CARD_COUNT:
            return
    cards_json = cards_dir.parent / "data" / "cards.json"
    if not cards_json.exists():
        return
    print("First run: downloading card images to", cards_dir, "...", file=sys.stderr)
    cards_dir.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(_ROOT)}
    r = subprocess.run(
        [sys.executable, "-m", "tarot_skill.scripts.download_card_images", "--output-dir", str(cards_dir)],
        cwd=str(_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r.returncode != 0 and r.stderr:
        print(r.stderr, file=sys.stderr)
    n = len(list(cards_dir.glob("*.jpg")))
    if n > 0:
        print(f"Downloaded {n}/78 card images.", file=sys.stderr)
    if n < EXPECTED_CARD_COUNT:
        print("Some images failed (e.g. 403). Spread will use placeholders for missing cards.", file=sys.stderr)


def get_card_url(card_id: str, fallback_url: str, images_dir: Optional[Path]) -> str:
    if images_dir:
        local = images_dir / f"{card_id}.jpg"
        if local.exists():
            return str(local.resolve())
    return fallback_url


# Browser-like headers when requesting sacred-texts to reduce 403 (same source as tarot_game)
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.sacred-texts.com/tarot/pkt/",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
}


def fetch_image(url: str) -> bytes:
    if "://" in url and not url.startswith("file:"):
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read()
    path = url.replace("file:", "").strip()
    return Path(path).read_bytes()


def placeholder_image(width: int, height: int, card_id: str, is_reversed: bool) -> Image.Image:
    img = Image.new("RGB", (width, height), PLACEHOLDER_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=PLACEHOLDER_BORDER, width=2)
    label = f"{card_id}\n{'Reversed' if is_reversed else 'Upright'}"
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 14)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) / 2, (height - th) / 2), label, fill=PLACEHOLDER_TEXT, font=font)
    return img


def load_card_image(
    url: str, width: int, height: int, is_reversed: bool, card_id: str = "?"
) -> Image.Image:
    try:
        raw = fetch_image(url)
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as e:
        print(f"Card {card_id} fetch failed, using placeholder: {e}", file=sys.stderr)
        return placeholder_image(width, height, card_id, is_reversed)
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    if is_reversed:
        img = img.rotate(180, expand=False)
    return img


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate tarot spread image")
    parser.add_argument("--input", help="Path to reading JSON (default: stdin)")
    parser.add_argument("--output", default="out/spread.png", help="Output PNG path")
    parser.add_argument(
        "--images-dir",
        help="Local directory with {card_id}.jpg (default: <repo>/cards if exists)",
    )
    args = parser.parse_args()

    raw = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
    reading = json.loads(raw)

    if not reading.get("ok") or not reading.get("spreadType") or not reading.get("spread"):
        print("Invalid reading: need ok=true, spreadType, and spread array.", file=sys.stderr)
        sys.exit(1)

    spread_type = reading["spreadType"]
    layout = SPREAD_LAYOUTS.get(spread_type)
    if not layout or len(layout["slots"]) != len(reading["spread"]):
        print(
            f'Layout for "{spread_type}" has {len(layout["slots"]) if layout else 0} slots, '
            f"but spread has {len(reading['spread'])} cards.",
            file=sys.stderr,
        )
        sys.exit(1)

    cw = layout["canvas_width"]
    ch = layout["canvas_height"]
    bg_hex = layout["background_color"].lstrip("#")
    bg = tuple(int(bg_hex[i : i + 2], 16) for i in (0, 2, 4))
    base = Image.new("RGB", (cw, ch), bg)

    images_dir = Path(args.images_dir) if args.images_dir else None
    if images_dir is None:
        default_cards = _ROOT / "cards"
        _ensure_card_images_once(default_cards)
        if default_cards.is_dir():
            images_dir = default_cards
    for i, pos in enumerate(reading["spread"]):
        slot = layout["slots"][i]
        card_id = pos["card"]["id"]
        fallback_url = pos["card"].get("image") or get_card_image_url(card_id)
        url = get_card_url(card_id, fallback_url, images_dir)
        print(url)
        card_img = load_card_image(
            url, slot["width"], slot["height"], pos.get("isReversed", False), card_id
        )
        if card_img.size != (slot["width"], slot["height"]):
            card_img = card_img.resize((slot["width"], slot["height"]), Image.Resampling.LANCZOS)
        base.paste(card_img, (slot["x"], slot["y"]))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    base.save(out_path)
    print("Written:", out_path.resolve())


if __name__ == "__main__":
    main()
