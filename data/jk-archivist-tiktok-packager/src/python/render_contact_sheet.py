"""Render a contact sheet image for 6 generated slides."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ModuleNotFoundError:
    print(
        "Missing dependency: Pillow. Install with: python3 -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build contact sheet for 6 slide PNG files.")
    parser.add_argument("--slides-dir", required=True, help="Directory with slide_01.png..slide_06.png")
    parser.add_argument("--out", required=True, help="Output contact sheet PNG path")
    return parser.parse_args()


def load_slides(slides_dir: Path) -> list[Image.Image]:
    images: list[Image.Image] = []
    for idx in range(1, 7):
        path = slides_dir / f"slide_{idx:02d}.png"
        if not path.exists():
            fail(f"Missing slide for contact sheet: {path}")
        images.append(Image.open(path).convert("RGB"))
    return images


def main() -> None:
    args = parse_args()
    slides_dir = Path(args.slides_dir)
    out_path = Path(args.out)

    images = load_slides(slides_dir)

    thumb_w = 341
    thumb_h = 512
    gap = 16
    cols = 3
    rows = 2
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (20, 20, 28))
    draw = ImageDraw.Draw(sheet)

    for idx, img in enumerate(images):
        r = idx // cols
        c = idx % cols
        x = gap + c * (thumb_w + gap)
        y = gap + r * (thumb_h + gap)
        thumb = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x, y))
        draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=(90, 90, 110), width=2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, format="PNG")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
