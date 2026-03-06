---
name: pdf_compressor
description: "Compresses a given PDF file to reduce its size."
version: "1.0.0"
runtime: shell
entrypoint: "uv run src/main.py"

inputs:
  - name: pdf_path
    type: string
    description: "The absolute path to the PDF file to be compressed."
    required: true
  - name: compression_level
    type: integer
    description: "Compression level (1=Low, 2=Medium, 3=High). Defaults to 2."
    required: false
    default: 2

output:
  type: json
  description: "JSON object containing compression success status and data like the compressed file path, original size, and compressed size."
---

# PDF Compressor Skill

This skill is designed to compress a PDF file to reduce its size using standard optimization parameters. It is powered by PyMuPDF and offers three tunable compression levels depending on the user's needs.

## Usage Guide
When using this skill to compress a PDF, you should provide the `pdf_path` (absolute path to the target PDF) and optionally the `compression_level` (from 1 to 3). The skill will return the output path of the newly created compressed PDF.

- **Level 1 (Low)**: Basic compression, fastest.
- **Level 2 (Medium)**: Optimized compression, balanced speed and file size reduction (Default).
- **Level 3 (High)**: Deep optimization for maximum file size reduction.
