---
name: azure-doc-ocr
description: |
  Extract text and structured data from documents using Azure Document Intelligence (formerly Form Recognizer).
  Supports OCR for PDFs, images, scanned documents, handwritten text, CJK languages, tables, forms, invoices,
  receipts, ID documents, business cards, and tax forms. Uses the REST API v4.0 (2024-11-30) with prebuilt
  models for various document types.

  Triggers: OCR, text extraction, Azure Document Intelligence, PDF OCR, image OCR, scanned documents,
  handwriting recognition, CJK text extraction, table extraction, invoice processing, receipt scanning,
  ID document recognition, document parsing, form extraction, Azure Form Recognizer
---

# Azure Document Intelligence OCR

Extract text and structured data from documents using Azure Document Intelligence REST API.

## Quick Start

### 1. Environment Setup

Set your Azure Document Intelligence credentials:

```bash
export AZURE_DOC_INTEL_ENDPOINT="https://your-resource.cognitiveservices.azure.com"
export AZURE_DOC_INTEL_KEY="your-api-key"
```

### 2. Single File OCR

```bash
# Basic text extraction from PDF
python scripts/ocr_extract.py document.pdf

# Extract with layout (tables, structure)
python scripts/ocr_extract.py document.pdf --model prebuilt-layout --format markdown

# Process invoice
python scripts/ocr_extract.py invoice.pdf --model prebuilt-invoice --format json

# OCR from URL
python scripts/ocr_extract.py --url "https://example.com/document.pdf"

# Save output to file
python scripts/ocr_extract.py document.pdf --output result.txt

# Extract specific pages
python scripts/ocr_extract.py document.pdf --pages 1-3,5
```

### 3. Batch Processing

```bash
# Process all documents in a folder
python scripts/batch_ocr.py ./documents/

# Custom output directory and format
python scripts/batch_ocr.py ./documents/ --output-dir ./extracted/ --format markdown

# Use layout model with 8 workers
python scripts/batch_ocr.py ./documents/ --model prebuilt-layout --workers 8

# Filter specific extensions
python scripts/batch_ocr.py ./documents/ --ext .pdf,.png
```

## Model Selection Guide

| Document Type | Recommended Model | Use Case |
|---------------|-------------------|----------|
| General text | `prebuilt-read` | Pure text extraction, any document |
| Structured docs | `prebuilt-layout` | Tables, forms, paragraphs, figures |
| Invoices | `prebuilt-invoice` | Vendor info, line items, totals |
| Receipts | `prebuilt-receipt` | Merchant, items, totals, dates |
| IDs/Passports | `prebuilt-idDocument` | Identity documents |
| Business cards | `prebuilt-businessCard` | Contact information |
| W-2 forms | `prebuilt-tax.us.w2` | US tax documents |
| Insurance cards | `prebuilt-healthInsuranceCard.us` | Health insurance info |

See [references/models.md](references/models.md) for detailed model documentation.

## Supported Input Formats

- **PDF**: `.pdf` (including scanned PDFs)
- **Images**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`
- **URLs**: Direct links to documents

## Output Formats

- **text**: Plain text concatenation of all extracted content
- **markdown**: Structured output with headers and tables (best with layout model)
- **json**: Raw API response with full extraction details

## Features

- **Handwriting Recognition**: Extracts handwritten text alongside printed text
- **CJK Support**: Full support for Chinese, Japanese, Korean characters
- **Table Extraction**: Preserves table structure (use layout model)
- **Multi-page Processing**: Handles documents with multiple pages
- **Concurrent Processing**: Batch script supports parallel processing
- **URL Input**: Process documents directly from URLs

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_DOC_INTEL_ENDPOINT` | Yes | Azure Document Intelligence endpoint URL |
| `AZURE_DOC_INTEL_KEY` | Yes | API subscription key |

## Error Handling

- Invalid credentials: Check endpoint URL and API key
- Unsupported format: Ensure file extension matches supported types
- Timeout: Large documents may need longer processing (max 300s)
- Rate limiting: Reduce concurrent workers for batch processing

## Examples

### Extract text from scanned PDF

```bash
python scripts/ocr_extract.py scanned_contract.pdf --model prebuilt-read
```

### Process invoices with structured output

```bash
python scripts/ocr_extract.py invoice.pdf --model prebuilt-invoice --format json --output invoice_data.json
```

### Batch process with layout analysis

```bash
python scripts/batch_ocr.py ./reports/ --model prebuilt-layout --format markdown --workers 4
```

### Extract specific pages from large document

```bash
python scripts/ocr_extract.py large_doc.pdf --pages 1,3-5,10 --format text
```
