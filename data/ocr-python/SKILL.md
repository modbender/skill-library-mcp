---
name: ocr
description: "Optical Character Recognition (OCR) tool, supports Chinese and
  English text extraction from PDFs and images. Use cases: (1) extract text from
  scanned PDFs, (2) recognize text from images, (3) extract text content from
  invoices, contracts, and other documents"
---


# OCR Text Recognition

This skill uses PaddleOCR for text recognition, supporting both Chinese and English.

## Quick Start

### Basic Usage

Perform OCR recognition directly on image or PDF files:

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='ch')
result = ocr.predict("file_path.jpg")
```

## Dependency Installation

Install dependencies before first use:

```bash
pip3 install paddlepaddle paddleocr
```

## Output Format

Recognition results return JSON containing:
- `rec_texts`: List of recognized text
- `rec_scores`: Confidence score for each text

## Typical Use Cases

1. **PDF Scans**: Use PyMuPDF to extract images first, then OCR
2. **Image Text Recognition**: Perform OCR directly on images
3. **Multi-page PDFs**: Process page by page

## Scripts

Common scripts are located in the `scripts/` directory.
