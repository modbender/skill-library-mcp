#!/usr/bin/env python3
"""Compress image files with Pillow and Node.js fallback."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SUPPORTED = {"jpg", "jpeg", "png", "webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compress an image and report size reduction."
    )
    parser.add_argument("input", type=Path, help="Path to source image")
    parser.add_argument("output", type=Path, help="Path to output image")
    parser.add_argument(
        "--quality",
        type=int,
        default=75,
        help="Output quality for lossy formats (default: 75)",
    )
    parser.add_argument("--max-width", type=int, help="Resize max width")
    parser.add_argument("--max-height", type=int, help="Resize max height")
    parser.add_argument(
        "--format",
        choices=["keep", "jpeg", "png", "webp"],
        default="keep",
        help="Output format (default: keep input format)",
    )
    parser.add_argument(
        "--strategy",
        choices=["auto", "pillow", "node"],
        default="auto",
        help="Compression backend (default: auto)",
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


def validate_paths(input_path: Path, output_path: Path, overwrite: bool) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use --overwrite to replace it."
        )
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output paths must be different")

    in_ext = input_path.suffix.lower().lstrip(".")
    if in_ext not in SUPPORTED:
        raise ValueError(f"Unsupported input format: .{in_ext}")


def output_format(input_path: Path, requested: str) -> str:
    if requested != "keep":
        return requested
    ext = input_path.suffix.lower().lstrip(".")
    return "jpeg" if ext == "jpg" else ext


def run_pillow(
    input_path: Path,
    output_path: Path,
    quality: int,
    fmt: str,
    max_width: int | None,
    max_height: int | None,
) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow not installed. Install with: pip install pillow") from exc

    save_format = "JPEG" if fmt == "jpeg" else fmt.upper()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(input_path) as img:
        if max_width or max_height:
            target = (max_width or img.width, max_height or img.height)
            img.thumbnail(target, Image.Resampling.LANCZOS)

        params: dict[str, object] = {"optimize": True}
        if save_format in {"JPEG", "WEBP"}:
            params["quality"] = max(1, min(100, quality))
        if save_format == "PNG":
            params["compress_level"] = 9
        if save_format == "JPEG" and img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        img.save(output_path, format=save_format, **params)


def run_node_backend(
    input_path: Path,
    output_path: Path,
    quality: int,
    fmt: str,
    max_width: int | None,
    max_height: int | None,
) -> None:
    node_bin = shutil.which("node")
    if not node_bin:
        raise RuntimeError("Node.js not found in PATH")

    script_path = Path(__file__).resolve().parent / "compress_image_node.mjs"
    cmd = [
        node_bin,
        str(script_path),
        str(input_path),
        str(output_path),
        "--quality",
        str(quality),
        "--format",
        fmt,
    ]
    if max_width:
        cmd += ["--max-width", str(max_width)]
    if max_height:
        cmd += ["--max-height", str(max_height)]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip() or "unknown error"
        raise RuntimeError(f"Node backend failed: {stderr}")


def compress(args: argparse.Namespace) -> tuple[str, int, int, Path]:
    input_path = args.input.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    validate_paths(input_path, output_path, args.overwrite)
    fmt = output_format(input_path, args.format)

    tmp_dir = Path(tempfile.mkdtemp(prefix="img-compress-"))
    tmp_output = tmp_dir / output_path.name
    try:
        chosen = args.strategy
        if chosen == "pillow":
            run_pillow(
                input_path, tmp_output, args.quality, fmt, args.max_width, args.max_height
            )
            backend = "pillow"
        elif chosen == "node":
            run_node_backend(
                input_path, tmp_output, args.quality, fmt, args.max_width, args.max_height
            )
            backend = "node-sharp"
        else:
            try:
                run_pillow(
                    input_path,
                    tmp_output,
                    args.quality,
                    fmt,
                    args.max_width,
                    args.max_height,
                )
                backend = "pillow"
            except Exception:
                run_node_backend(
                    input_path,
                    tmp_output,
                    args.quality,
                    fmt,
                    args.max_width,
                    args.max_height,
                )
                backend = "node-sharp"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        before = input_path.stat().st_size
        after = tmp_output.stat().st_size
        shutil.move(str(tmp_output), str(output_path))
        return backend, before, after, output_path
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
            "Warning: output is not smaller than input. Try another quality/format/backend.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
