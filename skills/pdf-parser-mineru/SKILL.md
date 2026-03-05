---
name: pdf-process-mineru
description: PDF document parsing tool based on local MinerU, supports converting PDF to Markdown, JSON, and other machine-readable formats.
---

## Tool List

### 1. pdf_to_markdown

Convert PDF documents to Markdown format, preserving document structure, formulas, tables, and images.

**Description**: Use MinerU to parse PDF documents and output in Markdown format, supporting OCR, formula recognition, table extraction, and other features.

**Parameters**:
- `file_path` (string, required): Absolute path to the PDF file
- `output_dir` (string, required): Absolute path to the output directory
- `backend` (string, optional): Parsing backend, options: `hybrid-auto-engine` (default), `pipeline`, `vlm-auto-engine`
- `language` (string, optional): OCR language code, such as `en` (English), `ch` (Chinese), `ja` (Japanese), etc., defaults to auto-detection
- `enable_formula` (boolean, optional): Whether to enable formula recognition, defaults to true
- `enable_table` (boolean, optional): Whether to enable table extraction, defaults to true
- `start_page` (integer, optional): Start page number (starting from 0), defaults to 0
- `end_page` (integer, optional): End page number (starting from 0), defaults to -1 meaning parse all pages

**Return Value**:
```json
{
  "success": true,
  "output_path": "/path/to/output",
  "markdown_content": "Converted Markdown content...",
  "images": ["List of image paths"],
  "tables": ["List of table information"],
  "formula_count": 10
}
```

**Examples**:
```bash
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_markdown", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output"}}'

# Use specific backend
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_markdown", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output", "backend": "pipeline"}}'

# Parse specific pages
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_markdown", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output", "start_page": 0, "end_page": 5}}'
```

---

### 2. pdf_to_json

Convert PDF documents to JSON format, including detailed layout and structural information.

**Description**: Use MinerU to parse PDF documents and output in JSON format, containing structured information such as text blocks, images, tables, formulas, etc.

**Parameters**:
- `file_path` (string, required): Absolute path to the PDF file
- `output_dir` (string, required): Absolute path to the output directory
- `backend` (string, optional): Parsing backend, options: `hybrid-auto-engine` (default), `pipeline`, `vlm-auto-engine`
- `language` (string, optional): OCR language code, such as `en` (English), `ch` (Chinese), `ja` (Japanese), etc., defaults to auto-detection
- `enable_formula` (boolean, optional): Whether to enable formula recognition, defaults to true
- `enable_table` (boolean, optional): Whether to enable table extraction, defaults to true
- `start_page` (integer, optional): Start page number (starting from 0), defaults to 0
- `end_page` (integer, optional): End page number (starting from 0), defaults to -1 meaning parse all pages

**Return Value**:
```json
{
  "success": true,
  "output_path": "/path/to/output.json",
  "pages": [
    {
      "page_no": 0,
      "page_size": [595, 842],
      "blocks": [
        {
          "type": "text",
          "text": "Text content",
          "bbox": [x, y, x, y]
        }
      ],
      "images": [],
      "tables": [],
      "formulas": []
    }
  ],
  "metadata": {
    "total_pages": 10,
    "author": "Author",
    "title": "Title"
  }
}
```

**Examples**:
```bash
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_json", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output"}}'

# Use specific backend and language
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_json", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output", "backend": "hybrid-auto-engine", "language": "ch"}}'
```

---

## Installation Instructions

### 1. Install MinerU

```bash
# Update pip and install uv
pip install --upgrade pip
pip install uv

# Install MinerU (including all features)
uv pip install -U "mineru[all]"
```

### 2. Verify Installation

```bash
# Check if MinerU is installed successfully
mineru --version

# Test basic functionality
mineru --help
```

### 3. System Requirements

- **Python Version**: 3.10-3.13
- **Operating System**: Linux / Windows / macOS 14.0+
- **Memory**:
  - Using `pipeline` backend: minimum 16GB, recommended 32GB+
  - Using `hybrid/vlm` backend: minimum 16GB, recommended 32GB+
- **Disk Space**: minimum 20GB (SSD recommended)
- **GPU** (optional):
  - `pipeline` backend: supports CPU-only
  - `hybrid/vlm` backend: requires NVIDIA GPU (Volta architecture and above) or Apple Silicon

## Use Cases

1. **Academic Paper Parsing**: Extract structured content such as formulas, tables, and images
2. **Technical Document Conversion**: Convert PDF documents to Markdown for version control and online publishing
3. **OCR Processing**: Process scanned PDFs and garbled PDFs
4. **Multilingual Documents**: Supports OCR recognition for 109 languages
5. **Batch Processing**: Batch convert multiple PDF documents

## Backend Selection Recommendations

- **hybrid-auto-engine** (default): Balanced accuracy and speed, suitable for most scenarios
- **pipeline**: Suitable for CPU-only environments, best compatibility
- **vlm-auto-engine**: Highest accuracy, requires GPU acceleration

## Notes

1. **File Paths**: All paths must be absolute paths
2. **Output Directory**: Non-existent directories will be created automatically
3. **Performance**: Using GPU can significantly improve parsing speed
4. **Page Numbers**: Page numbers start counting from 0
5. **Memory**: Processing large documents may consume more memory

## Troubleshooting

### Common Issues

1. **Installation Failure**:
   - Ensure using Python 3.10-3.13
   - Windows only supports Python 3.10-3.12 (ray does not support 3.13)
   - Using `uv pip install` can resolve most dependency conflicts

2. **Insufficient Memory**:
   - Use `pipeline` backend
   - Limit parsing pages: `start_page` and `end_page`
   - Reduce virtual memory allocation

3. **Slow Parsing Speed**:
   - Enable GPU acceleration
   - Use `hybrid-auto-engine` backend
   - Disable unnecessary features (formulas, tables)

4. **Low OCR Accuracy**:
   - Specify the correct document language
   - Ensure the backend supports OCR (use `pipeline` or `hybrid-*`)

## Related Resources

- MinerU Official Documentation: https://opendatalab.github.io/MinerU/
- MinerU GitHub: https://github.com/opendatalab/MinerU
- Online Demo: https://mineru.net/
