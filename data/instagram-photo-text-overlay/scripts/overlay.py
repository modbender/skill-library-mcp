#!/usr/bin/env python3
"""
Instagram photo text overlay — generates a portrait (4:5) image with
a gradient overlay and text for Instagram posts.

Usage:
  python3 overlay.py --input photo.jpg --output out.jpg \
    --title "TAORMINA" --subtitle "3-Day Trip Itinerary" \
    --items '["Teatro Greco|Ancient theatre with Mt. Etna views", "Bam Bar|Legendary pistachio granita"]' \
    [--watermark "tabiji.ai"] [--accent "255,220,150"] [--style list|clean]
"""

import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageFont

# --- Font helpers ---

FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNSText.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

BOLD_INDEX = 1  # index inside .ttc for bold variant (Helvetica)
ITALIC_INDEX = 2  # index inside .ttc for oblique/italic variant (Helvetica)

def _find_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

def get_font(path, size, bold=False, italic=False):
    if path is None:
        return ImageFont.load_default()
    try:
        idx = 0
        if bold and path.endswith(".ttc"):
            idx = BOLD_INDEX
        elif italic and path.endswith(".ttc"):
            idx = ITALIC_INDEX
        return ImageFont.truetype(path, size, index=idx)
    except Exception:
        return ImageFont.truetype(path, size)

# --- Crop to 4:5 portrait ---

def crop_portrait(img):
    W, H = img.size
    target = 4 / 5
    current = W / H
    if current > target:
        new_w = int(H * target)
        left = (W - new_w) // 2
        img = img.crop((left, 0, left + new_w, H))
    elif current < target:
        new_h = int(W / target)
        top = (H - new_h) // 2
        img = img.crop((0, top, W, top + new_h))
    return img

# --- Draw gradient ---

