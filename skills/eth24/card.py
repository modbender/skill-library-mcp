#!/usr/bin/env python3
"""Generate Bloomberg-terminal-style ETH24 card image using Pillow."""

import json
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).parent
CONFIG = json.loads((SCRIPT_DIR / "config.json").read_text())

W, H = 1200, 675
BG = "#000000"
WHITE = "#ffffff"
CYAN = "#00e5ff"
DIM = "#666666"
SIGNAL_COLORS = {"URGENT": "#ff3b3b", "WATCH": "#ffd600", "CONTEXT": "#00e676"}
RAINBOW = [
    "#ff0000", "#ff8800", "#ffff00", "#00ff00",
    "#0088ff", "#8800ff", "#ff00ff",
]


def _try_font(path_or_name, size):
    try:
        return ImageFont.truetype(str(path_or_name), size)
    except (OSError, IOError):
        return None


def load_font(size):
    """Load JetBrains Mono, fall back to system monospace, then default."""
    # Bundled font
    for name in ("JetBrainsMono-Regular.ttf", "JetBrainsMono-Bold.ttf"):
        f = _try_font(SCRIPT_DIR / "fonts" / name, size)
        if f:
            return f
    # System monospace
    for name in ("Courier New", "Courier", "DejaVu Sans Mono"):
        f = _try_font(name, size)
        if f:
            return f
    return ImageFont.load_default()


def load_font_bold(size):
    """Load bold variant."""
    f = _try_font(SCRIPT_DIR / "fonts" / "JetBrainsMono-Bold.ttf", size)
    return f or load_font(size)


def generate_card(ranked):
    """Render the card image and return a PIL Image."""
    stories = ranked.get("stories", [])
    date_label = ranked.get("date_label", datetime.now().strftime("%b %d"))
    brand = CONFIG.get("brand", {})
    brand_name = brand.get("name", "ETH24")
    brand_account = brand.get("account", "@ethcforg")
    topic = CONFIG.get("topic", "ETH")

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Rainbow top bar
    seg_w = W / len(RAINBOW)
    for i, color in enumerate(RAINBOW):
        draw.rectangle(
            [int(i * seg_w), 0, int((i + 1) * seg_w), 4],
            fill=color,
        )

    # Fonts
    ft_title = load_font_bold(40)
    ft_date = load_font(28)
    ft_sub = load_font(14)
    ft_handle = load_font_bold(18)
    ft_comment = load_font(18)
    ft_footer = load_font(15)
    ft_small = load_font(13)

    # Header: ETH24 - Feb 12
    draw.text((50, 30), brand_name, fill=WHITE, font=ft_title)
    title_box = draw.textbbox((50, 30), brand_name, font=ft_title)
    draw.text((title_box[2] + 20, 38), f"- {date_label}", fill=DIM, font=ft_date)

    # Separator + subtitle
    draw.line([(50, 80), (250, 80)], fill=DIM, width=1)
    draw.text(
        (50, 92),
        f"DAILY {topic.upper()} INTELLIGENCE",
        fill=DIM,
        font=ft_sub,
    )

    # Stories list
    y = 130
    line_h = 48
    max_show = len(stories)
    for i in range(max_show):
        s = stories[i]
        signal = s.get("signal", "CONTEXT")
        color = SIGNAL_COLORS.get(signal, SIGNAL_COLORS["CONTEXT"])

        # Signal dot
        draw.ellipse([55, y - 4, 67, y + 8], fill=color)

        # @handle
        handle = s.get("handle", "")
        handle_text = f"@{handle}" if handle else ""
        draw.text((80, y - 3), handle_text, fill=CYAN, font=ft_handle)
        hbox = draw.textbbox((80, y - 3), handle_text, font=ft_handle)
        text_x = hbox[2] + 10 if handle_text else 80

        # Commentary (truncate to fit card width using pixel measurement)
        commentary = s.get("commentary", s.get("headline", ""))
        avail_w = W - text_x - 50
        while commentary:
            bbox = draw.textbbox((0, 0), commentary, font=ft_comment)
            if bbox[2] - bbox[0] <= avail_w:
                break
            commentary = commentary[:-1]
        if commentary != s.get("commentary", s.get("headline", "")):
            commentary = commentary[:-3] + "..." if len(commentary) > 3 else "..."
        draw.text((text_x, y - 3), commentary, fill=WHITE, font=ft_comment)

        y += line_h

    # Footer
    draw.line([(50, H - 55), (W - 50, H - 55)], fill=DIM, width=1)
    draw.text(
        (W - 50, H - 40), brand_account, fill=DIM, font=ft_footer, anchor="ra"
    )
    draw.text((50, H - 38), f"${topic[:3].upper()}", fill=CYAN, font=ft_small)

    return img


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    ranked_path = SCRIPT_DIR / "output" / today / "ranked.json"

    if ranked_path.exists():
        ranked = json.loads(ranked_path.read_text())
    else:
        ranked = json.loads(sys.stdin.read())

    img = generate_card(ranked)

    out_dir = SCRIPT_DIR / "output" / today
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "eth24-card.png"
    img.save(str(out_path), "PNG")
    print(f"> Card saved to {out_path}", file=sys.stderr)
    print(str(out_path))


if __name__ == "__main__":
    main()
