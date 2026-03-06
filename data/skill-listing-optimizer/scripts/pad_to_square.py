#!/usr/bin/env python3
"""
Pad images to 2000x2000 square with white background (Amazon standard).

Usage:
    python3 pad_to_square.py <directory>
    python3 pad_to_square.py ./image_fix/

Processes all *_orig.jpg files in the directory.
Outputs *_fixed.jpg files at 2000x2000px.
"""
from PIL import Image
import os, sys, glob

dir_path = sys.argv[1] if len(sys.argv) > 1 else "."
files = glob.glob(os.path.join(dir_path, "*_orig.jpg"))

if not files:
    print(f"No *_orig.jpg files found in {dir_path}")
    sys.exit(0)

print(f"Processing {len(files)} images...\n")
for f in files:
    img = Image.open(f).convert("RGB")
    w, h = img.size
    size = max(w, h, 2000)
    new_img = Image.new("RGB", (size, size), (255, 255, 255))
    x = (size - w) // 2
    y = (size - h) // 2
    new_img.paste(img, (x, y))
    new_img = new_img.resize((2000, 2000), Image.LANCZOS)
    out = f.replace("_orig.jpg", "_fixed.jpg")
    new_img.save(out, "JPEG", quality=95)
    print(f"  ✅ {os.path.basename(f)} ({w}x{h}) → {os.path.basename(out)} (2000x2000)")

print(f"\nDone. {len(files)} images fixed.")
