#!/usr/bin/env python3
"""Decode a QR code image to credential JSON. Mode B: camera → credential.

Usage: python3 read-qr.py <image_path>
Outputs decoded credential JSON to stdout.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
qr_format = import_module("qr-format")

import cv2

def main():
    if len(sys.argv) < 2:
        print("Usage: read-qr.py <image_path>", file=sys.stderr)
        sys.exit(1)

    img = cv2.imread(sys.argv[1])
    if img is None:
        print(f"Cannot open image: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)

    if not data:
        print("No QR code found in image", file=sys.stderr)
        sys.exit(1)

    cred = qr_format.decode(data)
    print(json.dumps(cred))

if __name__ == "__main__":
    main()
