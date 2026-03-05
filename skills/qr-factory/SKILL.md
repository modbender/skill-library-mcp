---
description: Generate QR codes for URLs, WiFi credentials, vCards, email, SMS, and plain text.
---

# QR Factory

Generate QR codes for various data types with customizable appearance.

## Requirements

- Python 3.8+
- `pip install qrcode[pil]` (qrcode + Pillow)

## Instructions

1. **Determine QR type** and build payload:
   - **URL**: Raw URL string (e.g., `https://example.com`)
   - **WiFi**: `WIFI:T:<WPA|WEP|nopass>;S:<SSID>;P:<password>;;`
   - **vCard**: `BEGIN:VCARD\nVERSION:3.0\nN:<last>;<first>\nTEL:<phone>\nEMAIL:<email>\nEND:VCARD`
   - **Email**: `mailto:user@example.com?subject=Hello&body=Hi`
   - **SMS**: `smsto:<number>:<message>`
   - **Text**: Raw text string

2. **Generate QR code**:
   ```python
   import qrcode
   qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
   qr.add_data(payload)
   qr.make(fit=True)
   img = qr.make_image(fill_color="black", back_color="white")
   img.save(output_path)
   ```

3. **Output**: Save as PNG to `/tmp/qr_<type>_<timestamp>.png` or user-specified path. Return the file path.

## Customization Options

- **Size**: Adjust `box_size` (default 10, range 5-20)
- **Border**: Adjust `border` (default 4, minimum 4 per spec)
- **Colors**: `fill_color` and `back_color` accept color names or hex codes
- **Error correction**: `L` (7%), `M` (15%), `Q` (25%), `H` (30%) — higher = more resilient but larger

## Edge Cases

- **Large data**: QR version auto-scales (`fit=True`), but warn if data > 2KB (may not scan well).
- **Special characters in WiFi**: Escape `;`, `:`, `\`, and `,` in SSID/password with backslash.
- **Missing Pillow**: If `PIL` import fails, run `pip install Pillow` and retry.
- **Binary data**: Not recommended for QR — suggest a URL link instead.

## Security

- **WiFi passwords**: Warn user that QR codes containing passwords are readable by anyone who scans them.
- **Sensitive data**: Never generate QR codes containing API keys, tokens, or secrets unless explicitly requested.
- Sanitize file paths to prevent directory traversal.
