---
name: universal-pdf-vision-parser
description: Extract multilingual document content and language learning notes (French, German, Japanese, Spanish, etc.) from PDFs using multimodal vision (Qwen-VL-Max). This skill converts PDF pages to high-res images and 'sees' the content to produce perfectly structured, high-readability Markdown.
---

# Universal PDF Vision Parser Skill

**Version:** 0.1

This skill is a high-end multilingual document digitizer. It uses multimodal vision to 'look' at each PDF page, making it perfect for language learning notes, bilingual documents, and complex layouts that standard OCR fails to capture.

## Prerequisites

1.  **DashScope API Key:** A valid key from Alibaba Cloud Bailian with `qwen-vl-max` access.
2.  **Environment:** 
```bash
pip install pymupdf dashscope
```

## Usage

### Basic Command

```bash
python scripts/vision_parse.py --pdf <path_to_pdf> --out <path_to_output.md> --api-key <YOUR_API_KEY> --max-pages 2
```

- `--max-pages`: (Optional) Max pages to process. Defaults to `2`. Set to `-1` for all pages.

### Agentic Workflow

1.  **Visual Scanning:** Converts PDF pages to 300 DPI PNGs.
2.  **Expert Transcription:** Qwen-VL-Max identifies the language and transcribes terms, translations, and explanations.
3.  **Markdown Structuring:** Automatically formats content with bold keywords, italicized meanings, and clean tables.

## Examples

User: "Convert this German-Chinese note to markdown: notes.pdf"

Agent Action:
```bash
python scripts/vision_parse.py --pdf notes.pdf --out notes.md
```
