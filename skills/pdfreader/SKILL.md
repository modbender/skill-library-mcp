# PDF Reader Skill for OpenClaw

Extract and read text from PDF files using PyMuPDF.

## Installation

```powershell
pip install pymupdf
```

## Usage

```powershell
# Extract text (first 10 pages by default)
python pdf_reader.py "path/to/file.pdf" 10

# Output to JSON file (for reading)
python pdf_reader.py "path/to/file.pdf" 10 --output=extracted.json

# Read specific number of pages
python pdf_reader.py "path/to/file.pdf" 5
```

## Features

- Extracts text from any PDF
- Supports large files
- Outputs JSON for AI reading
- Handles encoding issues
- Shows metadata (title, author, etc.)

## Security Restrictions

For safety, the script enforces:
- **Input files:** Must be `.pdf` files within the current working directory
- **Output files:** Must be `.json` files within the current working directory
- No path traversal (`../`) allowed
- Files can only be read/written in the directory where the script runs

## Files

- `pdf_reader.py` - Main Python script
- `SKILL.md` - This documentation
