---
name: qr-code
description: Generate, decode, and beautify QR codes with customizable colors, logos, and formats. Works across all OpenClaw channels including WhatsApp.
openclaw:
  homepage: https://github.com/zouyawen/openclaw-qrcode
  user-invocable: true
  emoji: "📱"
---

# QR Code Skill

**⚠️ This skill requires the companion plugin to function!**

## 🚀 Quick Start

### 💎 **Recommended: Full Feature Installation**
For the complete experience with **rounded dots, gradient colors, logo integration, and natural language support**, install from GitHub:

```bash
curl -s https://raw.githubusercontent.com/zouyawen/openclaw-qrcode/main/install.sh | bash
openclaw gateway restart
```

### ⚡ **Basic Installation (from ClawHub)**
This provides basic QR code functionality only:

```bash
mkdir -p ~/.openclaw/skills/qr-code
# Extract the downloaded skill.zip to this directory
openclaw gateway restart
```

> **💡 Pro Tip**: The GitHub installation includes advanced features like rounded dots, color gradients, and logo embedding that aren't available through ClawHub alone!

## Features
- **Generate**: Create QR codes with custom colors, background, size, logo overlay, and format (PNG, JPG, SVG)
- **Decode**: Extract data from QR code images
- **Beautify**: Enhance existing QR codes with new styling while preserving data
- **Natural Language**: Just say "make a colorful QR code" or "add a logo to this QR code"
- **Cross-channel compatibility**: Works seamlessly across all OpenClaw channels including WhatsApp, Telegram, Discord, etc.
- **Automatic format handling**: Converts formats as needed for channel compatibility
- **Enhanced security**: Path traversal protection, input validation, and secure error handling
- **WhatsApp optimization**: Automatic SVG-to-PNG conversion for WhatsApp compatibility

## Security Features
- **Path traversal protection**: Logo paths are validated to prevent directory traversal attacks
- **Input sanitization**: All color, size, and format parameters are strictly validated
- **Secure error handling**: Comprehensive try-catch blocks prevent information leakage
- **File access restrictions**: Only allows access to files within the workspace directory

## Usage Examples

### Natural Language (Recommended)
- "生成一个圆点的渐变色二维码，内容是 https://example.com"
- "在二维码中间加个 logo"
- "用蓝色和黄色做渐变效果"
- "这个二维码图片里是什么内容？" (attach image)

### Command Mode (Optional)
```
/qr generate https://mzt315.com color=red backgroundColor=white size=10 format=png
/qr decode [attach QR code image]  
/qr beautify [attach QR code image] color=green backgroundColor=black size=12
```

### With Logo (Secure)
```
/qr generate https://mzt315.com logoPath=logo.png
```
Note: Logo paths must be relative to the workspace and cannot contain `..` or absolute paths.

## File Locations
- **QR Code Output**: `~/clawd/qr-codes/`
- **Logo Assets**: `~/clawd/qr-assets/` (place your logo files here)

## WhatsApp Compatibility
- Automatically handles WhatsApp's format requirements (PNG/JPG only)
- **Automatic SVG-to-PNG conversion**: If SVG is requested on WhatsApp, it's automatically converted to PNG
- Returns MEDIA paths that can be sent directly to any channel
- Optimized for mobile viewing with appropriate sizing

## Input Validation
- **Colors**: Must be valid CSS color names or hex codes (e.g., "red", "#FF0000")
- **Background Colors**: Same validation as colors
- **Size**: Must be a number between 1 and 50 (inclusive)
- **Format**: Must be one of: png, jpg, jpeg, svg
- **Logo Path**: Must be a relative path within the workspace directory

## Installation Requirements

This skill works best with the companion plugin from GitHub:

```bash
# Full feature installation (recommended)
curl -s https://raw.githubusercontent.com/zouyawen/openclaw-qrcode/main/install.sh | bash

# Python dependencies (installed automatically by the script)
# qrcode[pil], pillow, numpy, pyzbar
```

## Technical Details
This skill leverages OpenClaw's built-in `qr_code_operations` tool which supports both Python-based advanced features and Node.js fallback for maximum compatibility across different environments. All operations include comprehensive error handling and security validation.