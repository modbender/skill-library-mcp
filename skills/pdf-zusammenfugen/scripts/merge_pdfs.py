#!/usr/bin/env python3
"""Merge multiple PDF files into one output PDF."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def load_backend():
    try:
        from pypdf import PdfReader, PdfWriter  # type: ignore

        return PdfReader, PdfWriter, "pypdf"
    except ImportError:
        try:
            from PyPDF2 import PdfReader, PdfWriter  # type: ignore

            return PdfReader, PdfWriter, "PyPDF2"
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Missing PDF backend. Install with: python3 -m pip install --user pypdf"
            ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge PDF files in the given order."
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path of merged PDF output file.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output if it already exists.",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input PDF files in merge order.",
    )
    return parser.parse_args()


def ensure_input_paths(paths: list[Path]) -> None:
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        if not path.is_file():
            raise FileNotFoundError(f"Input path is not a file: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Input is not a PDF file: {path}")


def merge_pdfs(output: Path, inputs: list[Path], overwrite: bool) -> int:
    PdfReader, PdfWriter, backend = load_backend()

    if output.exists() and not overwrite:
        raise FileExistsError(
            f"Output already exists: {output} (use --overwrite to replace)"
        )

    if not output.parent.exists():
        output.parent.mkdir(parents=True, exist_ok=True)

    ensure_input_paths(inputs)

    writer = PdfWriter()
    page_count = 0

    for src in inputs:
        with src.open("rb") as fh:
            reader = PdfReader(fh)
            is_encrypted = getattr(reader, "is_encrypted", False)
            if is_encrypted:
                try:
                    decrypt_result = reader.decrypt("")
                except Exception as exc:
                    raise ValueError(
                        f"Encrypted PDF cannot be opened without password: {src}"
                    ) from exc
                if not decrypt_result:
                    raise ValueError(
                        f"Encrypted PDF cannot be opened without password: {src}"
                    )

            for page in reader.pages:
                writer.add_page(page)
                page_count += 1

    with output.open("wb") as out_fh:
        writer.write(out_fh)

    print(f"[ok] backend: {backend}")
    print(f"[ok] merged files: {len(inputs)}")
    print(f"[ok] merged pages: {page_count}")
    print(f"[ok] output: {output}")
    return 0


def main() -> int:
    args = parse_args()
    output = Path(args.output).expanduser().resolve()
    inputs = [Path(p).expanduser().resolve() for p in args.inputs]

    try:
        return merge_pdfs(output=output, inputs=inputs, overwrite=args.overwrite)
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
