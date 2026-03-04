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

# WiseDiag MedOcr Skill

Convert PDF files into Markdown format. The script handles API authentication, file upload, OCR processing, and saves the result automatically.

## ⚠️ IMPORTANT: How to Use This Skill

**You MUST use the provided script to process files. Do NOT call any API or HTTP endpoint directly.**

The script `scripts/medocr.py` handles everything:
- API authentication (reads `WISEDIAG_API_KEY` from environment)
- PDF upload and OCR processing
- Saves the Markdown result to `WiseDiag-MedOcr-1.0.0/{filename}.md`

## 🔑 API Key Setup (Required)

**Get your API key:**
👉 https://chat.wisediag.com/apiKeyManage

```bash
export WISEDIAG_API_KEY=your_api_key
```

## Installation

```bash
pip install -r requirements.txt
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

## License

MIT
