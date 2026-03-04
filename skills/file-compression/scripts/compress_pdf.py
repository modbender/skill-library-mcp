#!/usr/bin/env python3
"""Compress PDF files using Ghostscript or pikepdf."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


GS_PRESETS = {
    "screen": "/screen",
    "ebook": "/ebook",
    "printer": "/printer",
    "prepress": "/prepress",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compress a PDF file and report size reduction."
    )
    parser.add_argument("input", type=Path, help="Path to source PDF")
    parser.add_argument("output", type=Path, help="Path to output PDF")
    parser.add_argument(
        "--preset",
        choices=sorted(GS_PRESETS.keys()),
        default="ebook",
        help="Compression preset (default: ebook)",
    )
    parser.add_argument(
        "--strategy",
        choices=["auto", "ghostscript", "pikepdf"],
        default="auto",
        help="Compression backend (default: auto)",
    )
    parser.add_argument(
        "--remove-metadata",
        action="store_true",
        help="Remove document metadata when using pikepdf",
    )
    parser.add_argument(
        "--no-linearize",
        action="store_true",
        help="Disable linearized output for web fast-start",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting output path if it already exists",
    )
    return parser.parse_args()


def bytes_to_human(value: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{value} B"


def run_ghostscript(input_pdf: Path, output_pdf: Path, preset: str) -> None:
    gs_bin = shutil.which("gs")
    if not gs_bin:
        raise RuntimeError("Ghostscript not found in PATH")

    cmd = [
        gs_bin,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.6",
        f"-dPDFSETTINGS={GS_PRESETS[preset]}",
        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        f"-sOutputFile={output_pdf}",
        str(input_pdf),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip() or "unknown error"
        raise RuntimeError(f"Ghostscript failed: {stderr}")


def run_pikepdf(
    input_pdf: Path,
    output_pdf: Path,
    remove_metadata: bool,
    linearize: bool,
) -> None:
    try:
        import pikepdf
    except ImportError as exc:
        raise RuntimeError(
            "pikepdf is not installed. Install with: pip install pikepdf"
        ) from exc

    with pikepdf.open(input_pdf) as pdf:
        if remove_metadata:
            pdf.docinfo.clear()
        pdf.remove_unreferenced_resources()
        pdf.save(
            output_pdf,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            recompress_flate=True,
            linearize=linearize,
        )


def validate_paths(input_pdf: Path, output_pdf: Path, overwrite: bool) -> None:
    if not input_pdf.exists():
        raise FileNotFoundError(f"Input file not found: {input_pdf}")
    if input_pdf.suffix.lower() != ".pdf":
        raise ValueError(f"Input must be a .pdf file: {input_pdf}")
    if output_pdf.exists() and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_pdf}. Use --overwrite to replace it."
        )
    if input_pdf.resolve() == output_pdf.resolve():
        raise ValueError("Input and output paths must be different")


def compress(args: argparse.Namespace) -> tuple[str, int, int, Path]:
    input_pdf = args.input.expanduser().resolve()
    output_pdf = args.output.expanduser().resolve()
    validate_paths(input_pdf, output_pdf, args.overwrite)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix="pdf-compress-"))
    tmp_output = tmp_dir / output_pdf.name

    linearize = not args.no_linearize
    strategy = args.strategy

    try:
        if strategy == "ghostscript":
            run_ghostscript(input_pdf, tmp_output, args.preset)
            chosen = "ghostscript"
        elif strategy == "pikepdf":
            run_pikepdf(input_pdf, tmp_output, args.remove_metadata, linearize)
            chosen = "pikepdf"
        else:
            try:
                run_ghostscript(input_pdf, tmp_output, args.preset)
                chosen = "ghostscript"
            except Exception:
                run_pikepdf(input_pdf, tmp_output, args.remove_metadata, linearize)
                chosen = "pikepdf"

        before = input_pdf.stat().st_size
        after = tmp_output.stat().st_size
        shutil.move(str(tmp_output), str(output_pdf))
        return chosen, before, after, output_pdf
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main() -> int:
    args = parse_args()
    try:
        backend, before, after, output_path = compress(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    saved = before - after
    ratio = (saved / before * 100) if before else 0
    print(f"Backend: {backend}")
    print(f"Output path: {output_path}")
    print(f"Input size:  {bytes_to_human(before)}")
    print(f"Output size: {bytes_to_human(after)}")
    print(f"Saved:       {bytes_to_human(saved)} ({ratio:.2f}%)")
    print(f"From/To:     from {bytes_to_human(before)} to {bytes_to_human(after)}")
    if after >= before:
        print(
            "Warning: output is not smaller than input. Try another preset/backend.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
