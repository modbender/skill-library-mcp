---
name: imgbb-api
description: Upload images to ImgBB and get shareable URLs. Use when: (1) User wants to upload images to imgbb, (2) Need to get direct image URLs for sharing, (3) Converting local images to shareable links, (4) Bulk uploading images, (5) Uploading from URL, (6) Base64 encoding.
version: 1.1.0
changelog: "v1.1.0: Added reasoning framework, decision tree, troubleshooting"
metadata:
  openclaw:
    requires:
      bins:
        - python3
      pip:
        - requests
      env:
        - IMGBB_API_KEY
    emoji: "📸"
    category: "utility"
    homepage: https://github.com/KeXu9/imgbb-api
---

# ImgBB API

Upload images to ImgBB and get shareable URLs.

## When This Skill Activates

This skill triggers when user wants to upload images to the web for sharing.

## Reasoning Framework

| Step | Action | Why |
|------|--------|-----|
| 1 | **CHECK** | Verify API key is available |
| 2 | **PREPARE** | Get image path or URL |
| 3 | **UPLOAD** | Send to ImgBB API |
| 4 | **RETURN** | Return shareable URL |

---

## Setup

```bash
export IMGBB_API_KEY="your_api_key_here"
# or
echo "your_api_key" > ~/.imgbb_api_key
```

## Get API Key

1. Go to https://api.imgbb.com/
2. Click "Get API Key"
3. Copy your API key

---

## Decision Tree

```
├── Upload single image → python imgbb.py image.jpg
├── Upload from URL → python imgbb.py --url "URL"
├── Custom name → python imgbb.py image.jpg --name myimg
├── Set expiration → python imgbb.py image.jpg --expiration 3600
├── Batch upload → python imgbb.py --batch ./folder/
└── JSON output → python imgbb.py image.jpg --json
```

---

## Usage

```bash
# Upload file
python imgbb.py image.jpg

# With custom API key
python imgbb.py image.jpg --key YOUR_KEY

# From URL
python imgbb.py --url "https://..."

# Batch upload
python imgbb.py --batch ./folder/

# JSON output
python imgbb.py image.jpg --json
```

## Options

| Flag | Description |
|------|-------------|
| `image` | Path to image |
| `--key` | API key |
| `--url` | Upload from URL |
| `--name` | Custom name |
| `--expiration` | Expiry seconds |
| `--json` | JSON output |
| `--batch` | Batch folder |
| `--set-key` | Save API key |

---

## Troubleshooting

### No API key found
- Fix: Set `IMGBB_API_KEY` env or use `--key`

### File not found
- Fix: Check file path is correct

### Invalid image format
- Fix: Use JPG, PNG, GIF, or WEBP

### Image too large
- Fix: Compress under 32MB

---

## Quick Reference

| Task | Command |
|------|---------|
| Upload | `python imgbb.py image.jpg` |
| URL | `python imgbb.py --url "URL"` |
| Batch | `python imgbb.py --batch ./folder/` |
| JSON | `python imgbb.py image.jpg --json` |
