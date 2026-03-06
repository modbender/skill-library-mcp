"""Verification helper for rendered TikTok intro slides."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ModuleNotFoundError:
    print(
        "Missing dependency: Pillow. Install with: python3 -m pip install pillow",
        file=sys.stderr,
    )
    sys.exit(1)


EXPECTED_FILES = [f"slide_{idx:02d}.png" for idx in range(1, 7)]
EXPECTED_SIZE = (1024, 1536)


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify rendered slide PNG outputs.")
    parser.add_argument("--dir", required=True, help="Directory containing slide PNG files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    slides_dir = Path(args.dir)
    if not slides_dir.exists() or not slides_dir.is_dir():
        fail(f"Slides directory not found: {slides_dir}")

    actual = sorted(path.name for path in slides_dir.glob("slide_*.png"))
    if actual != EXPECTED_FILES:
        fail(
            "Expected exactly these files: "
            f"{', '.join(EXPECTED_FILES)}. Found: {', '.join(actual) or '(none)'}"
        )

    for name in EXPECTED_FILES:
        path = slides_dir / name
        try:
            with Image.open(path) as img:
                if img.size != EXPECTED_SIZE:
                    fail(f"{name} has size {img.size}, expected {EXPECTED_SIZE}")
        except OSError as exc:
            fail(f"Could not open {name} as PNG: {exc}")

    print(
        f"OK: verified {len(EXPECTED_FILES)} slides in {slides_dir} at "
        f"{EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}"
    )


if __name__ == "__main__":
    main()