def draw_gradient(img, start_pct, max_alpha=200, power=0.8):
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    grad_start = int(H * start_pct)
    for y in range(grad_start, H):
        alpha = int(max_alpha * ((y - grad_start) / (H - grad_start)) ** power)
        draw.rectangle([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

# --- Text wrapping helper ---

def wrap_text(draw, text, font, max_width):
    """Split text into lines that fit within max_width pixels."""
    words = text.split()
    if not words:
        return [text]
    lines = []
    current = words[0]
    for word in words[1:]:
        test = current + " " + word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines

# --- Styles ---

def _estimate_list_height(draw, W, scale, title, subtitle, items, fp, max_text_w):
    """Estimate total content height for list style at given scale factor."""
    title_font = get_font(fp, int(W * 0.085 * scale), bold=True)
    title_lines = wrap_text(draw, title.upper(), title_font, max_text_w)
    h = len(title_lines) * int(W * 0.095 * scale)

    sub_font = get_font(fp, int(W * 0.038 * scale))
    sub_lines = wrap_text(draw, subtitle, sub_font, max_text_w)
    h += len(sub_lines) * int(W * 0.05 * scale)
    h += int(W * 0.015 * scale)  # subtitle gap
    h += int(W * 0.035 * scale)  # divider gap

    item_font = get_font(fp, int(W * 0.033 * scale), bold=True)
    reason_font = get_font(fp, int(W * 0.028 * scale))
    num_offset = int(W * 0.06 * scale)
    item_max_w = max_text_w - num_offset

    for item in items:
        parts = item.split("|", 1)
        name = parts[0].strip()
        reason = parts[1].strip() if len(parts) > 1 else ""
        name_lines = wrap_text(draw, name, item_font, item_max_w)
        h += len(name_lines) * int(W * 0.042 * scale)
        if reason:
            reason_lines = wrap_text(draw, reason, reason_font, item_max_w)
            h += len(reason_lines) * int(W * 0.048 * scale)
        else:
            h += int(W * 0.02 * scale)
    return h


def render_list(img, title, subtitle, items, watermark, accent):
    W, H = img.size
    fp = _find_font()
    img = draw_gradient(img, 0.38, 200, 0.8)
    draw = ImageDraw.Draw(img)
    margin = int(W * 0.06)
    ac = tuple(int(c) for c in accent.split(","))
    max_text_w = W - 2 * margin
    bottom_pad = int(H * 0.04)
    available_h = H - int(H * 0.44) - bottom_pad

    # Find scale that fits
    scale = 1.0
    for _ in range(10):
        est = _estimate_list_height(draw, W, scale, title, subtitle, items, fp, max_text_w)
        if est <= available_h:
            break
        scale *= 0.9

    # Watermark
    if watermark:
        draw.text((margin, int(H * 0.03)), watermark, font=get_font(fp, int(W * 0.03)), fill=(255, 255, 255, 200))

    y = int(H * 0.44)

    # Title
    title_font = get_font(fp, int(W * 0.085 * scale), bold=True)
    title_lines = wrap_text(draw, title.upper(), title_font, max_text_w)
    line_h = int(W * 0.095 * scale)
    for line in title_lines:
        draw.text((margin, y), line, font=title_font, fill="white")
        y += line_h

    # Subtitle
    sub_font = get_font(fp, int(W * 0.038 * scale))
    sub_lines = wrap_text(draw, subtitle, sub_font, max_text_w)
    for sl in sub_lines:
        draw.text((margin, y), sl, font=sub_font, fill=(255, 255, 255, 220))
        y += int(W * 0.05 * scale)
    y += int(W * 0.015 * scale)

    # Divider
    draw.line([(margin, y), (margin + int(W * 0.15), y)], fill=(255, 255, 255, 180), width=2)
    y += int(W * 0.035 * scale)

    # Items
    item_font = get_font(fp, int(W * 0.033 * scale), bold=True)
    reason_font = get_font(fp, int(W * 0.028 * scale))
    num_offset = int(W * 0.06 * scale)
    item_max_w = max_text_w - num_offset

    for i, item in enumerate(items):
        parts = item.split("|", 1)
        name = parts[0].strip()
        reason = parts[1].strip() if len(parts) > 1 else ""

        draw.text((margin, y), f"{i+1}.", font=item_font, fill=ac)
        name_lines = wrap_text(draw, name, item_font, item_max_w)
        for nl in name_lines:
            draw.text((margin + num_offset, y), nl, font=item_font, fill="white")
            y += int(W * 0.042 * scale)
        if reason:
            reason_lines = wrap_text(draw, reason, reason_font, item_max_w)
            for rl in reason_lines:
                draw.text((margin + num_offset, y), rl, font=reason_font, fill=(255, 255, 255, 180))
                y += int(W * 0.048 * scale)
        else:
            y += int(W * 0.02 * scale)

    return img


def render_clean(img, title, subtitle, watermark, accent):
    W, H = img.size
    fp = _find_font()
    img = draw_gradient(img, 0.55, 180, 0.7)
    draw = ImageDraw.Draw(img)
    margin = int(W * 0.06)
    ac = tuple(int(c) for c in accent.split(","))

    if watermark:
        draw.text((margin, int(H * 0.03)), watermark, font=get_font(fp, int(W * 0.03)), fill=(255, 255, 255, 200))

    max_text_w = W - 2 * margin
    title_font = get_font(fp, int(W * 0.11), bold=True)
    title_text = title.upper()
    title_lines = wrap_text(draw, title_text, title_font, max_text_w)
    line_h = int(W * 0.12)
    sub_font = get_font(fp, int(W * 0.045))
    sub_h = int(W * 0.065)
    sub_lines = wrap_text(draw, subtitle, sub_font, max_text_w)
    # Calculate total block height and position from bottom up
    total_h = len(title_lines) * line_h + len(sub_lines) * sub_h
    bottom_margin = int(H * 0.06)
    y = H - bottom_margin - total_h
    for line in title_lines:
        draw.text((margin, y), line, font=title_font, fill="white")
        y += line_h
    sub_lines = wrap_text(draw, subtitle, sub_font, max_text_w)
    for sl in sub_lines:
        draw.text((margin, y), sl, font=sub_font, fill=(255, 255, 255, 220))
        y += sub_h

    return img


def render_quote(img, title, subtitle, quote_text, watermark, accent, author=""):
    W, H = img.size
    fp = _find_font()
    img = draw_gradient(img, 0.40, 210, 0.8)
    draw = ImageDraw.Draw(img)
    margin = int(W * 0.06)
    ac = tuple(int(c) for c in accent.split(","))
    max_text_w = W - 2 * margin

    # Watermark
    if watermark:
        draw.text((margin, int(H * 0.03)), watermark, font=get_font(fp, int(W * 0.03)), fill=(255, 255, 255, 200))

    # --- Layout: Title with accent bar, then blockquote below ---
    title_font = get_font(fp, int(W * 0.09), bold=True)
    title_lines = wrap_text(draw, title.upper(), title_font, max_text_w)
    t_line_h = int(W * 0.10)

    quote_font = get_font(fp, int(W * 0.042), italic=True)
    text_x = margin + int(W * 0.04)
    quote_max_w = W - text_x - margin
    quote_lines = wrap_text(draw, quote_text, quote_font, quote_max_w)
    q_line_h = int(W * 0.058)

    # Author line
    author_font = get_font(fp, int(W * 0.035))
    author_h = int(W * 0.055) if author else 0

    # Work backwards from bottom
    bottom_pad = int(H * 0.06)
    quote_block_h = len(quote_lines) * q_line_h + author_h
    quote_y = H - bottom_pad - quote_block_h
    title_block_h = len(title_lines) * t_line_h
    title_y = quote_y - int(W * 0.03) - title_block_h

    # Title with accent bar
    bar_x = margin
    bar_top = title_y
    bar_bottom = title_y + title_block_h
    draw.line([(bar_x, bar_top), (bar_x, bar_bottom)], fill=ac, width=max(3, int(W * 0.005)))

    y = title_y
    for line in title_lines:
        draw.text((text_x, y), line, font=title_font, fill="white")
        y += t_line_h

    # Blockquote below
    y = quote_y
    for line in quote_lines:
        draw.text((margin, y), line, font=quote_font, fill=(255, 255, 255, 220))
        y += q_line_h

    # Author attribution
    if author:
        draw.text((margin, y + int(W * 0.01)), author, font=author_font, fill=ac)

    return img


def main():
    p = argparse.ArgumentParser(description="Instagram photo text overlay")
    p.add_argument("--input", required=True, help="Source image path")
    p.add_argument("--output", required=True, help="Output image path")
    p.add_argument("--title", required=True, help="Main title (e.g. destination name)")
    p.add_argument("--subtitle", default="", help="Subtitle text (omit for no subtitle)")
    p.add_argument("--items", default="[]", help='JSON array of "Name|Reason" strings')
    p.add_argument("--watermark", default="tabiji.ai", help="Top-left watermark text")
    p.add_argument("--accent", default="255,220,150", help="Accent color as R,G,B")
    p.add_argument("--quote", default="", help="Quote text for quote style")
    p.add_argument("--author", default="", help="Quote attribution (e.g. r/JapanTravelTips)")
    p.add_argument("--style", default="list", choices=["list", "clean", "quote"], help="Layout style")
    p.add_argument("--quality", type=int, default=95, help="JPEG quality")
    args = p.parse_args()

    img = Image.open(args.input).convert("RGB")
    img = crop_portrait(img)
    items = json.loads(args.items)

    if args.style == "list":
        img = render_list(img, args.title, args.subtitle, items, args.watermark, args.accent)
    elif args.style == "quote":
        img = render_quote(img, args.title, args.subtitle, args.quote, args.watermark, args.accent, args.author)
    else:
        img = render_clean(img, args.title, args.subtitle, args.watermark, args.accent)

    img.save(args.output, quality=args.quality)
    print(f"Saved: {args.output} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
