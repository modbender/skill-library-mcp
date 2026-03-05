#!/usr/bin/env python3
"""
Larry — Text Overlay
Legt Hook-Text + Slide-Texte auf die Bilder (Pillow).
Style: Weißer Text, halbtransparenter schwarzer Hintergrund unten.
"""
from pathlib import Path

def add_overlays(image_paths: list, concept: dict) -> list:
    """Fügt Text-Overlays zu allen Slides hinzu"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("⚠️  Pillow fehlt. Install: pip3 install pillow")
        return image_paths

    slides = concept.get("slides", [])
    output_paths = []

    for i, (img_path, slide) in enumerate(zip(image_paths, slides)):
        text = slide.get("text", "")
        out_path = img_path.replace(".png", "_overlay.png")

        try:
            img = Image.open(img_path).convert("RGBA")
            img = _add_text_overlay(img, text, is_hook=(i == 0))
            img.convert("RGB").save(out_path, "JPEG", quality=90)
            output_paths.append(out_path)
        except Exception as e:
            print(f"  ⚠️  Overlay Slide {i+1}: {e}")
            output_paths.append(img_path)

    return output_paths

def _add_text_overlay(img, text: str, is_hook: bool = False):
    from PIL import Image, ImageDraw, ImageFont
    import textwrap

    W, H = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Font-Größe
    font_size = 80 if is_hook else 60
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        font_bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font

    # Text umbrechen
    max_chars = 22 if is_hook else 28
    lines = textwrap.wrap(text, width=max_chars)

    # Text-Block Höhe berechnen
    line_height = font_size + 12
    total_height = len(lines) * line_height + 60
    bg_y1 = H - total_height - 80
    bg_y2 = H - 60

    # Halbtransparenter Hintergrund
    draw.rectangle([(0, bg_y1 - 20), (W, bg_y2 + 20)], fill=(0, 0, 0, 160))

    # Text zeichnen
    y = bg_y1 + 10
    for line in lines:
        # Schatten
        draw.text((W // 2 + 2, y + 2), line, font=font, fill=(0, 0, 0, 200), anchor="mt")
        # Text
        draw.text((W // 2, y), line, font=font_bold, fill=(255, 255, 255, 255), anchor="mt")
        y += line_height

    # Bild + Overlay zusammenführen
    result = Image.alpha_composite(img, overlay)
    return result
