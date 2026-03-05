#!/usr/bin/env python3
import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.request
import urllib.error

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

# Configuration
BASE_URL = os.getenv("LNBITS_BASE_URL", "https://legend.lnbits.com").rstrip("/")
API_KEY = os.getenv("LNBITS_API_KEY")
# Save QR codes relative to CWD so the path can be expressed as ./ for media parsers.
# The CWD is shared between the Python subprocess and the parent Node.js process.
QR_DIR = os.path.join(os.getcwd(), ".lnbits_qr")
QR_MAX_AGE_SECONDS = 300  # 5 minutes

# --- Helpers ---

def error(msg, code=1):
    print(json.dumps({"error": msg}))
    sys.exit(code)

def cleanup_old_qr_files():
    """Remove QR code files older than QR_MAX_AGE_SECONDS."""
    if not os.path.exists(QR_DIR):
        return
    now = time.time()
    for filename in os.listdir(QR_DIR):
        if not filename.endswith(".png"):
            continue
        filepath = os.path.join(QR_DIR, filename)
        try:
            if now - os.path.getmtime(filepath) > QR_MAX_AGE_SECONDS:
                os.remove(filepath)
        except OSError:
            pass

def get_qr_path():
    """Get a unique path for a new QR code file. Returns (absolute_path, media_path).

    The media_path is a ./ relative path resolved from the gateway's CWD (home dir)
    since OpenClaw's MEDIA: parser only accepts ./relative paths.
    """
    os.makedirs(QR_DIR, exist_ok=True)
    cleanup_old_qr_files()
    filename = f"invoice_{int(time.time() * 1000)}.png"
    abs_path = os.path.join(QR_DIR, filename)
    media_path = "./" + os.path.relpath(abs_path, os.path.expanduser("~"))
    return abs_path, media_path

def generate_qr(data, output_path=None):
    """Generate a QR code. If output_path provided, saves to file and returns path. Otherwise returns base64."""
    if not HAS_QRCODE:
        return None
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data.upper())  # BOLT11 should be uppercase for QR
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    if output_path:
        img.save(output_path, format="PNG")
        return output_path
    else:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

def request(method, endpoint, data=None):
    if not API_KEY:
        error("LNBITS_API_KEY environment variable is not set.")

    url = f"{BASE_URL}/api/v1{endpoint}"
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "LNbits-CLI/1.0"
    }
    body = json.dumps(data).encode("utf-8") if data else None
    
    req = urllib.request.Request(url, method=method, headers=headers, data=body)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        error(f"API Error ({e.code}): {error_body}")
    except Exception as e:
        error(f"Network Error: {str(e)}")

# --- Core Logic ---

def get_balance():
    data = request("GET", "/wallet")
    return {
        "name": data.get("name"),
        "balance_msat": data.get("balance"),
        "balance_sats": int(data.get("balance", 0) / 1000)
    }

def create_invoice(amount, memo, include_qr=True):
    result = request("POST", "/payments", {
        "out": False, "amount": amount, "memo": memo, "unit": "sat"
    })
    if include_qr and result.get("payment_request"):
        abs_path, rel_path = get_qr_path()
        qr_result = generate_qr(result["payment_request"], abs_path)
        if qr_result:
            result["qr_file"] = rel_path
            # Also include base64 for direct embedding
            with open(abs_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                result["qr_base64"] = f"image/png;base64,{b64}"
        else:
            result["qr_error"] = "qrcode library not installed (pip install qrcode[pil])"
    return result

def pay_invoice(bolt11):
    return request("POST", "/payments", {"out": True, "bolt11": bolt11})

def decode_invoice(bolt11):
    return request("POST", "/payments/decode", {"data": bolt11})

def create_wallet(name):
    url = f"{BASE_URL}/api/v1/account"
    req = urllib.request.Request(
        url,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "LNbits-CLI/1.0"},
        data=json.dumps({"name": name}).encode("utf-8")
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

# --- CLI Handlers ---

def cmd_balance(args):
    print(json.dumps(get_balance(), indent=2))

def cmd_create(args):
    print(json.dumps(create_wallet(args.name), indent=2))

def cmd_invoice(args):
    print(json.dumps(create_invoice(args.amount, args.memo, not args.no_qr), indent=2))

def cmd_pay(args):
    print(json.dumps(pay_invoice(args.bolt11), indent=2))

def cmd_decode(args):
    print(json.dumps(decode_invoice(args.bolt11), indent=2))

def cmd_qr(args):
    """Generate QR code from a BOLT11 string."""
    if args.output:
        abs_path = args.output
        rel_path = args.output
    else:
        abs_path, rel_path = get_qr_path()
    qr_result = generate_qr(args.bolt11, abs_path)
    if qr_result:
        result = {"qr_file": rel_path, "bolt11": args.bolt11}
        with open(abs_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            result["qr_base64"] = f"image/png;base64,{b64}"
        print(json.dumps(result, indent=2))
    else:
        error("qrcode library not installed (pip install qrcode[pil])")

# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="LNbits CLI Bridge for Clawdbot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Balance
    p_balance = subparsers.add_parser("balance", help="Get wallet balance")
    p_balance.set_defaults(func=cmd_balance)

    # Create Wallet (Account)
    p_create = subparsers.add_parser("create", help="Create a new LNbits wallet")
    p_create.add_argument("--name", type=str, default="Moltbot Wallet", help="Name of the new wallet")
    p_create.set_defaults(func=cmd_create)

    # Invoice
    p_invoice = subparsers.add_parser("invoice", help="Create a lightning invoice")
    p_invoice.add_argument("--amount", type=int, required=True, help="Amount in satoshis")
    p_invoice.add_argument("--memo", type=str, default="", help="Optional memo")
    p_invoice.add_argument("--no-qr", action="store_true", dest="no_qr", help="Skip QR code generation")
    p_invoice.set_defaults(func=cmd_invoice)

    # Pay
    p_pay = subparsers.add_parser("pay", help="Pay a lightning invoice")
    p_pay.add_argument("bolt11", type=str, help="The Bolt11 invoice string")
    p_pay.set_defaults(func=cmd_pay)

    # Decode
    p_decode = subparsers.add_parser("decode", help="Decode a lightning invoice")
    p_decode.add_argument("bolt11", type=str, help="The Bolt11 invoice string")
    p_decode.set_defaults(func=cmd_decode)

    # QR Code
    p_qr = subparsers.add_parser("qr", help="Generate QR code from a BOLT11 invoice")
    p_qr.add_argument("bolt11", type=str, help="The Bolt11 invoice string")
    p_qr.add_argument("-o", "--output", type=str, help="Output PNG file path (default: auto-generated temp file)")
    p_qr.set_defaults(func=cmd_qr)

    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as e:
        error(str(e))

if __name__ == "__main__":
    main()