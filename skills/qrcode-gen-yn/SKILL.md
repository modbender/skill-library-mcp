---
name: generate-qrcode
description: Generate QR codes from URLs or text using a pre-built Python script with qrcode library
author: yuanyanan
version: 1.0.0
metadata: 
  openclaw:
    emoji: "📱"
    always: true
  tags:
    - qrcode
    - image
    - utility
    - python
---

# QR Code Generator

Generate QR codes from URLs or text using a pre-built Python script.

## Usage

**IMPORTANT**: Use the existing Python script, don't write inline code.

```bash
python3 ~/.openclaw/skills/generate-qrcode/agent.py "<URL or text>" <output_path>
```

## Examples

Generate QR code for a URL:
```bash
python3 ~/.openclaw/skills/generate-qrcode/agent.py "https://www.baidu.com" ~/Desktop/baidu_qr.png
```

Generate QR code for text:
```bash
python3 ~/.openclaw/skills/generate-qrcode/agent.py "Hello World" ~/Desktop/hello.png
```

## Output
- PNG image file with QR code
- Default size: 10x10 boxes per module
- 4-box border

## Requirements
- Python 3.x
- qrcode library (pre-installed)
