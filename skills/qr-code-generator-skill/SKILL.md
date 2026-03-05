---
name: qr-generator
description: "A precision utility to generate QR code images from URLs or text using Python."
version: "1.0.0"
author: "YourName"
tags: [utility, images, tools, qr]
metadata:
  openclaw:
    requires:
      bins:
        - python3
      pip:
        - qrcode[pil]
---

# QR Code Generator Skill

This skill empowers the OpenClaw agent to generate and save QR code images locally.

## Logic & Constraints
- **Library:** Uses the `qrcode` Python library with `Pillow` (PIL) support.
- **Output Format:** High-resolution PNG.
- **Default Path:** If no path is specified, save to the current working directory as `qrcode.png`.
- **Error Handling:** If `qrcode` is missing, the agent should first attempt `pip install qrcode[pil]`.

## Execution Instructions
When the user requests a QR code, execute a Python one-liner to perform the generation. 

### Implementation Template:
```bash
python3 -c "import qrcode; img = qrcode.QRCode(version=1, box_size=10, border=5); img.add_data('USER_TEXT_HERE'); img.make(fit=True); img.make_image(fill_color='black', back_color='white').save('FILE_NAME.png')"