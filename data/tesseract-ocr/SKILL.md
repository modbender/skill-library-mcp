---
name: tesseract-ocr
description: |
  Extract text from images using the Tesseract OCR engine directly via command line.
  Supports multiple languages including Chinese, English, and more. Use this skill 
  when users need to extract text from images, recognize text content in images, 
  or perform OCR tasks without Python dependencies.
---

# Tesseract OCR Skill

Extract text content from images using the Tesseract engine directly via command line.

## Features

- Extract text from image files using native tesseract CLI
- Support multi-language recognition (Chinese, English, etc.)
- No Python dependencies required
- Simple and fast

## Dependencies

Install Tesseract OCR system package:

```bash
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# macOS:
brew install tesseract tesseract-lang
```

## Usage

### Basic Usage

```bash
# Use default language (English)
tesseract /path/to/image.png stdout

# Specify language (Chinese + English)
tesseract /path/to/image.png stdout -l chi_sim+eng

# Save to file
tesseract /path/to/image.png output.txt -l chi_sim+eng

# Multiple languages
tesseract /path/to/image.png stdout -l chi_sim+eng+jpn
```

### Common Language Codes

| Language | Code |
|----------|------|
| Simplified Chinese | chi_sim |
| Traditional Chinese | chi_tra |
| English | eng |
| Japanese | jpn |
| Korean | kor |
| Chinese + English | chi_sim+eng |

### Quick Examples

```bash
# OCR with Chinese support
tesseract image.jpg stdout -l chi_sim

# OCR with mixed Chinese and English
tesseract image.png stdout -l chi_sim+eng

# Save to file instead of stdout
tesseract document.png result -l chi_sim+eng
# Creates result.txt
```

## Notes

1. OCR accuracy depends on image quality; use clear images for best results
2. Complex layouts (tables, multi-column) may require post-processing
3. Chinese recognition requires the tesseract-ocr-chi-sim language pack
4. Language packs must be installed separately on your system
