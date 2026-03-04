#!/usr/bin/env python3
"""Generate a QR code image from credential JSON. Mode A: vault → QR.

Usage: echo '{"username":"x","password":"y","domain":"z"}' | python3 generate-qr.py [output.png]
Outputs the path to the generated QR image.
"""

import json
import sys
import os
import tempfile

# Allow importing sibling module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
qr_format = import_module("qr-format")

import qrcode

def main():
    cred = json.load(sys.stdin)
    payload = qr_format.encode(cred["username"], cred["password"], cred["domain"])

    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "qr-password.png")

    img = qrcode.make(payload, error_correction=qrcode.constants.ERROR_CORRECT_M)
    img.save(out_path)
    print(out_path)

if __name__ == "__main__":
    main()
