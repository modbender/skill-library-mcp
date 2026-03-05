---
name: url2pdf
description: Convert URL to PDF suitable for mobile reading.
author: guoqiao
metadata: {"openclaw":{"always":true,"emoji":"🦞","homepage":"https://clawhub.ai/guoqiao/url2pdf","os":["darwin","linux","win32"],"requires":{"bins":["uv"]}}}
triggers:
- "/url2pdf <url>"
- "Save this url as pdf"
- "Convert to pdf for mobile"
---

# URL to PDF

Given a url for a webpage, convert it to pdf suitable for mobile reading.

See [examples](https://github.com/guoqiao/skills/tree/main/url2pdf/examples).

## Requirements

- `uv`

## Installation

playwright itself will be installed by uv automatically, while it also needs browser to be installed:
```
uvx playwright install chromium
```

## Usage

```bash
uv run --script ${baseDir}/url2pdf.py "${url}"
```
Path to pdf will be printed to stdout.

### Agent Instructions

1. **Run the script**: Pass the url to be converted as an argument.
2. **Handle Output**: The script will output a path to a pdf file.
Use the `message` tool to send the pdf file to the user as a document message:
```json
{
   "action": "send",
   "filePath": "<filepath>"
}
```