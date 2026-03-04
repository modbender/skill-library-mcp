---
name: paddleocr-doc-parsing
description: Parse documents using PaddleOCR's API. Supports both sync and async modes for images and PDFs.
homepage: https://www.paddleocr.com
metadata:
  {
    "openclaw":
      {
        "emoji": "📄",
        "os": ["darwin", "linux"],
        "requires":
          {
            "bins": ["curl", "base64", "jq", "python3"],
            "env": ["PADDLEOCR_ACCESS_TOKEN", "PADDLEOCR_API_URL"],
          },
      },
  }
---

# PaddleOCR Document Parsing

Parse images and PDF files using PaddleOCR's API. Supports both synchronous and asynchronous parsing modes with structured output.

## Resource Links

| Resource              | Link                                                                           |
| --------------------- | ------------------------------------------------------------------------------ |
| **Official Website**  | [https://www.paddleocr.com](https://www.paddleocr.com)                                     |
| **API Documentation** | [https://ai.baidu.com/ai-doc/AISTUDIO/Cmkz2m0ma](https://ai.baidu.com/ai-doc/AISTUDIO/Cmkz2m0ma)         |
| **GitHub**            | [https://github.com/PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) |

## Key Features

- **Multi-format support**: PDF and image files (JPG, PNG, BMP, TIFF)
- **Two parsing modes**:
  - **Sync mode**: Fast response for small files (<600s timeout)
  - **Async mode**: For large files with progress polling
- **Layout analysis**: Automatic detection of text blocks, tables, formulas
- **Multi-language**: Support for 110+ languages
- **Structured output**: Markdown format with preserved document structure

## Setup

1. Visit [PaddleOCR](https://www.paddleocr.com) to obtain your API credentials
2. Set environment variables:

```bash
export PADDLEOCR_ACCESS_TOKEN="your_token_here"
export PADDLEOCR_API_URL="https://your-endpoint.aistudio-app.com/layout-parsing"

# Optional: For async mode
export PADDLEOCR_JOB_URL="https://your-job-endpoint.aistudio-app.com/api/v2/ocr/jobs"
export PADDLEOCR_MODEL="PaddleOCR-VL-1.5"
```

## Usage Examples

### Sync Mode (Default)

For small files and quick processing:

```bash
# Parse local image
{baseDir}/paddleocr_parse.sh document.jpg

# Parse PDF
{baseDir}/paddleocr_parse.sh -t pdf document.pdf

# Parse from URL
{baseDir}/paddleocr_parse.sh https://example.com/document.jpg

# Save output to file
{baseDir}/paddleocr_parse.sh -o result.json document.jpg

# Verbose output
{baseDir}/paddleocr_parse.sh -v document.jpg
```

### Async Mode

For large files with progress tracking:

```bash
# Parse large PDF with async mode
{baseDir}/paddleocr_parse.sh --async large-document.pdf

# Parse from URL with async mode
{baseDir}/paddleocr_parse.sh --async -t pdf https://example.com/doc.pdf

# Save async result to file
{baseDir}/paddleocr_parse.sh --async -o result.json document.pdf
```

### Using Python Script Directly

```bash
# Sync mode
python3 {baseDir}/paddleocr_parse.py document.jpg

# Async mode
python3 {baseDir}/paddleocr_parse.py --async-mode document.pdf

# With output file
python3 {baseDir}/paddleocr_parse.py -o result.json --async-mode document.pdf
```

## Response Structure

```json
{
  "logId": "unique_request_id",
  "errorCode": 0,
  "errorMsg": "Success",
  "result": {
    "layoutParsingResults": [
      {
        "prunedResult": [...],
        "markdown": {
          "text": "# Document Title\n\nParagraph content...",
          "images": {}
        },
        "outputImages": [...],
        "inputImage": "http://input-image"
      }
    ],
    "dataInfo": {...}
  }
}
```

**Important Fields:**

- **`prunedResult`** - Contains detailed layout element information including positions, categories, etc.
- **`markdown`** - Stores the document content converted to Markdown format with preserved structure and formatting.

## Mode Selection Guide

| Use Case | Recommended Mode |
|----------|-----------------|
| Small images (< 10MB) | Sync |
| Single page PDFs | Sync |
| Large PDFs (> 10MB) | Async |
| Multi-page documents | Async |
| Batch processing | Async |
| Quick text extraction | Sync |

## Error Handling

The script will exit with code 1 and print error message for:
- Missing required environment variables
- File not found
- API authentication failures
- Invalid JSON responses
- API error codes (non-zero)

## Quota Information

See official documentation: https://ai.baidu.com/ai-doc/AISTUDIO/Xmjclapam
