#!/usr/bin/env python3
"""PDF rendering and image extraction using pymupdf (fitz): info, export-images, extract-images."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def import_fitz():
    try:
        import fitz  # type: ignore  # pymupdf
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'pymupdf'. Install it with: pip install pymupdf"
        ) from exc
    return fitz


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_info(args: argparse.Namespace, fitz) -> int:
    doc = fitz.open(args.input)
    print(f"Pages  : {len(doc)}")
    meta = doc.metadata or {}
    for key, value in meta.items():
        if value:
            print(f"{key}: {value}")
    for idx, page in enumerate(doc):
        r = page.rect
        print(f"  page {idx}: {r.width:.1f} x {r.height:.1f} pt")
    return 0


def cmd_export_images(args: argparse.Namespace, fitz) -> int:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(args.input).stem
    fmt = args.format.lower()

    doc = fitz.open(args.input)
    target_pages = set(args.pages) if args.pages is not None else range(len(doc))
    written = 0
    for idx in target_pages:
        if idx >= len(doc):
            print(f"Warning: page {idx} out of range (total {len(doc)})", file=sys.stderr)
            continue
        page = doc[idx]
        mat = fitz.Matrix(args.dpi / 72, args.dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_path = output_dir / f"{stem}_page_{idx:04d}.{fmt}"
        pix.save(str(out_path))
        written += 1

    print(f"Exported {written} page(s) as {fmt.upper()} to {output_dir}")
    return 0


def cmd_extract_images(args: argparse.Namespace, fitz) -> int:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(args.input).stem

    doc = fitz.open(args.input)
    target_pages = set(args.pages) if args.pages is not None else range(len(doc))
    written = 0
    for page_idx in target_pages:
        if page_idx >= len(doc):
            print(f"Warning: page {page_idx} out of range (total {len(doc)})", file=sys.stderr)
            continue
        page = doc[page_idx]
        for img_idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            ext = base_image["ext"]
            image_bytes = base_image["image"]
            out_path = output_dir / f"{stem}_page_{page_idx:04d}_img_{img_idx:04d}.{ext}"
            out_path.write_bytes(image_bytes)
            written += 1

    print(f"Extracted {written} image(s) to {output_dir}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PDF rendering and image extraction using pymupdf.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # info
    p_info = sub.add_parser("info", help="Print page count, dimensions, and metadata.")
    p_info.add_argument("--input", required=True, help="Path to the PDF file.")

    # export-images
    p_exp = sub.add_parser("export-images", help="Render pages to image files.")
    p_exp.add_argument("--input", required=True, help="Path to the PDF file.")
    p_exp.add_argument("--output-dir", required=True, help="Directory to write image files.")
    p_exp.add_argument("--format", default="png", choices=["png", "jpg", "ppm"], help="Image format (default: png).")
    p_exp.add_argument("--dpi", type=int, default=150, help="Resolution in DPI (default: 150).")
    p_exp.add_argument("--pages", type=int, nargs="+", help="0-indexed page numbers (default: all).")

    # extract-images
    p_ext = sub.add_parser("extract-images", help="Extract images embedded inside the PDF.")
    p_ext.add_argument("--input", required=True, help="Path to the PDF file.")
    p_ext.add_argument("--output-dir", required=True, help="Directory to write extracted images.")
    p_ext.add_argument("--pages", type=int, nargs="+", help="0-indexed page numbers (default: all).")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        fitz = import_fitz()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    dispatch = {
        "info": cmd_info,
        "export-images": cmd_export_images,
        "extract-images": cmd_extract_images,
    }

    try:
        return dispatch[args.command](args, fitz)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
