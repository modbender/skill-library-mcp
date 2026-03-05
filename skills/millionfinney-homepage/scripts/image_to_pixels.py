#!/usr/bin/env python3
"""Rasterize an image/logo into Million Finney pixel payloads.

Usage:
  python3 scripts/image_to_pixels.py \
    --input logo.png \
    --top-left 120,300 \
    --max-width 80 --max-height 60 \
    --title-prefix "Finney Logo" \
    --palette 0x000000 0xFFFFFF 0xFF9500 \
    --dither \
    --skip-hex 0xFFFFFF \
    --json pixels.json --csv pixels.csv

Outputs a JSON list of `{x,y,tokenId,color,title}` rows plus an optional CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from PIL import Image

GRID_MIN = 0
GRID_MAX = 999
PIXEL_PRICE_ETH = 0.001


@dataclass
class Pixel:
    x: int
    y: int
    color: Tuple[int, int, int]

    @property
    def token_id(self) -> int:
        return self.y * 1000 + self.x

    @property
    def color_hex(self) -> str:
        r, g, b = self.color
        return f"0x{r:02X}{g:02X}{b:02X}"


def parse_xy(value: str) -> Tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Coordinate must be formatted as x,y")
    x, y = (int(parts[0]), int(parts[1]))
    return x, y


def clamp_size(img: Image.Image, width: int | None, height: int | None, max_w: int | None, max_h: int | None) -> Image.Image:
    target_w = width or img.width
    target_h = height or img.height

    if max_w and target_w > max_w:
        target_h = round(target_h * (max_w / target_w))
        target_w = max_w
    if max_h and target_h > max_h:
        target_w = round(target_w * (max_h / target_h))
        target_h = max_h

    if width or height or max_w or max_h:
        return img.resize((max(1, target_w), max(1, target_h)), Image.NEAREST)
    return img


def parse_palette(values: Sequence[str]) -> List[Tuple[int, int, int]]:
    palette = []
    for raw in values:
        h = raw.lower().replace("#", "0x")
        if not h.startswith("0x"):
            raise argparse.ArgumentTypeError(f"Palette value '{raw}' must be hex (e.g. 0xFFAA00)")
        n = int(h, 16)
        palette.append(((n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF))
    return palette


def nearest_color(rgb: Tuple[int, int, int], palette: Sequence[Tuple[int, int, int]]) -> Tuple[int, int, int]:
    r, g, b = rgb
    best = palette[0]
    best_dist = 10 ** 9
    for pr, pg, pb in palette:
        dist = (pr - r) ** 2 + (pg - g) ** 2 + (pb - b) ** 2
        if dist < best_dist:
            best_dist = dist
            best = (pr, pg, pb)
    return best


def floyd_steinberg(img: Image.Image, palette: Sequence[Tuple[int, int, int]]) -> Image.Image:
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            old = pixels[x, y][:3]
            new = nearest_color(old, palette)
            pixels[x, y] = (*new, pixels[x, y][3])
            err = tuple(old[i] - new[i] for i in range(3))
            for dx, dy, factor in ((1, 0, 7 / 16), (-1, 1, 3 / 16), (0, 1, 5 / 16), (1, 1, 1 / 16)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    nr, ng, nb, na = pixels[nx, ny]
                    nr = int(max(0, min(255, nr + err[0] * factor)))
                    ng = int(max(0, min(255, ng + err[1] * factor)))
                    nb = int(max(0, min(255, nb + err[2] * factor)))
                    pixels[nx, ny] = (nr, ng, nb, na)
    return img


def rasterize(image_path: Path, args: argparse.Namespace) -> List[Pixel]:
    img = Image.open(image_path).convert("RGBA")
    img = clamp_size(img, args.width, args.height, args.max_width, args.max_height)

    if args.palette:
        palette = parse_palette(args.palette)
        if args.dither:
            img = floyd_steinberg(img.copy(), palette)
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    continue
                nr, ng, nb = nearest_color((r, g, b), palette)
                pixels[x, y] = (nr, ng, nb, a)
    else:
        palette = None

    skip = {c.lower() for c in args.skip_hex} if args.skip_hex else set()
    out: List[Pixel] = []

    for sy in range(img.height):
        for sx in range(img.width):
            r, g, b, a = img.getpixel((sx, sy))
            if a == 0:
                continue
            color_hex = f"0x{r:02X}{g:02X}{b:02X}".lower()
            if color_hex in skip:
                continue

            gx = args.top_left[0] + sx
            gy = args.top_left[1] + sy
            if not (GRID_MIN <= gx <= GRID_MAX and GRID_MIN <= gy <= GRID_MAX):
                raise ValueError(f"Pixel ({gx}, {gy}) falls outside the 0–999 grid")
            out.append(Pixel(gx, gy, (r, g, b)))
    return out


def dump_json(pixels: Sequence[Pixel], path: Path, title_prefix: str | None) -> None:
    payload = []
    for idx, px in enumerate(pixels, start=1):
        title = f"{title_prefix or 'Finney Pixel'} #{idx}"
        payload.append(
            {
                "x": px.x,
                "y": px.y,
                "tokenId": px.token_id,
                "color": px.color_hex,
                "title": title,
            }
        )
    path.write_text(json.dumps(payload, indent=2))


def dump_csv(pixels: Sequence[Pixel], path: Path, title_prefix: str | None) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["tokenId", "x", "y", "color", "title"])
        for idx, px in enumerate(pixels, start=1):
            title = f"{title_prefix or 'Finney Pixel'} #{idx}"
            writer.writerow([px.token_id, px.x, px.y, px.color_hex, title])


def preview(pixels: Sequence[Pixel], width: int, height: int, top_left: Tuple[int, int]) -> None:
    grid = [["·" for _ in range(width)] for _ in range(height)]
    min_x, min_y = top_left
    for px in pixels:
        grid[px.y - min_y][px.x - min_x] = "■"
    print("Preview (■ = colored pixel):")
    for row in grid:
        print("".join(row))


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert images into Million Finney pixel payloads.")
    parser.add_argument("--input", required=True, help="Path to source image (PNG/JPEG/WebP/SVG rasterized)")
    parser.add_argument("--top-left", type=parse_xy, required=True, help="Top-left coordinate 'x,y' on the grid")
    parser.add_argument("--width", type=int, help="Force exact output width")
    parser.add_argument("--height", type=int, help="Force exact output height")
    parser.add_argument("--max-width", type=int, help="Clamp width if image exceeds this value")
    parser.add_argument("--max-height", type=int, help="Clamp height if image exceeds this value")
    parser.add_argument("--palette", nargs="*", help="Restrict colors to the supplied hex list (e.g. 0x000000 0xFFFFFF)")
    parser.add_argument("--dither", action="store_true", help="Apply Floyd–Steinberg dithering when using --palette")
    parser.add_argument("--skip-hex", nargs="*", default=[], help="Hex colors to treat as transparent (e.g. 0xFFFFFF)")
    parser.add_argument("--title-prefix", help="Prefix for generated pixel titles")
    parser.add_argument("--json", type=Path, default=Path("pixels.json"), help="Output JSON path")
    parser.add_argument("--csv", type=Path, help="Optional CSV path")

    args = parser.parse_args()
    args.top_left = args.top_left  # ensure tuple stored

    pixels = rasterize(Path(args.input), args)

    if not pixels:
        raise SystemExit("No opaque pixels detected after filtering; nothing to export")

    dump_json(pixels, args.json, args.title_prefix)
    if args.csv:
        dump_csv(pixels, args.csv, args.title_prefix)

    print(f"Converted {len(pixels)} pixels spanning {len(pixels) / 100:.2f} batches (≤100 each)")
    est_cost = len(pixels) * PIXEL_PRICE_ETH
    print(f"Pixel spend: {len(pixels)} × {PIXEL_PRICE_ETH} ETH = {est_cost:.3f} ETH (before gas)")
    print(f"JSON written to {args.json}")
    if args.csv:
        print(f"CSV written to {args.csv}")

    min_x = min(px.x for px in pixels)
    max_x = max(px.x for px in pixels)
    min_y = min(px.y for px in pixels)
    max_y = max(px.y for px in pixels)
    preview(pixels, max_x - min_x + 1, max_y - min_y + 1, (min_x, min_y))


if __name__ == "__main__":
    main()
