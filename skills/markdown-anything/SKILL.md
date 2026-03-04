---
name: markdown-anything
description: Convert PDF, DOCX, XLSX, PPTX, images, audio, and 25+ file formats to clean Markdown using the Markdown Anything API.
homepage: https://markdownanything.com
metadata:
  clawdbot:
    emoji: "📝"
    requires:
      env: ["MDA_API_TOKEN"]
    primaryEnv: "MDA_API_TOKEN"
    files: ["scripts/*"]
---

# Markdown Anything

Convert files to clean, structured Markdown using the [Markdown Anything](https://markdownanything.com) API. Supports PDF, DOCX, XLSX, PPTX, images, audio, and 25+ formats.

## Setup

Set your API token as an environment variable. Get one from **Settings > API Tokens** in your [Markdown Anything workspace](https://markdownanything.com/workspaces).

```
MDA_API_TOKEN=mda_your_token_here
```

## When to Use

Use the `mda-convert` tool when the user asks to:

- Convert a file to Markdown
- Extract text from a PDF, document, image, or audio file
- Turn a document into Markdown for use in a prompt or workflow

## Tools

### mda-convert

Converts a file to Markdown. Run `scripts/convert.sh` with the file path as the first argument.

**Arguments:**
- `$1` — Path to the file to convert

**Optional environment variables:**
- `MDA_ENHANCED_AI=true` — Use Enhanced AI for scanned documents, images, and audio (costs extra credits)
- `MDA_INCLUDE_METADATA=true` — Include document metadata in the response
- `MDA_OPTIMIZE_TOKENS=true` — Optimize output for LLM token efficiency

**Example:**
```
scripts/convert.sh /path/to/document.pdf
```

The tool outputs the converted Markdown to stdout.

### mda-credits

Check your remaining credit balance. Run `scripts/credits.sh` with no arguments.

**Example:**
```
scripts/credits.sh
```

## Security & Privacy

- Files are sent to `https://markdownanything.com/api/v1/convert` for processing
- Your API token is sent via the `Authorization` header
- No data is stored locally beyond the conversion result
- See [Markdown Anything Privacy Policy](https://markdownanything.com/privacy) for data handling details
