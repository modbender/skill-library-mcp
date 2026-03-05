---
description: Lint Markdown files for style issues, broken links, and formatting problems with auto-fix suggestions.
---

# Markdown Linter

Check and improve Markdown file quality.

## Capabilities

- **Style Checks**: Heading levels, list consistency, line length
- **Link Validation**: Check for broken internal/external links
- **Structure Analysis**: TOC generation, heading hierarchy
- **Auto-Fix**: Suggest or apply formatting corrections

## Usage

Ask the agent to:
- "Lint README.md for issues"
- "Check all markdown files in this directory"
- "Fix formatting issues in docs/"
- "Generate a table of contents for this document"

## How It Works

Analyzes Markdown files for common issues:
- Inconsistent heading levels (skipping levels)
- Trailing whitespace, missing blank lines
- Broken relative links
- Inconsistent list markers
- Long lines

Can use `markdownlint-cli` if available, or perform analysis with built-in text processing.

## Requirements

- Optional: `markdownlint-cli` (`npm install -g markdownlint-cli`)
- Works without external tools using text analysis
- No API keys needed
