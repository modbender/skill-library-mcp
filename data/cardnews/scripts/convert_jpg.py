#!/usr/bin/env python3
"""Convert PNG card news images to Instagram-ready JPG files.

Usage:
    python3 convert_jpg.py image1.png image2.png ...
    python3 convert_jpg.py *.png --size 1080
    python3 convert_jpg.py *.png --quality 95

Output: *-ig.jpg files in the same directory.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image


def convert(src: str, size: int = 1024, quality: int = 92) -> str:
    img = Image.open(src).convert("RGB")
    if img.size != (size, size):
        img = img.resize((size, size), Image.LANCZOS)
    out = str(Path(src).with_suffix("")) + "-ig.jpg"
    img.save(out, "JPEG", quality=quality)
    print(f"✅ {Path(src).name} → {Path(out).name}")
    return out


def main():
    parser = argparse.ArgumentParser(description="PNG → JPG converter for Instagram")
    parser.add_argument("files", nargs="+", help="PNG files to convert")
    parser.add_argument("--size", type=int, default=1024, help="Output size (square, default 1024)")
    parser.add_argument("--quality", type=int, default=92, help="JPEG quality (default 92)")
    args = parser.parse_args()

    results = []
    for f in args.files:
        if not Path(f).exists():
            print(f"⚠️  {f} not found, skipping")
            continue
        results.append(convert(f, args.size, args.quality))

    print(f"\n🎉 Converted {len(results)} files")
    for r in results:
        print(f"   {r}")


if __name__ == "__main__":
    main()
