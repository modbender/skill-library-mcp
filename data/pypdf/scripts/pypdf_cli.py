#!/usr/bin/env python3
"""PDF operations using pypdf: info, extract-text, extract-pages, split, merge, rotate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def import_pypdf():
    try:
        import pypdf  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'pypdf'. Install it with: pip install pypdf"
        ) from exc
    return pypdf


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_info(args: argparse.Namespace, pypdf) -> int:
    reader = pypdf.PdfReader(args.input)
    meta = reader.metadata or {}
    print(f"Pages : {len(reader.pages)}")
    for key, value in meta.items():
        print(f"{key}: {value}")
    return 0


def cmd_extract_text(args: argparse.Namespace, pypdf) -> int:
    reader = pypdf.PdfReader(args.input)
    pages = args.pages if args.pages is not None else range(len(reader.pages))
    for idx in pages:
        if idx >= len(reader.pages):
            print(f"Warning: page {idx} out of range (total {len(reader.pages)})", file=sys.stderr)
            continue
        text = reader.pages[idx].extract_text() or ""
        print(text)
    return 0


def cmd_extract_pages(args: argparse.Namespace, pypdf) -> int:
    reader = pypdf.PdfReader(args.input)
    writer = pypdf.PdfWriter()
    for idx in args.pages:
        if idx >= len(reader.pages):
            print(f"Warning: page {idx} out of range (total {len(reader.pages)})", file=sys.stderr)
            continue
        writer.add_page(reader.pages[idx])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        writer.write(f)
    print(f"Written {len(writer.pages)} page(s) to {output}")
    return 0


def cmd_split(args: argparse.Namespace, pypdf) -> int:
    reader = pypdf.PdfReader(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(args.input).stem
    for idx, page in enumerate(reader.pages):
        writer = pypdf.PdfWriter()
        writer.add_page(page)
        out_path = output_dir / f"{stem}_page_{idx:04d}.pdf"
        with open(out_path, "wb") as f:
            writer.write(f)
    print(f"Split {len(reader.pages)} page(s) into {output_dir}")
    return 0


def cmd_merge(args: argparse.Namespace, pypdf) -> int:
    writer = pypdf.PdfWriter()
    total = 0
    for path in args.inputs:
        reader = pypdf.PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
            total += 1
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        writer.write(f)
    print(f"Merged {total} page(s) from {len(args.inputs)} file(s) into {output}")
    return 0


def cmd_rotate(args: argparse.Namespace, pypdf) -> int:
    if args.angle not in (90, 180, 270):
        print("Error: --angle must be 90, 180, or 270.", file=sys.stderr)
        return 1
    reader = pypdf.PdfReader(args.input)
    writer = pypdf.PdfWriter()
    target_pages = set(args.pages) if args.pages is not None else None
    for idx, page in enumerate(reader.pages):
        if target_pages is None or idx in target_pages:
            page.rotate(args.angle)
        writer.add_page(page)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        writer.write(f)
    print(f"Written {len(writer.pages)} page(s) to {output}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PDF operations using pypdf.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # info
    p_info = sub.add_parser("info", help="Print page count and metadata.")
    p_info.add_argument("--input", required=True, help="Path to the PDF file.")

    # extract-text
    p_text = sub.add_parser("extract-text", help="Extract text from pages (stdout).")
    p_text.add_argument("--input", required=True, help="Path to the PDF file.")
    p_text.add_argument("--pages", type=int, nargs="+", help="0-indexed page numbers (default: all).")

    # extract-pages
    p_ep = sub.add_parser("extract-pages", help="Extract selected pages into a new PDF.")
    p_ep.add_argument("--input", required=True, help="Path to the source PDF.")
    p_ep.add_argument("--pages", type=int, nargs="+", required=True, help="0-indexed page numbers.")
    p_ep.add_argument("--output", required=True, help="Output PDF path.")

    # split
    p_split = sub.add_parser("split", help="Split each page into a separate PDF.")
    p_split.add_argument("--input", required=True, help="Path to the PDF file.")
    p_split.add_argument("--output-dir", required=True, help="Directory to write page PDFs.")

    # merge
    p_merge = sub.add_parser("merge", help="Merge multiple PDFs into one.")
    p_merge.add_argument("--inputs", nargs="+", required=True, help="Input PDF paths (in order).")
    p_merge.add_argument("--output", required=True, help="Output PDF path.")

    # rotate
    p_rot = sub.add_parser("rotate", help="Rotate pages in a PDF.")
    p_rot.add_argument("--input", required=True, help="Path to the source PDF.")
    p_rot.add_argument("--angle", type=int, required=True, choices=[90, 180, 270], help="Rotation angle.")
    p_rot.add_argument("--pages", type=int, nargs="+", help="0-indexed pages to rotate (default: all).")
    p_rot.add_argument("--output", required=True, help="Output PDF path.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        pypdf = import_pypdf()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    dispatch = {
        "info": cmd_info,
        "extract-text": cmd_extract_text,
        "extract-pages": cmd_extract_pages,
        "split": cmd_split,
        "merge": cmd_merge,
        "rotate": cmd_rotate,
    }

    try:
        return dispatch[args.command](args, pypdf)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
