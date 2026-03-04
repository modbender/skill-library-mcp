---
name: mistral-ocr
description: Convert PDF/images to Markdown/JSON/HTML using Mistral OCR API. Supports image extraction, table recognition, header/footer handling. Usage: Upload a file and say "Use Mistral OCR to process this".
---

# Mistral OCR Skill

## Usage

Upload a file and say "Use Mistral OCR to process this".

Supported formats:
- PDF (.pdf)
- Images (.png, .jpg, .jpeg, .tiff)

## CLI Usage

```bash
cd ~/.openclaw/workspace/skills/mistral_ocr

# Process PDF
python3 mistral_ocr.py -i input.pdf -f markdown

# Process image
python3 mistral_ocr.py -i image.png -f markdown

# Output as JSON
python3 mistral_ocr.py -i input.pdf -f json directory
python3 mistral_ocr.py -i input

# Specify output.pdf -o ~/ocr_results
```

## Arguments

| Flag | Description |
|------|-------------|
| `-i, --input` | Input file path (required) |
| `-f, --format` | Output format: markdown/json/html (default: markdown) |
| `-o, --output` | Output directory (default: ocr_result/) |

## Output

- **Markdown**: Complete document with image references
- **JSON**: Structured page data
- **Images**: Saved in images/ subdirectory

## API Key

Set the API key as an environment variable:

```bash
export MISTRAL_API_KEY=your_api_key
```

The script requires `MISTRAL_API_KEY` to be set. It will raise an error if the environment variable is missing.
