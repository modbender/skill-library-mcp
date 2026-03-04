"""Deterministic Pillow renderer for 6 TikTok intro slides.

Usage:
  python3 scripts/render_slides_pillow.py --spec <path> --out <dir> --font <ttf_path>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError:
    print(
        "Missing dependency: Pillow. Install with: python3 -m pip install pillow",
        file=sys.stderr,
    )
    sys.exit(1)


WIDTH = 1024
HEIGHT = 1536
DEFAULT_STYLE: Dict[str, object] = {
    "safe_margins": {"left": 90, "right": 90, "top": 180, "bottom_reserved": 260},
    "background": {"base": "#2A124A", "gradient_strength": 1.0, "texture_density": 0.06},
    "text": {"color": "#FFFFFF", "shadow_color": "#000000", "min_size": 40, "max_size": 70},
}
SHADOW_OFFSETS = ((3, 3), (2, 2), (4, 4))
LINE_SPACING_RATIO = 0.22


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render deterministic 6-slide TikTok intro deck as PNG files."
    )
    parser.add_argument("--spec", required=True, help="Path to JSON spec with 6 slides")
    parser.add_argument("--out", required=True, help="Output directory for PNG slides")
    parser.add_argument("--font", required=True, help="Path to .ttf font file")
    return parser.parse_args()


def fail(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def load_spec_document(spec_path: Path) -> Dict[str, object]:
    if not spec_path.exists():
        fail(f"Spec file not found: {spec_path}")
    try:
        document = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Spec file is not valid JSON: {exc}")
    except OSError as exc:
        fail(f"Could not read spec file: {exc}")
    if not isinstance(document, dict):
        fail("Spec JSON root must be an object.")
    return document


def load_spec(spec_path: Path) -> List[str]:
    raw = load_spec_document(spec_path)
    slides = raw.get("slides")
    if not isinstance(slides, list):
        fail("Spec must contain a 'slides' list.")
    if len(slides) != 6:
        fail(f"Spec must contain exactly 6 slides. Got: {len(slides)}")
    if not all(isinstance(item, str) and item.strip() for item in slides):
        fail("All slide entries must be non-empty strings.")
    return slides


def parse_hex_color(value: str, alpha: int | None = None) -> Tuple[int, int, int] | Tuple[int, int, int, int]:
    clean = value.strip().lstrip("#")
    if len(clean) != 6:
        fail(f"Invalid color value: {value}")
    rgb = tuple(int(clean[i : i + 2], 16) for i in (0, 2, 4))
    if alpha is None:
        return rgb
    return (rgb[0], rgb[1], rgb[2], alpha)


def merge_style(raw_style: Dict[str, object] | None) -> Dict[str, object]:
    merged = json.loads(json.dumps(DEFAULT_STYLE))
    if not isinstance(raw_style, dict):
        return merged
    for section in ("safe_margins", "background", "text"):
        if isinstance(raw_style.get(section), dict):
            merged[section].update(raw_style[section])
    return merged


def validate_font(font_path: Path) -> None:
    if not font_path.exists():
        fail(f"Font file not found: {font_path}")
    if not font_path.is_file():
        fail(f"Font path is not a file: {font_path}")


def build_background(slide_idx: int, style: Dict[str, object]) -> Image.Image:
    base_color = parse_hex_color(style["background"]["base"])
    gradient_strength = float(style["background"]["gradient_strength"])
    texture_density = float(style["background"]["texture_density"])

    image = Image.new("RGB", (WIDTH, HEIGHT), base_color)
    draw = ImageDraw.Draw(image)

    for y in range(HEIGHT):
        blend = y / float(HEIGHT - 1)
        delta_r = int(12 * blend * gradient_strength)
        delta_g = int(10 * blend * gradient_strength)
        delta_b = int(22 * blend * gradient_strength)
        accent = slide_idx * 2
        color = (
            min(255, base_color[0] + delta_r + accent),
            min(255, base_color[1] + delta_g),
            min(255, base_color[2] + delta_b + accent),
        )
        draw.line([(0, y), (WIDTH, y)], fill=color)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    px = overlay.load()
    seed = (slide_idx + 1) * 131
    for y in range(0, HEIGHT, 4):
        for x in range(0, WIDTH, 4):
            value = (x * 17 + y * 31 + seed * 13) % 100
            if value < int(texture_density * 100):
                alpha = 10 + (value % 5)
                px[x, y] = (255, 255, 255, alpha)

    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    return image


def wrap_text(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_text_width: int
) -> List[str]:
    words = text.split()
    if not words:
        return [""]

    lines: List[str] = []
    current = words[0]

    for word in words[1:]:
        candidate = f"{current} {word}"
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if width <= max_text_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)

    final_lines: List[str] = []
    for line in lines:
        if draw.textbbox((0, 0), line, font=font)[2] <= max_text_width:
            final_lines.append(line)
            continue

        chunk = ""
        for ch in line:
            candidate = f"{chunk}{ch}"
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_text_width or not chunk:
                chunk = candidate
            else:
                final_lines.append(chunk)
                chunk = ch
        if chunk:
            final_lines.append(chunk)
    return final_lines


def measure_block(
    draw: ImageDraw.ImageDraw, lines: List[str], font: ImageFont.FreeTypeFont
) -> Tuple[int, int, int]:
    line_heights: List[int] = []
    max_width = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        max_width = max(max_width, width)
        line_heights.append(height)

    spacing = max(10, int(font.size * LINE_SPACING_RATIO))
    total_height = sum(line_heights) + spacing * (len(lines) - 1)
    return max_width, total_height, spacing


def layout_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: Path,
    max_text_width: int,
    safe_top: int,
    safe_text_height: int,
    safe_bottom_reserved: int,
    min_font_size: int,
    max_font_size: int,
) -> Tuple[ImageFont.FreeTypeFont, List[str], int, int]:
    for font_size in range(max_font_size, min_font_size - 1, -2):
        font = ImageFont.truetype(str(font_path), size=font_size)
        lines = wrap_text(draw, text, font, max_text_width)
        block_width, block_height, spacing = measure_block(draw, lines, font)
        if block_width <= max_text_width and block_height <= safe_text_height:
            y = safe_top + (safe_text_height - block_height) // 2
            y = max(safe_top, y)
            max_y = HEIGHT - safe_bottom_reserved - block_height
            y = min(y, max_y)
            return font, lines, y, spacing

    fail(
        "Could not fit text within safe margins. "
        "Try shorter slide copy or a font with narrower glyphs."
    )
    raise RuntimeError("Unreachable")


def draw_slide_text(image: Image.Image, text: str, font_path: Path, style: Dict[str, object]) -> None:
    safe_left = int(style["safe_margins"]["left"])
    safe_right = int(style["safe_margins"]["right"])
    safe_top = int(style["safe_margins"]["top"])
    safe_bottom_reserved = int(style["safe_margins"]["bottom_reserved"])
    max_text_width = WIDTH - safe_left - safe_right
    safe_text_height = HEIGHT - safe_top - safe_bottom_reserved
    text_color = parse_hex_color(style["text"]["color"])
    shadow_color = parse_hex_color(style["text"]["shadow_color"], alpha=140)
    min_font_size = int(style["text"]["min_size"])
    max_font_size = int(style["text"]["max_size"])

    draw = ImageDraw.Draw(image, "RGBA")
    font, lines, y, spacing = layout_text(
        draw,
        text,
        font_path,
        max_text_width,
        safe_top,
        safe_text_height,
        safe_bottom_reserved,
        min_font_size,
        max_font_size,
    )

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = safe_left + (max_text_width - line_w) // 2

        for dx, dy in SHADOW_OFFSETS:
            draw.text((x + dx, y + dy), line, font=font, fill=shadow_color)
        draw.text((x, y), line, font=font, fill=text_color)
        y += line_h + spacing


def render_slides(slides: List[str], out_dir: Path, font_path: Path, style: Dict[str, object]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    checksums: Dict[str, str] = {}
    for idx, slide_text in enumerate(slides, start=1):
        image = build_background(idx, style)
        draw_slide_text(image, slide_text, font_path, style)
        out_path = out_dir / f"slide_{idx:02d}.png"
        image.save(out_path, format="PNG", compress_level=9, optimize=False)
        checksums[out_path.name] = hashlib.sha256(out_path.read_bytes()).hexdigest()
        print(f"Wrote {out_path}")
    metadata_path = out_dir.parent / "_render_metadata.json"
    metadata = {
        "font_path": str(font_path),
        "font_sha256": hashlib.sha256(font_path.read_bytes()).hexdigest(),
        "style": style,
        "checksums": checksums,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    spec_path = Path(args.spec)
    out_dir = Path(args.out)
    font_path = Path(args.font)

    document = load_spec_document(spec_path)
    slides = load_spec(spec_path)
    style = merge_style(document.get("style"))
    validate_font(font_path)
    render_slides(slides, out_dir, font_path, style)


if __name__ == "__main__":
    main()
