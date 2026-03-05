#!/usr/bin/env python3
"""
KDP Cover Generator — create-cover.py
Creates a KDP-ready full-wrap cover PDF (front + spine + back + bleed).

The output is a single-page PDF at the exact dimensions KDP requires.
Text overlays are added programmatically (never baked into AI images).

Usage:
  python3 create-cover.py --title "My Book" --author "Jane Doe" --pages 28
  python3 create-cover.py --title "My Book" --author "Jane Doe" --pages 28 \\
      --front-image output/my-book/images/cover.png \\
      --back-text "A heartwarming tale about..." \\
      --trim 8.5x8.5 --paper white-color
  python3 create-cover.py --help
"""

import argparse
import json
import sys
import io
from pathlib import Path

try:
    from reportlab.lib.pagesizes import inch as INCH
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.colors import HexColor, white, black, Color
    from reportlab.lib.utils import ImageReader
    from PIL import Image
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Run: pip install reportlab Pillow")
    sys.exit(1)


# ─── Spine Width Formulas ─────────────────────────────────────────────────────
# Source: KDP Cover Calculator (kdp.amazon.com/en_US/cover-calculator)

SPINE_WIDTH_PER_PAGE = {
    "white-bw":    0.002252,   # White paper, B&W interior
    "cream-bw":    0.002500,   # Cream paper, B&W interior
    "white-color": 0.002347,   # White paper, color interior
}

TRIM_SIZES = {
    "8.5x8.5":  (8.5, 8.5),
    "8.5x11":   (8.5, 11.0),
    "6x9":      (6.0, 9.0),
    "5.5x8.5":  (5.5, 8.5),
    "7x10":     (7.0, 10.0),
}

BLEED = 0.125  # inches — standard KDP bleed


def calc_spine_width(pages: int, paper: str) -> float:
    """Return spine width in inches."""
    rate = SPINE_WIDTH_PER_PAGE.get(paper, SPINE_WIDTH_PER_PAGE["white-bw"])
    return pages * rate


def calc_cover_dimensions(trim_w: float, trim_h: float, pages: int, paper: str):
    """
    Return (total_width_in, total_height_in, spine_width_in, bleed_in).
    All in inches.
    """
    spine = calc_spine_width(pages, paper)
    total_w = trim_w + spine + trim_w + (2 * BLEED)
    total_h = trim_h + (2 * BLEED)
    return total_w, total_h, spine, BLEED


def load_image(path_str: str) -> Image.Image:
    """Load a PIL image from a file path."""
    p = Path(path_str)
    if not p.exists():
        print(f"❌ Image not found: {path_str}")
        sys.exit(1)
    return Image.open(p).convert("RGB")


