---
name: qr-gen
description: Generate QR codes from text, URLs, WiFi credentials, vCards, or any data. Use when the user wants to create a QR code, share a link as a scannable code, generate WiFi login QR codes, create contact/vCard QR codes, or produce any scannable barcode image. Outputs PNG, SVG, or ASCII art.
---

# QR Code Generator

Generate QR codes via the bundled Python script.

## Quick Start

```bash
python3 scripts/generate_qr.py "https://example.com" -o qr.png
```

## Common Patterns

### URL or text
```bash
python3 scripts/generate_qr.py "https://example.com" -o link.png
```

### WiFi network (scannable by phones)
```bash
python3 scripts/generate_qr.py "wifi" --wifi-ssid "MyNetwork" --wifi-pass "secret123" -o wifi.png
```

### vCard contact
Generate the vCard string and pipe it:
```bash
python3 scripts/generate_qr.py "BEGIN:VCARD
VERSION:3.0
FN:Jane Smith
TEL:+1234567890
EMAIL:jane@example.com
END:VCARD" -o contact.png
```

### ASCII art (terminal preview)
```bash
python3 scripts/generate_qr.py "hello" --format ascii
```

### SVG (scalable, web-friendly)
```bash
python3 scripts/generate_qr.py "data" -o code.svg
```

## Options

- `-o FILE` — output path (default: qr.png)
- `-s N` — box size in pixels (default: 10)
- `--border N` — border width (default: 4)
- `--format png|svg|ascii` — force format (auto-detected from extension)
- `--error-correction L|M|Q|H` — error correction level (default: M; use H for logos/damage tolerance)

## Dependencies

The script auto-installs `qrcode[pil]` via pip if missing. No manual setup needed.
