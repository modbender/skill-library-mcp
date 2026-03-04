---
name: markitdown
description: MarkItDown is a Python utility from Microsoft for converting various files (PDF, Word, Excel, PPTX, Images, Audio) to Markdown. Useful for extracting structured text for LLM analysis.
homepage: https://github.com/microsoft/markitdown
repository: https://github.com/microsoft/markitdown
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "install":
          [
            {
              "id": "venv",
              "kind": "exec",
              "command": "python3 -m venv .venv && .venv/bin/pip install 'markitdown[all]'",
              "label": "Create virtual environment and install markitdown with all dependencies from PyPI",
            },
          ],
      },
  }
---

# MarkItDown Skill

## Description
MarkItDown is a Python utility developed by Microsoft (source: https://github.com/microsoft/markitdown) for converting various files and office documents to Markdown. It allows me to easily extract structured text (including tables, headers, and lists) from complex formats to better understand their content. The conversion happens locally using installed Python libraries.

**Safety Note**: The installation process downloads the `markitdown` package and its dependencies from the official Python Package Index (PyPI). Processing certain formats (like YouTube URLs) requires external network access to fetch the content. Processing local files requires access to the directory where the target files are located.

## Supported Formats
- **Office Documents:** PowerPoint (PPTX), Word (DOCX), Excel (XLSX, XLS).
- **PDF**
- **Images:** Text extraction (OCR) and metadata (EXIF).
- **Audio/Video:** Speech transcription (wav, mp3, Youtube URLs) and EXIF.
- **Web and Text:** HTML, CSV, JSON, XML.
- **Archives and Books:** ZIP archives, EPub.

## Dependencies
The skill installs the utility in a local virtual environment. Most features work out-of-the-box thanks to the `markitdown[all]` dependencies installed via PyPI. For specific formats (audio/video), system libraries (e.g., `ffmpeg`) may be required and must be installed on the host.

## When to Use
- When you need to read, analyze, or extract information from PDF, Word, Excel, or PowerPoint files.
- When document structure is important for the response (e.g., tables or formatted lists).
- If you need to extract text from audio or video files, or "read" an image.

## How to Use

The virtual environment is automatically set up when the skill is installed. You must run the utility from within the skill's folder.

### Conversion with Console Output (STDOUT)
Useful for small files to see the result immediately.
```bash
./.venv/bin/markitdown /path/to/file.pdf
```

### Conversion with File Output
The best option for large documents. Save the result to a `.md` file and read it using the `read` tool.
```bash
./.venv/bin/markitdown /path/to/file.pdf -o /path/to/result.md
```

### Example: Excel Conversion
Navigate to the skill folder (e.g., `cd ~/skills/markitdown`) and execute:
```bash
./.venv/bin/markitdown ~/downloads/report.xlsx -o ~/downloads/report.md
```
After that, you can read the resulting `report.md` file.