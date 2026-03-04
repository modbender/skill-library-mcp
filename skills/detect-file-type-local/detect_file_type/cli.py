"""CLI entry point for detect-file-type."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import List

from magika import Magika

from detect_file_type.formatter import (
    format_human,
    format_json,
    format_mime,
    result_to_dict,
)

STDIN_HEAD_MAX_BYTES = 1_048_576  # 1 MB (head mode only)
STDIN_SPOOL_CHUNK_BYTES = 65_536


def positive_int(value: str) -> int:
    """Argparse type for strictly positive integers."""
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be > 0")
    return parsed


def collect_paths(args_paths: List[str], recursive: bool) -> List[str]:
    """Expand directories if --recursive, otherwise return paths as-is."""
    expanded = []
    for p in args_paths:
        if p == "-":
            expanded.append("-")
            continue
        path = Path(p)
        if recursive and path.is_dir():
            for root, _dirs, files in os.walk(path):
                for f in sorted(files):
                    expanded.append(os.path.join(root, f))
        else:
            expanded.append(p)
    return expanded


def identify_stdin_spool(magika_instance: Magika) -> dict:
    """Identify stdin by spooling to a temp file, then using identify_path."""
    fd, temp_path = tempfile.mkstemp(prefix="detect-file-type-stdin-", suffix=".bin")
    try:
        with os.fdopen(fd, "wb") as tmp:
            while True:
                chunk = sys.stdin.buffer.read(STDIN_SPOOL_CHUNK_BYTES)
                if not chunk:
                    break
                tmp.write(chunk)
        result = magika_instance.identify_path(Path(temp_path))
        return result_to_dict("-", result)
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass


def identify_stdin_head(magika_instance: Magika, max_bytes: int) -> tuple[dict, bool]:
    """Identify stdin by reading the first max_bytes bytes only."""
    data = sys.stdin.buffer.read(max_bytes)
    result = magika_instance.identify_bytes(data)
    return result_to_dict("-", result), len(data) == max_bytes


def detect_files(
    magika_instance: Magika,
    paths: List[str],
    stdin_mode: str,
    stdin_max_bytes: int,
) -> tuple:
    """Detect file types. Returns (results_list, had_errors)."""
    results = []
    had_errors = False

    # Separate stdin from file paths while preserving original indices
    file_entries = [(i, p) for i, p in enumerate(paths) if p != "-"]
    stdin_indices = [i for i, p in enumerate(paths) if p == "-"]

    # Handle stdin (single stream only)
    if len(stdin_indices) > 1:
        print("error: multiple stdin inputs are not supported; use '-' only once", file=sys.stderr)
        had_errors = True
    elif len(stdin_indices) == 1:
        idx = stdin_indices[0]
        try:
            if stdin_mode == "head":
                result, capped = identify_stdin_head(magika_instance, stdin_max_bytes)
                if capped:
                    print(
                        "warning: stdin head mode reached max bytes; trailing bytes were ignored",
                        file=sys.stderr,
                    )
            else:
                result = identify_stdin_spool(magika_instance)
            results.append((idx, result))
        except Exception as e:
            print(f"error: stdin: {e}", file=sys.stderr)
            had_errors = True

    # Handle file paths
    if file_entries:
        valid_file_entries = []
        path_objects = []
        for idx, p in file_entries:
            pp = Path(p)
            if not pp.exists():
                print(f"error: {p}: No such file or directory", file=sys.stderr)
                had_errors = True
                continue
            if not pp.is_file():
                print(f"error: {p}: Not a regular file", file=sys.stderr)
                had_errors = True
                continue
            try:
                # Check readability
                with open(pp, "rb"):
                    pass
            except PermissionError:
                print(f"error: {p}: Permission denied", file=sys.stderr)
                had_errors = True
                continue
            valid_file_entries.append((idx, p))
            path_objects.append(pp)

        if path_objects:
            try:
                magika_results = magika_instance.identify_paths(path_objects)
                for (idx, p_str), result in zip(valid_file_entries, magika_results):
                    results.append((idx, result_to_dict(p_str, result)))
            except Exception as e:
                print(f"error: detection failed: {e}", file=sys.stderr)
                had_errors = True

    # Sort by original order
    results.sort(key=lambda x: x[0])
    return [r[1] for r in results], had_errors


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="detect-file-type",
        description="AI-powered local file type detection using Google Magika",
    )
    parser.add_argument("paths", nargs="+", help="File paths to detect (use - for stdin)")
    parser.add_argument(
        "--json", dest="format", action="store_const", const="json", help="JSON output (default)"
    )
    parser.add_argument(
        "--human", dest="format", action="store_const", const="human", help="Human-readable output"
    )
    parser.add_argument(
        "--mime", dest="format", action="store_const", const="mime", help="Bare MIME type output"
    )
    parser.add_argument(
        "--recursive", "-r", action="store_true", help="Recurse into directories"
    )
    parser.add_argument(
        "--stdin-mode",
        choices=["spool", "head"],
        default="spool",
        help="How to process '-' stdin input (default: spool)",
    )
    parser.add_argument(
        "--stdin-max-bytes",
        type=positive_int,
        default=STDIN_HEAD_MAX_BYTES,
        help=f"Max stdin bytes in head mode (default: {STDIN_HEAD_MAX_BYTES})",
    )
    parser.set_defaults(format="json")

    args = parser.parse_args(argv)

    paths = collect_paths(args.paths, args.recursive)
    if not paths:
        print("error: no files to process", file=sys.stderr)
        sys.exit(1)

    magika_instance = Magika()
    results, had_errors = detect_files(
        magika_instance,
        paths,
        stdin_mode=args.stdin_mode,
        stdin_max_bytes=args.stdin_max_bytes,
    )

    if not results:
        sys.exit(1)

    if args.format == "json":
        print(format_json(results))
    elif args.format == "human":
        print(format_human(results))
    elif args.format == "mime":
        print(format_mime(results))

    if had_errors:
        sys.exit(2)


if __name__ == "__main__":
    main()
