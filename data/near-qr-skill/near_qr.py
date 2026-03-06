#!/usr/bin/env python3
"""
NEAR QR Code Skill — OpenClaw
Generate and read QR codes for NEAR Protocol addresses and payment requests.
"""

import argparse
import json
import os
import sys
import urllib.parse
from pathlib import Path

try:
    import qrcode
except ImportError:
    print("Error: 'qrcode' package not found. Install with: pip install qrcode[pil]")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: 'Pillow' package not found. Install with: pip install Pillow")
    sys.exit(1)

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
except ImportError:
    pyzbar_decode = None  # Optional — reading QR codes requires pyzbar


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NEAR_QR_SCHEME = "near"
NEAR_ADDRESS_PREFIX = f"{NEAR_QR_SCHEME}:"
NEAR_PAYMENT_ACTION = "transfer"

DEFAULT_QR_SIZE = 400
DEFAULT_BOX_SIZE = 10
DEFAULT_BORDER = 4

NEAR_PURPLE = (112, 0, 255)
NEAR_DARK = (30, 30, 30)
WHITE = (255, 255, 255)


# ---------------------------------------------------------------------------
# URI helpers
# ---------------------------------------------------------------------------

def build_address_uri(account: str) -> str:
    """Build a NEAR address URI: near:<account_id>"""
    return f"{NEAR_ADDRESS_PREFIX}{account}"


def build_payment_uri(to: str, amount: str, memo: str | None = None) -> str:
    """
    Build a NEAR payment URI.
    Format: near:<account_id>?action=transfer&amount=<amount>[&memo=<memo>]
    """
    params: dict[str, str] = {
        "action": NEAR_PAYMENT_ACTION,
        "amount": amount,
    }
    if memo:
        params["memo"] = memo
    query = urllib.parse.urlencode(params)
    return f"{NEAR_ADDRESS_PREFIX}{to}?{query}"


def parse_near_uri(uri: str) -> dict:
    """
    Parse a NEAR URI back into structured data.
    Returns a dict with 'type' and relevant fields.
    """
    if not uri.startswith(NEAR_ADDRESS_PREFIX):
        return {"type": "unknown", "raw": uri}

    remainder = uri[len(NEAR_ADDRESS_PREFIX):]

    if "?" in remainder:
        account, query_string = remainder.split("?", 1)
        params = dict(urllib.parse.parse_qsl(query_string))
        action = params.get("action", "")
        if action == NEAR_PAYMENT_ACTION:
            result: dict = {
                "type": "near_payment",
                "to": account,
                "amount": params.get("amount", "0"),
            }
            if "memo" in params:
                result["memo"] = params["memo"]
            return result
        return {"type": "near_unknown_action", "account": account, "params": params}

    return {"type": "near_address", "account": remainder}


# ---------------------------------------------------------------------------
# QR generation
# ---------------------------------------------------------------------------

def _make_qr(data: str, size: int = DEFAULT_QR_SIZE) -> Image.Image:
    """Create a QR code image with NEAR branding colours (purple on white)."""
    # First pass: determine the number of modules in the QR code
    qr = qrcode.QRCode(
        version=None,  # auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=DEFAULT_BORDER,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Calculate the optimal box_size so the image is close to the desired size
    # without needing a lossy resize afterwards
    module_count = qr.modules_count + DEFAULT_BORDER * 2
    box_size = max(1, size // module_count)

    # Regenerate with the properly calculated box_size
    qr2 = qrcode.QRCode(
        version=qr.version,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=DEFAULT_BORDER,
    )
    qr2.add_data(data)
    qr2.make(fit=True)

    # Use solid NEAR purple for high-contrast, reliable scanning
    img = qr2.make_image(fill_color=NEAR_PURPLE, back_color=WHITE).convert("RGB")

    # Only resize if needed, using NEAREST to preserve sharp pixel edges
    if img.size[0] != size:
        img = img.resize((size, size), Image.NEAREST)
    return img


def _add_label(img: Image.Image, label: str) -> Image.Image:
    """Add a small text label below the QR code."""
    label_height = 36
    new_img = Image.new("RGB", (img.width, img.height + label_height), WHITE)
    new_img.paste(img, (0, 0))

    draw = ImageDraw.Draw(new_img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except (OSError, IOError):
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    x = (new_img.width - text_w) // 2
    y = img.height + 8
    draw.text((x, y), label, fill=NEAR_DARK, font=font)
    return new_img


def generate_address_qr(account: str, output: str | None = None, size: int = DEFAULT_QR_SIZE) -> str:
    """Generate a QR code for a NEAR address and save to file."""
    uri = build_address_uri(account)
    img = _make_qr(uri, size)
    img = _add_label(img, account)

    output_path = output or f"{account.replace('.', '_')}_qr.png"
    img.save(output_path)
    return os.path.abspath(output_path)


def generate_payment_qr(
    to: str,
    amount: str,
    memo: str | None = None,
    output: str | None = None,
    size: int = DEFAULT_QR_SIZE,
) -> str:
    """Generate a QR code for a NEAR payment request and save to file."""
    uri = build_payment_uri(to, amount, memo)
    img = _make_qr(uri, size)

    label = f"Pay {amount} NEAR → {to}"
    if memo:
        label += f" ({memo})"
    img = _add_label(img, label)

    output_path = output or "payment_qr.png"
    img.save(output_path)
    return os.path.abspath(output_path)


def read_qr(image_path: str) -> dict:
    """Read and decode a NEAR QR code from an image file."""
    if pyzbar_decode is None:
        return {"error": "pyzbar is not installed. Install with: pip install pyzbar"}

    path = Path(image_path)
    if not path.exists():
        return {"error": f"File not found: {image_path}"}

    img = Image.open(path)
    decoded_objects = pyzbar_decode(img)

    if not decoded_objects:
        return {"error": "No QR code found in the image."}

    raw_data = decoded_objects[0].data.decode("utf-8")
    result = parse_near_uri(raw_data)
    result["raw_uri"] = raw_data
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="NEAR QR Code Skill — generate & read NEAR QR codes",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- address ---
    addr_parser = subparsers.add_parser("address", help="Generate QR for a NEAR address")
    addr_parser.add_argument("account", help="NEAR account ID (e.g. alice.near)")
    addr_parser.add_argument("--output", "-o", help="Output file path")
    addr_parser.add_argument("--size", "-s", type=int, default=DEFAULT_QR_SIZE, help="Image size in px")

    # --- payment ---
    pay_parser = subparsers.add_parser("payment", help="Generate QR for a NEAR payment request")
    pay_parser.add_argument("to", help="Recipient NEAR account (e.g. bob.near)")
    pay_parser.add_argument("amount", help="NEAR amount (e.g. 2.5)")
    pay_parser.add_argument("--memo", "-m", help="Optional memo")
    pay_parser.add_argument("--output", "-o", help="Output file path")
    pay_parser.add_argument("--size", "-s", type=int, default=DEFAULT_QR_SIZE, help="Image size in px")

    # --- read ---
    read_parser = subparsers.add_parser("read", help="Read/decode a NEAR QR code from an image")
    read_parser.add_argument("image_path", help="Path to QR code image")

    args = parser.parse_args()

    if args.command == "address":
        out = generate_address_qr(args.account, args.output, args.size)
        print(json.dumps({"status": "success", "file": out}, indent=2))

    elif args.command == "payment":
        out = generate_payment_qr(args.to, args.amount, args.memo, args.output, args.size)
        print(json.dumps({"status": "success", "file": out}, indent=2))

    elif args.command == "read":
        result = read_qr(args.image_path)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
