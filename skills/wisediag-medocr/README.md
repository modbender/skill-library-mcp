---
name: wisediag-medocr
description: "Convert PDF files to Markdown using WiseDiag MedOcr API. Supports table recognition, multi-column layouts, and medical document OCR. Usage: Upload a PDF file and say Use MedOcr to process this."
registry:
  homepage: https://github.com/wisediag/medocr-skill
  author: WiseDiag
  credentials:
    required: true
    env_vars:
      - WISEDIAG_API_KEY
---

# WiseDiag MedOcr (OpenClaw Skill)

A medical-grade OCR tool that converts PDF files into Markdown format.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)

## Features

- PDF to Markdown conversion with high accuracy
- Table recognition and structured formatting
- Multi-column layout support
- Medical document optimized OCR processing
- Automatic file saving with input filename

## ⚠️ IMPORTANT: How to Use This Skill

**You MUST use the provided script to process files. Do NOT call any API or HTTP endpoint directly.**

The script `scripts/medocr.py` handles everything automatically:
- API authentication (reads `WISEDIAG_API_KEY` from environment)
- PDF upload and OCR processing
- Saves the Markdown result to `WiseDiag-MedOcr-1.0.0/{filename}.md`
- No additional saving is needed after the script runs

## Installation (for OpenClaw)

OpenClaw will automatically read this README and install dependencies.

**Manual Installation:**

```bash
pip install -r requirements.txt
```

## 🔑 API Key Setup (Required)

**Get your API key:**
👉 [https://chat.wisediag.com/apiKeyManage](https://chat.wisediag.com/apiKeyManage)

**Set the environment variable:**

```bash
# Temporary (current terminal session)
export WISEDIAG_API_KEY=your_api_key_here

# Permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export WISEDIAG_API_KEY=your_api_key_here' >> ~/.zshrc
source ~/.zshrc
```

## Usage

**To process a PDF file, run:**

```bash
cd scripts
python medocr.py -i /path/to/input.pdf
```

The script will automatically save the result to `WiseDiag-MedOcr-1.0.0/{filename}.md`.

**Example:**

```bash
python medocr.py -i /path/to/体检报告.pdf
# Output saved to: WiseDiag-MedOcr-1.0.0/体检报告.md
```

**With custom output directory:**

```bash
python medocr.py -i /path/to/input.pdf -o /custom/output/dir
```

**Higher quality rendering:**

```bash
python medocr.py -i /path/to/input.pdf --dpi 300
```

## Arguments

| Flag | Description |
|------|-------------|
| `-i, --input` | Input PDF file path (required) |
| `-o, --output` | Output directory (default: ./WiseDiag-MedOcr-1.0.0) |
| `--dpi` | PDF rendering DPI, 72-600 (default: 200) |

## Output

After the script runs, the Markdown file is saved automatically:

- Default: `WiseDiag-MedOcr-1.0.0/{filename}.md`
- The file is named after the input PDF (e.g. `报告.pdf` → `报告.md`)
- No additional saving is needed — the file is already on disk

## Troubleshooting

**"WISEDIAG_API_KEY is not set" error:**

Make sure you've set the environment variable correctly. Run:

```bash
echo $WISEDIAG_API_KEY
```

If nothing is returned, re-set the API key following the instructions above.

**"Authentication failed" error:**

Your API key may be invalid or expired. Visit [https://chat.wisediag.com/apiKeyManage](https://chat.wisediag.com/apiKeyManage) to check or regenerate your key.

**Low quality OCR results:**

Try increasing the DPI for better image quality:

```bash
python medocr.py -i input.pdf --dpi 300
```

## License

MIT License - feel free to use in your projects!
