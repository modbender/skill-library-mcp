#!/usr/bin/env python3
"""
Generate 小红书 cover image (1080x1440) with gradient background and CJK text.

Requirements:
  - python3, Pillow (pip install Pillow or apt install python3-pil)
  - CJK fonts: fonts-noto-cjk on Linux, or Noto Sans CJK via Homebrew on macOS

Usage:
  python3 gen_cover.py --title "主标题" --subtitle "副标题" --tags "标签1,标签2" --output cover.png

Font paths:
  The script searches common locations for Noto Sans CJK fonts on Linux and macOS.
  If fonts are not found, you may need to adjust the CJK_FONT_SEARCH_PATHS below
  to match your system's font installation.
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

W, H = 1080, 1440

GRADIENTS = {
    "purple": ((102, 126, 234), (240, 147, 251)),
    "blue":   ((30, 60, 180),   (100, 180, 255)),
    "green":  ((34, 139, 87),   (144, 238, 144)),
    "orange": ((255, 140, 0),   (255, 200, 100)),
    "dark":   ((30, 30, 60),    (80, 80, 120)),
}

# Search paths for CJK fonts — add your system's font paths if needed.
# The script tries each path in order and uses the first one found.
CJK_BOLD_SEARCH_PATHS = [
    # Linux (apt install fonts-noto-cjk)
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    # macOS (Homebrew: brew install font-noto-sans-cjk)
    "/opt/homebrew/share/fonts/NotoSansCJK-Bold.ttc",
    "/usr/local/share/fonts/NotoSansCJK-Bold.ttc",
    # macOS system fonts (partial CJK support)
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]

CJK_REG_SEARCH_PATHS = [
    # Linux (apt install fonts-noto-cjk)
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    # macOS (Homebrew: brew install font-noto-sans-cjk)
    "/opt/homebrew/share/fonts/NotoSansCJK-Regular.ttc",
    "/usr/local/share/fonts/NotoSansCJK-Regular.ttc",
    # macOS system fonts (partial CJK support)
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]


def find_font(search_paths, label):
    """Find the first available font from the search paths."""
    for path in search_paths:
        if os.path.exists(path):
            return path
    print(
        f"Error: {label} CJK font not found. Searched:\n"
        + "\n".join(f"  - {p}" for p in search_paths)
        + "\n\nOn Linux: apt install fonts-noto-cjk"
        + "\nOn macOS: brew install font-noto-sans-cjk",
        file=sys.stderr,
    )
    sys.exit(1)


CJK_BOLD = None
CJK_REG = None


def check_fonts():
    global CJK_BOLD, CJK_REG
    CJK_BOLD = find_font(CJK_BOLD_SEARCH_PATHS, "Bold")
    CJK_REG = find_font(CJK_REG_SEARCH_PATHS, "Regular")


def draw_gradient(draw, color_top, color_bot):
    for y in range(H):
        r = y / H
        c = tuple(int(color_top[i] + (color_bot[i] - color_top[i]) * r) for i in range(3))
        draw.line([(0, y), (W, y)], fill=c + (255,))


def add_decorative_circles(img):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    circles = [(200, 200, 150, 30), (900, 350, 200, 20),
               (150, 1100, 180, 25), (850, 1200, 130, 30)]
    for cx, cy, rad, alpha in circles:
        od.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                   fill=(255, 255, 255, alpha))
    return Image.alpha_composite(img, overlay)


def draw_badge(img, text):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(CJK_REG, 34)
    bbox = draw.textbbox((0, 0), text, font=font)
    bw = bbox[2] - bbox[0] + 50
    bh = bbox[3] - bbox[1] + 24
    bx, by = W - bw - 50, 60

    badge_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge_bg)
    bd.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2,
                         fill=(255, 255, 255, 60), outline=(255, 255, 255, 100), width=2)
    img = Image.alpha_composite(img, badge_bg)
    draw = ImageDraw.Draw(img)
    draw.text((bx + 25, by + 8), text, fill="white", font=font)
    return img


def draw_title(img, title, subtitle=None):
    draw = ImageDraw.Draw(img)
    font_huge = ImageFont.truetype(CJK_BOLD, 82)
    font_med  = ImageFont.truetype(CJK_BOLD, 48)

    # Split title into lines if too long (auto-wrap at ~8 chars)
    max_chars_per_line = 8
    lines = []
    while title:
        lines.append(title[:max_chars_per_line])
        title = title[max_chars_per_line:]

    # Calculate total height
    line_heights = []
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font_huge)
        line_heights.append(bb[3] - bb[1])

    total_h = sum(line_heights) + 40 * (len(lines) - 1)
    if subtitle:
        bbs = draw.textbbox((0, 0), subtitle, font=font_med)
        sub_h = bbs[3] - bbs[1]
        total_h += sub_h + 50

    start_y = (H - total_h) // 2 - 50
    y = start_y

    for i, line in enumerate(lines):
        bb = draw.textbbox((0, 0), line, font=font_huge)
        tw = bb[2] - bb[0]
        th = bb[3] - bb[1]
        x = (W - tw) // 2

        # Highlight last line
        if i == len(lines) - 1 and len(lines) > 1:
            hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            hd = ImageDraw.Draw(hl)
            hd.rounded_rectangle([x - 25, y - 10, x + tw + 25, y + th + 15],
                                 radius=15, fill=(255, 255, 255, 50))
            img = Image.alpha_composite(img, hl)
            draw = ImageDraw.Draw(img)

        draw.text((x, y), line, fill="white", font=font_huge)
        y += th + 40

    if subtitle:
        y += 10
        bbs = draw.textbbox((0, 0), subtitle, font=font_med)
        tws = bbs[2] - bbs[0]
        draw.text(((W - tws) // 2, y), subtitle, fill=(255, 255, 255, 230), font=font_med)
        y += bbs[3] - bbs[1]

    return img, y


def draw_tags(img, tags, start_y):
    if not tags:
        return img
    draw = ImageDraw.Draw(img)
    font_tag = ImageFont.truetype(CJK_BOLD, 34)

    # Arrange in rows of 2-3
    rows = []
    row = []
    for tag in tags:
        row.append(tag)
        if len(row) >= 3 or (len(row) >= 2 and len(rows) == 0):
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    y = start_y + 60
    for row_tags in rows:
        # Measure
        tag_widths = []
        for tag in row_tags:
            bbt = draw.textbbox((0, 0), tag, font=font_tag)
            tag_widths.append(bbt[2] - bbt[0] + 60)

        row_w = sum(tag_widths) + 20 * (len(tag_widths) - 1)
        rx = (W - row_w) // 2

        tag_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag_layer)

        for tag, tw in zip(row_tags, tag_widths):
            bbt = draw.textbbox((0, 0), tag, font=font_tag)
            th = bbt[3] - bbt[1]
            td.rounded_rectangle([rx, y, rx + tw, y + th + 26],
                                 radius=(th + 26) // 2,
                                 fill=(255, 255, 255, 50),
                                 outline=(255, 255, 255, 80), width=1)
            # Need to composite then redraw
            img = Image.alpha_composite(img, tag_layer)
            draw = ImageDraw.Draw(img)
            draw.text((rx + 30, y + 10), tag, fill="white", font=font_tag)
            # Reset layer for next tag
            tag_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            td = ImageDraw.Draw(tag_layer)
            rx += tw + 20

        y += 75

    return img


def draw_logo(img, text="OpenClaw"):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(CJK_BOLD, 48)
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    draw.text(((W - tw) // 2, H - 120), text, fill=(255, 255, 255, 200), font=font)
    return img


def main():
    parser = argparse.ArgumentParser(description="Generate 小红书 cover image")
    parser.add_argument("--title", required=True, help="Main title text")
    parser.add_argument("--subtitle", default=None, help="Subtitle text")
    parser.add_argument("--tags", default=None, help="Comma-separated feature tags")
    parser.add_argument("--badge", default="OpenClaw", help="Badge text (top-right)")
    parser.add_argument("--output", default="cover.png", help="Output file path")
    parser.add_argument("--gradient", default="purple", choices=GRADIENTS.keys(),
                        help="Color scheme")
    args = parser.parse_args()

    check_fonts()

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    # Create base image
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)

    # Gradient background
    color_top, color_bot = GRADIENTS[args.gradient]
    draw_gradient(draw, color_top, color_bot)

    # Decorative elements
    img = add_decorative_circles(img)

    # Badge
    img = draw_badge(img, args.badge)

    # Title + subtitle
    img, content_bottom = draw_title(img, args.title, args.subtitle)

    # Tags
    img = draw_tags(img, tags, content_bottom)

    # Logo
    img = draw_logo(img)

    # Save
    img.convert("RGB").save(args.output, "PNG", quality=95)
    size = os.path.getsize(args.output)
    print(f"Cover saved: {args.output} ({size:,} bytes)")


if __name__ == "__main__":
    main()
