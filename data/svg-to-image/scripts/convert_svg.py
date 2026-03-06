#!/usr/bin/env python3
"""
Convert SVG to PNG or JPG. Fast raster export for sharing (e.g. Telegram) or print.
"""
import argparse
import sys

try:
    import cairosvg
except ImportError:
    print("Error: cairosvg is required. Install with: pip install cairosvg", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Convert SVG to PNG or JPG.")
    parser.add_argument("input", help="Input SVG file path")
    parser.add_argument("-o", "--output", default="", help="Output path (default: input name with .png or .jpg)")
    parser.add_argument("-f", "--format", choices=["png", "jpg", "jpeg"], default="png", help="Output format (default: png)")
    parser.add_argument("--width", type=float, default=None, help="Output width in pixels (keeps aspect if only one of width/height)")
    parser.add_argument("--height", type=float, default=None, help="Output height in pixels")
    parser.add_argument("--dpi", type=float, default=96, help="Scale for rasterization (default 96)")
    args = parser.parse_args()

    if not args.output:
        base = args.input.rsplit(".", 1)[0] if "." in args.input else args.input
        ext = "jpg" if args.format in ("jpg", "jpeg") else "png"
        args.output = f"{base}.{ext}"

    try:
        if args.format == "png":
            cairosvg.svg2png(
                url=args.input,
                write_to=args.output,
                output_width=args.width,
                output_height=args.height,
                dpi=args.dpi,
            )
        else:
            import io
            from PIL import Image
            buf = io.BytesIO()
            cairosvg.svg2png(
                url=args.input,
                write_to=buf,
                output_width=args.width,
                output_height=args.height,
                dpi=args.dpi,
            )
            buf.seek(0)
            img = Image.open(buf).convert("RGB")
            img.save(args.output, "JPEG", quality=95)
        print(f"Saved: {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
