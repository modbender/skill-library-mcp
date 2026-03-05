---
name: mistral-ocr
description: Convert PDF/images to Markdown/JSON/HTML using Mistral OCR API. Supports image extraction, table recognition, header/footer handling, and multi-column layouts.
registry:
  homepage: https://github.com/YZDame/Mistral-OCR-SKILL
  author: YZDame
  credentials:
    required: true
    env_vars:
      - MISTRAL_API_KEY
---

# ⚠️ Privacy Warning - 隐私警告

**IMPORTANT - READ BEFORE INSTALLING:**

This tool **uploads your files to Mistral's cloud servers** for OCR processing.

**Do NOT use with sensitive or confidential documents** unless:
- You trust Mistral's data handling policies
- You have reviewed Mistral's privacy policy
- You accept that file contents will be transmitted and processed remotely

**For sensitive documents, use offline/local OCR tools instead.**

---

# Mistral OCR (OpenClaw Skill)

A powerful OCR tool that converts PDF files and images into Markdown, JSON, or HTML formats using Mistral's state-of-the-art OCR API.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)

## Features

- PDF to Markdown/JSON/HTML conversion
- Image extraction with automatic path replacement
- Table recognition
- Header/footer handling
- Multi-column layout support
- Batch processing via CLI

## Installation (for OpenClaw)

OpenClaw will automatically read this README and install dependencies.

**Manual Installation:**

```bash
# Clone or download this repository
git clone https://github.com/YZDame/Mistral-OCR-SKILL.git
cd Mistral-OCR-SKILL

# Install dependencies
pip install -r requirements.txt
```

## 🔑 API Key Setup (Required)

You need a Mistral API key to use this tool.

**Get your API key:**
👉 [https://console.mistral.ai/home](https://console.mistral.ai/home)

**Set the environment variable:**

```bash
# Temporary (current terminal session)
export MISTRAL_API_KEY=your_api_key_here

# Permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export MISTRAL_API_KEY=your_api_key_here' >> ~/.zshrc
source ~/.zshrc
```

## CLI Usage

```bash
cd scripts

# Process PDF to Markdown
python3 mistral_ocr.py -i input.pdf

# Process PDF to JSON
python3 mistral_ocr.py -i input.pdf -f json

# Process PDF to HTML
python3 mistral_ocr.py -i input.pdf -f html

# Specify output directory
python3 mistral_ocr.py -i input.pdf -o ~/my_ocr_results

# Process images
python3 mistral_ocr.py -i image.png -f markdown
```

## Arguments

| Flag | Description |
|------|-------------|
| `-i, --input` | Input file path (required) |
| `-f, --format` | Output format: markdown/json/html (default: markdown) |
| `-o, --output` | Output directory (default: ./ocr_result) |

## Output

After processing, you'll get:

- `result.md` / `result.json` / `result.html` - Main output file
- `images/` - Extracted images (for Markdown/HTML formats)

## Data Privacy

**What happens to your files:**
1. Files are uploaded to Mistral's OCR API
2. Files are processed on Mistral servers
3. Processing results are returned to you
4. Files are not stored on Mistral servers (per Mistral policy)

**For more details, see:** https://mistral.ai/privacy-policy

## Troubleshooting

**"MISTRAL_API_KEY is not set" error:**

Make sure you've set the environment variable correctly. Run:

```bash
echo $MISTRAL_API_KEY
```

If nothing is returned, re-set the API key following the instructions above.

## License

MIT License - feel free to use in your projects!

## Contributing

Pull requests are welcome. For major changes, please open an issue first.