def make_placeholder_image(label: str, width: int = 1024, height: int = 1024,
                            color: str = "#3A6EA5") -> Image.Image:
    """Create a simple colored placeholder image."""
    from PIL import ImageDraw
    img = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, width - 20, height - 20], outline="#FFFFFF", width=4)
    draw.text((width // 2, height // 2), label[:30], fill="white", anchor="mm")
    return img


def image_to_reader(img: Image.Image) -> ImageReader:
    """Convert PIL Image to ReportLab ImageReader."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def wrap_text(c, text: str, max_width: float, font: str, size: int):
    """Word-wrap text to fit max_width. Returns list of lines."""
    words = text.split()
    lines, current = [], []
    for word in words:
        test = " ".join(current + [word])
        if c.stringWidth(test, font, size) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def create_cover(
    title: str,
    author: str,
    pages: int,
    paper: str = "white-color",
    trim_key: str = "8.5x8.5",
    front_image_path: str = None,
    back_image_path: str = None,
    back_text: str = "",
    spine_color: str = "#2C5F8A",
    title_color: str = "#1A1A2E",
    output_path: str = None,
    subtitle: str = "",
) -> Path:
    """Generate the full-wrap KDP cover PDF."""

    # Dimensions
    trim_w, trim_h = TRIM_SIZES.get(trim_key, (8.5, 8.5))
    total_w_in, total_h_in, spine_in, bleed_in = calc_cover_dimensions(
        trim_w, trim_h, pages, paper
    )

    # Convert to points (1 inch = 72 pt)
    total_w = total_w_in * INCH
    total_h = total_h_in * INCH
    bleed = bleed_in * INCH
    spine_w = spine_in * INCH
    trim_w_pt = trim_w * INCH
    trim_h_pt = trim_h * INCH

    # Coordinate references (from left edge of PDF)
    back_x = bleed                              # Back cover left edge
    spine_x = bleed + trim_w_pt                # Spine left edge
    front_x = spine_x + spine_w                # Front cover left edge
    cover_bottom = bleed                        # Bottom edge of cover area
    cover_top = bleed + trim_h_pt              # Top edge of cover area

    print(f"\n📐 Cover Dimensions")
    print(f"   Trim size   : {trim_w}\" × {trim_h}\"")
    print(f"   Pages       : {pages}")
    print(f"   Paper       : {paper}")
    print(f"   Spine width : {spine_in:.4f}\" ({spine_w:.2f} pt)")
    print(f"   Total size  : {total_w_in:.3f}\" × {total_h_in:.3f}\"")
    print(f"   ({total_w:.1f} × {total_h:.1f} pt)")

    # Output path
    if output_path is None:
        slug = title.lower().replace(" ", "-")[:40]
        output_path = f"cover-{slug}.pdf"
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # ─── Draw PDF ─────────────────────────────────────────────────────────────
    c = pdf_canvas.Canvas(str(out), pagesize=(total_w, total_h))

    # ── Background ────────────────────────────────────────────────────────────
    c.setFillColor(HexColor("#F0F4F8"))
    c.rect(0, 0, total_w, total_h, fill=1, stroke=0)

    # ── Front Cover ───────────────────────────────────────────────────────────
    # Background gradient simulation (solid color)
    c.setFillColor(HexColor("#2C5F8A"))
    c.rect(front_x, cover_bottom, trim_w_pt, trim_h_pt, fill=1, stroke=0)

    # Front cover image (fills most of the front, leaving room for title bar)
    title_bar_h = 1.8 * INCH
    img_area_h = trim_h_pt - title_bar_h - 0.25 * INCH
    img_area_w = trim_w_pt - 0.5 * INCH

    if front_image_path:
        front_img = load_image(front_image_path)
    else:
        front_img = make_placeholder_image("FRONT COVER IMAGE", 1024, 1024)

    c.drawImage(
        image_to_reader(front_img),
        front_x + 0.25 * INCH,
        cover_bottom + title_bar_h,
        img_area_w,
        img_area_h,
        preserveAspectRatio=True,
        anchor="c",
    )

    # Title bar on front cover
    c.setFillColor(HexColor(title_color))
    c.rect(front_x, cover_bottom, trim_w_pt, title_bar_h, fill=1, stroke=0)

    # Title text
    c.setFillColor(white)
    title_font_size = 32 if len(title) <= 25 else (24 if len(title) <= 40 else 18)
    c.setFont("Helvetica-Bold", title_font_size)
    title_lines = wrap_text(c, title, trim_w_pt - 0.5 * INCH, "Helvetica-Bold", title_font_size)
    y = cover_bottom + title_bar_h - 0.4 * INCH
    for line in title_lines:
        c.drawCentredString(front_x + trim_w_pt / 2, y, line)
        y -= (title_font_size + 6) / 72 * INCH

    # Subtitle
    if subtitle:
        c.setFont("Helvetica-Oblique", 14)
        c.setFillColor(HexColor("#CCDDEE"))
        c.drawCentredString(front_x + trim_w_pt / 2, cover_bottom + 0.85 * INCH, subtitle)

    # Author name on front cover
    c.setFont("Helvetica", 16)
    c.setFillColor(HexColor("#AACCEE"))
    c.drawCentredString(front_x + trim_w_pt / 2, cover_bottom + 0.35 * INCH, f"by {author}")

    # ── Back Cover ────────────────────────────────────────────────────────────
    c.setFillColor(HexColor("#1A3A5C"))
    c.rect(back_x, cover_bottom, trim_w_pt, trim_h_pt, fill=1, stroke=0)

    # Back cover image (optional, smaller)
    if back_image_path:
        back_img = load_image(back_image_path)
        c.drawImage(
            image_to_reader(back_img),
            back_x + 0.5 * INCH,
            cover_bottom + trim_h_pt * 0.45,
            trim_w_pt * 0.4,
            trim_h_pt * 0.35,
            preserveAspectRatio=True,
            anchor="c",
        )

    # Back cover title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(back_x + trim_w_pt / 2, cover_bottom + trim_h_pt - 1.0 * INCH, title)

    # Back cover description
    if back_text:
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor("#CCDDEE"))
        desc_lines = wrap_text(c, back_text, trim_w_pt - 1.0 * INCH, "Helvetica", 12)
        y = cover_bottom + trim_h_pt - 1.6 * INCH
        for line in desc_lines:
            c.drawCentredString(back_x + trim_w_pt / 2, y, line)
            y -= 18

    # Author name on back
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(HexColor("#AABBCC"))
    c.drawCentredString(back_x + trim_w_pt / 2, cover_bottom + 2.0 * INCH, f"by {author}")

    # ISBN barcode placeholder (bottom right of back cover)
    # KDP will overlay its own barcode here — leave 2" × 1.5" clear
    barcode_w = 2.0 * INCH
    barcode_h = 1.2 * INCH
    barcode_x = back_x + trim_w_pt - barcode_w - 0.3 * INCH
    barcode_y = cover_bottom + 0.4 * INCH
    c.setFillColor(white)
    c.rect(barcode_x, barcode_y, barcode_w, barcode_h, fill=1, stroke=0)
    c.setFillColor(HexColor("#999999"))
    c.setFont("Helvetica", 7)
    c.drawCentredString(barcode_x + barcode_w / 2, barcode_y + barcode_h / 2 - 4, "ISBN BARCODE")

    # ── Spine ─────────────────────────────────────────────────────────────────
    c.setFillColor(HexColor(spine_color))
    c.rect(spine_x, 0, spine_w, total_h, fill=1, stroke=0)

    # Spine text — only if spine is wide enough (≥ 0.25")
    if spine_in >= 0.25:
        c.saveState()
        c.translate(spine_x + spine_w / 2, total_h / 2)
        c.rotate(90)
        max_spine_text_w = trim_h_pt - 0.5 * INCH
        spine_font_size = min(14, int(spine_w * 72 * 0.6))
        spine_font_size = max(7, spine_font_size)
        c.setFont("Helvetica-Bold", spine_font_size)
        c.setFillColor(white)
        spine_text = f"{title}  ·  {author}"
        if c.stringWidth(spine_text, "Helvetica-Bold", spine_font_size) > max_spine_text_w:
            spine_text = title[:30]
        c.drawCentredString(0, -spine_font_size / 2, spine_text)
        c.restoreState()

    # ── Bleed / Safe Zone Guides (as comments in output, not visible) ─────────
    # Front cover safe zone: front_x + 0.125" from all edges
    # Back cover safe zone: back_x + 0.125" from all edges

    c.save()
    print(f"\n✅ Cover PDF created: {out}")
    print(f"   Upload this file as your KDP cover (Custom Cover > Upload PDF).")
    print(f"   KDP will automatically add the barcode over the white rectangle.")
    return out


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="KDP Cover Generator — create full-wrap cover PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 create-cover.py --title "The Curious Octopus" --author "Jane Doe" --pages 28
  python3 create-cover.py \\
      --title "My Activity Book" --author "Jane Doe" --pages 60 \\
      --trim 8.5x11 --paper white-bw \\
      --front-image output/my-book/images/cover.png \\
      --back-text "50 fun activities for curious kids!" \\
      --output output/my-book/cover.pdf

Paper options:
  white-color  — White paper, color interior (default)
  white-bw     — White paper, B&W interior
  cream-bw     — Cream paper, B&W interior

Spine width formula:
  white-color: pages × 0.002347 inches
  white-bw:    pages × 0.002252 inches
  cream-bw:    pages × 0.002500 inches
""",
    )
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--author", required=True, help="Author name")
    parser.add_argument("--pages", required=True, type=int, help="Interior page count")
    parser.add_argument(
        "--subtitle", default="", help="Optional subtitle text"
    )
    parser.add_argument(
        "--trim",
        default="8.5x8.5",
        choices=list(TRIM_SIZES.keys()),
        help="Trim size (default: 8.5x8.5)",
    )
    parser.add_argument(
        "--paper",
        default="white-color",
        choices=list(SPINE_WIDTH_PER_PAGE.keys()),
        help="Paper type — affects spine width (default: white-color)",
    )
    parser.add_argument(
        "--front-image", metavar="PATH", help="Path to front cover image (PNG/JPG)"
    )
    parser.add_argument(
        "--back-image", metavar="PATH", help="Path to back cover image (PNG/JPG, optional)"
    )
    parser.add_argument(
        "--back-text", default="", help="Back cover description text"
    )
    parser.add_argument(
        "--spine-color", default="#2C5F8A", help="Spine background hex color (default: #2C5F8A)"
    )
    parser.add_argument(
        "--title-color", default="#1A1A2E", help="Title bar hex color (default: #1A1A2E)"
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Output PDF path (default: cover-<slug>.pdf)"
    )
    parser.add_argument(
        "--from-metadata", metavar="PATH",
        help="Load title/author/pages from a metadata.json file (overrides individual flags)"
    )

    args = parser.parse_args()

    # Load from metadata if provided
    title, author, pages, subtitle = args.title, args.author, args.pages, args.subtitle
    if args.from_metadata:
        meta_path = Path(args.from_metadata)
        if not meta_path.exists():
            print(f"❌ Metadata file not found: {meta_path}")
            sys.exit(1)
        with open(meta_path) as f:
            meta = json.load(f)
        title = meta.get("title", title)
        author = meta.get("author", author)
        pages = meta.get("page_count", pages)
        subtitle = meta.get("subtitle", subtitle)
        print(f"✓ Loaded from metadata: {title} by {author}, {pages} pages")

    create_cover(
        title=title,
        author=author,
        pages=pages,
        paper=args.paper,
        trim_key=args.trim,
        front_image_path=args.front_image,
        back_image_path=args.back_image,
        back_text=args.back_text,
        spine_color=args.spine_color,
        title_color=args.title_color,
        output_path=args.output,
        subtitle=subtitle,
    )


if __name__ == "__main__":
    main()
