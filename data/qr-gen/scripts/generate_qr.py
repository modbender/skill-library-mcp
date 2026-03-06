#!/usr/bin/env python3
"""Generate QR codes from text, URLs, WiFi credentials, vCards, etc."""

import argparse
import sys
import os

def ensure_qrcode():
    try:
        import qrcode
        return qrcode
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode[pil]", "-q"])
        import qrcode
        return qrcode

def wifi_payload(ssid, password, security="WPA", hidden=False):
    hidden_str = "true" if hidden else "false"
    password_str = password if password else ""
    return f"WIFI:T:{security};S:{ssid};P:{password_str};H:{hidden_str};;"

def vcard_payload(name, phone="", email="", org="", url=""):
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{name}"]
    if phone: lines.append(f"TEL:{phone}")
    if email: lines.append(f"EMAIL:{email}")
    if org: lines.append(f"ORG:{org}")
    if url: lines.append(f"URL:{url}")
    lines.append("END:VCARD")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate QR codes")
    parser.add_argument("data", help="Text/URL to encode")
    parser.add_argument("-o", "--output", default="qr.png", help="Output file path (default: qr.png)")
    parser.add_argument("-s", "--size", type=int, default=10, help="Box size in pixels (default: 10)")
    parser.add_argument("--border", type=int, default=4, help="Border width in boxes (default: 4)")
    parser.add_argument("--format", choices=["png", "svg", "ascii"], default=None,
                        help="Output format (auto-detected from extension)")
    parser.add_argument("--error-correction", choices=["L", "M", "Q", "H"], default="M",
                        help="Error correction level (default: M)")
    parser.add_argument("--wifi-ssid", help="Generate WiFi QR: SSID")
    parser.add_argument("--wifi-pass", help="Generate WiFi QR: password")
    parser.add_argument("--wifi-security", default="WPA", help="WiFi security type (default: WPA)")
    args = parser.parse_args()

    qrcode = ensure_qrcode()

    ec_levels = {"L": qrcode.constants.ERROR_CORRECT_L, "M": qrcode.constants.ERROR_CORRECT_M,
                 "Q": qrcode.constants.ERROR_CORRECT_Q, "H": qrcode.constants.ERROR_CORRECT_H}

    # Determine data
    data = args.data
    if args.wifi_ssid:
        data = wifi_payload(args.wifi_ssid, args.wifi_pass or "", args.wifi_security)

    # Determine format
    fmt = args.format
    if not fmt:
        ext = os.path.splitext(args.output)[1].lower()
        fmt = {"svg": "svg", ".svg": "svg", ".txt": "ascii"}.get(ext, "png")

    qr = qrcode.QRCode(version=None, error_correction=ec_levels[args.error_correction],
                        box_size=args.size, border=args.border)
    qr.add_data(data)
    qr.make(fit=True)

    if fmt == "ascii":
        qr.print_ascii(out=sys.stdout if args.output == "qr.png" else open(args.output, "w"))
        if args.output != "qr.png":
            print(f"Saved ASCII QR to {args.output}")
    elif fmt == "svg":
        import qrcode.image.svg
        img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
        img.save(args.output)
        print(f"Saved SVG QR to {args.output}")
    else:
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(args.output)
        print(f"Saved QR to {args.output}")

if __name__ == "__main__":
    main()
