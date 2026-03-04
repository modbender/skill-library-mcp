---
name: qrcode-generator
description: "Generate QR codes from text, URLs, or images. Use when users ask to 'generate QR code', 'create QR', or 'make QR code for'. Supports text content, URLs, and local images (automatically compressed)."
version: 2.0.0
author: bowen nan
license: MIT
permissions: file read (specified image paths), file write (temp directory)
---

# QR Code Generator

Generate QR codes from text, URLs, or local images. Perfect for sharing links, contact information, or small images via scannable codes.

## Features
- ✅ Generate QR codes from text
- ✅ Generate QR codes from URLs  
- ✅ Generate QR codes from local images (auto-compressed)
- ✅ Customizable QR code size and colors
- ✅ Returns image path for easy sharing

## Installation
```bash
pip install qrcode[pil] pillow
```

## Usage Examples

### Basic Usage
```python
from agent import handle_call

# Generate QR for URL
result = handle_call({"content": "https://openclaw.ai"})

# Generate QR for text
result = handle_call({"content": "Hello OpenClaw"})

# Generate QR from image
result = handle_call({"image": "/path/to/image.jpg"})
```

### Command Line
```bash
# Install dependencies first
pip install qrcode[pil] pillow

# Run the example
python example.py
```

## Parameters
- `content` (string): Text or URL to encode
- `image` (string): Full path to local image file

## Returns
- `image_path`: Path to generated QR code image
- `error`: Error message if failed
- `message`: Informational message

## Notes
- Images larger than 10MB will be rejected
- Large images are automatically compressed for QR encoding
- For best results with images, use URLs instead of local files