#!/usr/bin/env python3
"""
Convert DXF to PNG, JPG, or SVG. Uses ezdxf drawing add-on (Matplotlib backend for raster, SVGBackend for vector).
Useful for sharing CAD/map DXF in chat (e.g. Telegram) or further editing.
"""
import argparse
import sys

try:
    import ezdxf
    from ezdxf.addons.drawing import RenderContext, Frontend, config
    from ezdxf.addons.drawing import layout
except ImportError as e:
    print(f"Error: {e}. Install ezdxf.", file=sys.stderr)
    sys.exit(1)


def export_svg(doc, output_path: str, margin_mm: float = 2):
    """Render modelspace to SVG via ezdxf SVGBackend."""
    from ezdxf.addons.drawing import svg
    msp = doc.modelspace()
    cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE)
    ctx = RenderContext(doc)
    backend = svg.SVGBackend()
    frontend = Frontend(ctx, backend, config=cfg)
    frontend.draw_layout(msp)
    page = layout.Page(0, 0, layout.Units.mm, margins=layout.Margins.all(margin_mm))
    svg_string = backend.get_string(page)
    with open(output_path, "wt", encoding="utf-8") as f:
        f.write(svg_string)


def main():
    parser = argparse.ArgumentParser(description="Convert DXF to PNG, JPG, or SVG.")
    parser.add_argument("input", help="Input DXF file path")
    parser.add_argument("-o", "--output", default="", help="Output path (default: input name with .png/.jpg/.svg)")
    parser.add_argument("-f", "--format", choices=["png", "jpg", "jpeg", "svg"], default="png", help="Output format (default: png)")
    parser.add_argument("--width", type=int, default=None, help="Output width in pixels (PNG/JPG only; keeps aspect if only one of width/height)")
    parser.add_argument("--height", type=int, default=None, help="Output height in pixels (PNG/JPG only)")
    parser.add_argument("--dpi", type=float, default=150, help="DPI for PNG/JPG rasterization (default 150)")
    parser.add_argument("--margin", type=float, default=2, help="Margin in mm for SVG (default 2)")
    args = parser.parse_args()

    if not args.output:
        base = args.input.rsplit(".", 1)[0] if "." in args.input else args.input
        if args.format == "svg":
            ext = "svg"
        elif args.format in ("jpg", "jpeg"):
            ext = "jpg"
        else:
            ext = "png"
        args.output = f"{base}.{ext}"

    try:
        doc = ezdxf.readfile(args.input)
    except Exception as e:
        print(f"Error reading DXF: {e}", file=sys.stderr)
        sys.exit(1)

    msp = doc.modelspace()
    if len(list(msp)) == 0:
        print("Warning: modelspace is empty; output will be blank.", file=sys.stderr)

    if args.format == "svg":
        try:
            export_svg(doc, args.output, margin_mm=args.margin)
            print(f"Saved: {args.output}")
        except Exception as e:
            print(f"Error writing SVG: {e}", file=sys.stderr)
            sys.exit(1)
        return 0

    try:
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as e:
        print(f"Error: matplotlib required for PNG/JPG. {e}", file=sys.stderr)
        sys.exit(1)

    cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE)
    ctx = RenderContext(doc)
    fig = plt.figure(dpi=args.dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.margins(0)
    backend = MatplotlibBackend(ax)
    frontend = Frontend(ctx, backend, config=cfg)
    frontend.draw_layout(msp, finalize=True)

    if args.width is not None or args.height is not None:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        w_data = xmax - xmin or 1
        h_data = ymax - ymin or 1
        aspect = h_data / w_data
        dpi = fig.dpi
        if args.width is not None and args.height is not None:
            fig.set_size_inches(args.width / dpi, args.height / dpi)
        elif args.width is not None:
            fig.set_size_inches(args.width / dpi, (args.width * aspect) / dpi)
        else:
            fig.set_size_inches((args.height / aspect) / dpi, args.height / dpi)

    try:
        if args.format == "png":
            fig.savefig(args.output, dpi=args.dpi, bbox_inches="tight", pad_inches=0.05)
        else:
            import io
            from PIL import Image
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=args.dpi, bbox_inches="tight", pad_inches=0.05)
            plt.close(fig)
            buf.seek(0)
            img = Image.open(buf).convert("RGB")
            img.save(args.output, "JPEG", quality=95)
            print(f"Saved: {args.output}")
            return 0
        plt.close(fig)
        print(f"Saved: {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
