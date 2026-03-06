#!/usr/bin/env python3
"""
generate_card.py — Generate an HTML bird trading card from the card template.

Fetches the bird image and embeds it as base64 for a fully self-contained card.
Saves card to {workspace}/cards/{slug}-{timestamp}.html and prints the path.

Usage:
  python generate_card.py \
    --species "American Robin" \
    --scientific-name "Turdus migratorius" \
    --rarity "common" \
    --region "California" \
    --date "2026-02-20" \
    --fun-fact "American Robins can produce up to three broods per year." \
    --image-url "https://example.com/robin.jpg" \
    --life-count 12 \
    [--slug "american-robin"] \
    [--workspace "./birdfolio"]

Output (JSON to stdout):
  {"status": "ok", "cardPath": "...", "slug": "...", "filename": "..."}
"""
import argparse
import base64
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError


RARITY_COLORS = {
    "common":    "#16a34a",
    "rare":      "#b45309",
    "superRare": "#dc2626",
    "bonus":     "#475569"
}
RARITY_LABELS = {
    "common":    "Common",
    "rare":      "Rare",
    "superRare": "Super Rare",
    "bonus":     "Bonus Find"
}
RARITY_EMOJIS = {
    "common":    "\U0001f7e2",   # 🟢
    "rare":      "\U0001f7e1",   # 🟡
    "superRare": "\U0001f534",   # 🔴
    "bonus":     "\u2728"        # ✨
}


def slugify(name):
    return name.lower().replace(" ", "-").replace("'", "").replace(".", "")


def fetch_image_as_data_uri(url):
    """Download image and return as data URI for embedding in HTML."""
    if not url:
        return ""
    try:
        req = Request(url, headers={"User-Agent": "Birdfolio/1.0"})
        with urlopen(req, timeout=10) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
            b64 = base64.b64encode(data).decode("ascii")
            return f"data:{content_type};base64,{b64}"
    except (URLError, Exception):
        # Fall back to URL directly — canvas may still load it
        return url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--species", required=True, help="Common name")
    parser.add_argument("--scientific-name", required=True, help="Scientific name")
    parser.add_argument("--rarity", required=True, choices=["common", "rare", "superRare", "bonus"])
    parser.add_argument("--region", required=True, help="Region where spotted")
    parser.add_argument("--date", required=True, help="Date spotted YYYY-MM-DD")
    parser.add_argument("--fun-fact", default="", help="One interesting fact about the species")
    parser.add_argument("--image-url", default="", help="Bird photo URL (use --image-path for local files)")
    parser.add_argument("--image-path", default="", help="Local path to bird photo (base64-embeds automatically)")
    parser.add_argument("--life-count", type=int, default=1, help="Bird number in life list")
    parser.add_argument("--object-position", default="center center", help="CSS object-position for bird photo (e.g. 40%% center)")
    parser.add_argument("--slug", default=None, help="URL slug (auto-generated if omitted)")
    parser.add_argument("--workspace", default="./birdfolio", help="Workspace directory")
    args = parser.parse_args()

    workspace = os.path.abspath(args.workspace)
    slug = args.slug or slugify(args.species)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    cards_dir = os.path.join(workspace, "cards")
    os.makedirs(cards_dir, exist_ok=True)

    # Locate template relative to this script: ../assets/card-template.html
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(skill_dir, "assets", "card-template.html")

    if not os.path.exists(template_path):
        print(json.dumps({"status": "error", "message": f"Template not found at {template_path}"}))
        sys.exit(1)

    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    # Prefer local image path over URL
    if args.image_path and os.path.exists(args.image_path):
        with open(args.image_path, "rb") as f:
            data = f.read()
        import mimetypes
        mime = mimetypes.guess_type(args.image_path)[0] or "image/jpeg"
        b64 = base64.b64encode(data).decode("ascii")
        image_src = f"data:{mime};base64,{b64}"
    else:
        image_src = fetch_image_as_data_uri(args.image_url)

    replacements = {
        "{{COMMON_NAME}}":     args.species,
        "{{SCIENTIFIC_NAME}}": args.scientific_name,
        "{{RARITY}}":          RARITY_LABELS.get(args.rarity, "Common"),
        "{{RARITY_COLOR}}":    RARITY_COLORS.get(args.rarity, "#16a34a"),
        "{{RARITY_EMOJI}}":    RARITY_EMOJIS.get(args.rarity, "\U0001f7e2"),
        "{{REGION}}":          args.region,
        "{{DATE}}":            args.date,
        "{{FUN_FACT}}":        args.fun_fact,
        "{{BIRD_IMAGE_SRC}}":  image_src,
        "{{LIFE_COUNT}}":      str(args.life_count),
        "{{OBJECT_POSITION}}": args.object_position,
    }

    card_html = template
    for key, value in replacements.items():
        card_html = card_html.replace(key, value)

    card_filename = f"{slug}-{timestamp}.html"
    card_path = os.path.join(cards_dir, card_filename)

    with open(card_path, "w", encoding="utf-8") as f:
        f.write(card_html)

    print(json.dumps({
        "status": "ok",
        "cardPath": card_path,
        "slug": slug,
        "filename": card_filename
    }))


if __name__ == "__main__":
    main()
