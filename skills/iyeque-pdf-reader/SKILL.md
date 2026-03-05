---
name: pdf-reader
description: Extract text, search inside PDFs, and produce summaries.
homepage: "https://pymupdf.readthedocs.io"
metadata:
  {
    "openclaw":
      {
        "emoji": "📄",
        "requires": { "bins": ["python3"], "pip": ["PyMuPDF"] },
        "install":
          [
            {
              "id": "pymupdf",
              "kind": "pip",
              "package": "PyMuPDF",
              "label": "Install PyMuPDF",
            },
          ],
        "version": "1.1.0",
      },
  }
---

# PDF Reader Skill

The `pdf-reader` skill provides functionality to extract text and retrieve metadata from PDF files using PyMuPDF (fitz).

## Tool API

The skill provides two commands:

### extract
Extracts plain text from the specified PDF file.

- **Parameters:**
  - `file_path` (string, required): Path to the PDF file to extract text from.
  - `--max_pages` (integer, optional): Maximum number of pages to extract.

**Usage:**
```bash
python3 skills/pdf-reader/reader.py extract /path/to/document.pdf
python3 skills/pdf-reader/reader.py extract /path/to/document.pdf --max_pages 5
```

**Output:** Plain text content from the PDF.

### metadata
Retrieve metadata about the document.

- **Parameters:**
  - `file_path` (string, required): Path to the PDF file.

**Usage:**
```bash
python3 skills/pdf-reader/reader.py metadata /path/to/document.pdf
```

**Output:** JSON object with PDF metadata including:
- `title`: Document title
- `author`: Document author
- `subject`: Document subject
- `creator`: Application that created the PDF
- `producer`: PDF producer
- `creationDate`: Creation date
- `modDate`: Modification date
- `format`: PDF format version
- `encryption`: Encryption info (if any)

## Implementation Notes

- Uses **PyMuPDF** (imported as `pymupdf`) for fast, reliable PDF processing
- Supports encrypted PDFs (will return error if password required)
- Handles large PDFs efficiently with `max_pages` option
- Returns structured JSON for metadata command

## Example

```bash
# Extract text from first 3 pages
python3 skills/pdf-reader/reader.py extract report.pdf --max_pages 3

# Get document metadata
python3 skills/pdf-reader/reader.py metadata report.pdf
# Output:
# {
#   "title": "Annual Report 2024",
#   "author": "John Doe",
#   "creationDate": "D:20240115120000",
#   ...
# }
```

## Error Handling

- Returns error message if file not found or not a valid PDF
- Returns error if PDF is encrypted and requires password
- Gracefully handles corrupted or malformed PDFs
