---
name: qr-code
description: "Generate QR codes for text, URLs, WiFi connections, and business cards (vCard). Use when: (1) creating QR codes for websites or text, (2) generating WiFi connection QR codes for easy network sharing, (3) creating digital business card QR codes, or (4) any QR code generation needs. Supports saving to custom file paths."
---

# QR Code Generator

Generate QR codes locally for various use cases. No API calls required - everything is generated on your machine.

## When to Use

- Share URLs quickly via QR codes
- Create WiFi connection codes for guests
- Generate digital business cards (vCard)
- Encode any text data into QR format

## Prerequisites

Install the required Python package:

```bash
pip3 install qrcode[pil]
# or on Ubuntu/Debian:
sudo apt-get install python3-qrcode
```

## Quick Start

### Generate URL QR Code
```bash
python3 scripts/qr-code.py text "https://example.com"
# Output: QR code saved to ~/qrcode_output.png
```

### Generate WiFi QR Code
```bash
python3 scripts/qr-code.py wifi "MyNetwork" "myPassword"
# Scan with phone to auto-connect
```

### Generate Business Card
```bash
python3 scripts/qr-code.py vcard --name "John Doe" --phone "+1234567890" --email "john@example.com"
```

## Commands

### `text <content> [output_path]`
Generate a QR code containing any text or URL.

**Parameters:**
- `content`: The text or URL to encode
- `output_path`: Optional. Where to save the PNG file. Defaults to `~/qrcode_output.png`

**Examples:**
```bash
# Basic URL
python3 scripts/qr-code.py text "https://github.com"

# Custom output location
python3 scripts/qr-code.py text "Hello World" ./hello_qr.png

# Long URL (auto-fits to QR version)
python3 scripts/qr-code.py text "https://example.com/very/long/path?with=parameters"
```

### `wifi <ssid> <password> [output_path]`
Generate a QR code that allows phones to connect to WiFi automatically.

**Parameters:**
- `ssid`: WiFi network name
- `password`: WiFi password
- `output_path`: Optional output path

**Supported phones:**
- iOS 11+ (Camera app)
- Android 9+ (Camera or WiFi settings)
- Most QR scanner apps

**Example:**
```bash
python3 scripts/qr-code.py wifi "HomeWiFi" "secretPass123" ~/wifi_qr.png
```

### `vcard --name <name> [options] [output_path]`
Generate a vCard (digital business card) QR code.

**Options:**
- `--name, -n` (required): Full name
- `--phone, -p`: Phone number
- `--email, -e`: Email address
- `--org, -o`: Organization/Company
- `--title, -t`: Job title
- `--url, -u`: Website URL
- `output`: Optional output path

**Examples:**
```bash
# Simple card
python3 scripts/qr-code.py vcard --name "张三"

# Full business card
python3 scripts/qr-code.py vcard \
  --name "John Smith" \
  --phone "+1-555-1234" \
  --email "john@company.com" \
  --org "Acme Corp" \
  --title "Senior Developer" \
  --url "https://johnsmith.dev" \
  ~/business_card.png
```

## Tips

- QR codes use high error correction - they still work even if partially obscured
- For large amounts of text, the QR code will automatically use a larger version
- Generated files are standard PNG images that can be printed or shared digitally
- WiFi QR codes follow the universal WIFI: format standard

## Troubleshooting

**"Missing qrcode module" error:**
```bash
pip3 install qrcode[pil]
```

**Permission denied when saving:**
- Check that the output directory exists
- Ensure you have write permissions

## Output

All generated QR codes are saved as PNG images. The output path will be displayed after successful generation.
