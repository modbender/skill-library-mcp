#!/usr/bin/env python3
"""
Extract a color palette from an image. Outputs HEX and RGB for each dominant color.
Uses colorgram if available, else a Pillow-based fallback.
"""
import argparse
import sys

try:
    import colorgram
    HAS_COLORGRAM = True
except ImportError:
    HAS_COLORGRAM = False

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def extract_with_colorgram(image_path: str, n: int):
    colors = colorgram.extract(image_path, n)
    return [(c.rgb.r, c.rgb.g, c.rgb.b) for c in colors]


def extract_with_pillow(image_path: str, n: int):
    from collections import Counter
    img = Image.open(image_path).convert("RGB")
    img.thumbnail((150, 150))
    pixels = list(img.getdata())
    # Quantize to reduce distinct colors (e.g. 32 levels per channel)
    def q(c):
        return (c[0] // 32 * 32, c[1] // 32 * 32, c[2] // 32 * 32)
    counted = Counter(q(p) for p in pixels)
    return [c for c, _ in counted.most_common(n)]


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return "#{:02x}{:02x}{:02x}".format(r, g, b).upper()


def main():
    parser = argparse.ArgumentParser(description="Extract color palette from an image.")
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("-n", "--num-colors", type=int, default=5, help="Number of colors (default 5)")
    parser.add_argument("--output", default="", help="Optional: save swatch PNG to this path")
    args = parser.parse_args()

    if args.num_colors < 1 or args.num_colors > 20:
        print("Error: --num-colors must be between 1 and 20", file=sys.stderr)
        sys.exit(1)

    try:
        if HAS_COLORGRAM:
            colors = extract_with_colorgram(args.image, args.num_colors)
        else:
            colors = extract_with_pillow(args.image, args.num_colors)
    except Exception as e:
        print(f"Error reading image: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Palette ({len(colors)} colors) from {args.image}")
    print("-" * 40)
    for i, (r, g, b) in enumerate(colors, 1):
        hex_val = rgb_to_hex(r, g, b)
        print(f"  {i}. {hex_val}  RGB({r}, {g}, {b})")

    if args.output:
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            fig, ax = plt.subplots(1, len(colors), figsize=(2 * len(colors), 2))
            if len(colors) == 1:
                ax = [ax]
            for i, (r, g, b) in enumerate(colors):
                ax[i].add_patch(mpatches.Rectangle((0, 0), 1, 1, facecolor=(r/255, g/255, b/255)))
                ax[i].set_title(rgb_to_hex(r, g, b), fontsize=10)
                ax[i].set_xlim(0, 1)
                ax[i].set_ylim(0, 1)
                ax[i].axis("off")
            plt.tight_layout()
            plt.savefig(args.output)
            print(f"Swatch saved to {args.output}")
        except Exception as e:
            print(f"Could not save swatch: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
