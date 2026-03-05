# shelv

Convert PDFs into structured Markdown filesystems and hydrate them into your workspace for exploration with standard Unix tools.

## What it does

Shelv takes any PDF document — contracts, books, research papers, regulations — and converts it into a well-organized Markdown filesystem. Upload a PDF, wait for processing, then hydrate the result into your OpenClaw workspace as real files you can explore with `ls`, `cat`, `grep`, and `find`.

## Setup

1. Create a Shelv account at [shelv.dev](https://shelv.dev)
2. Generate an API key at **Settings > API Keys**
3. Set the `SHELV_API_KEY` environment variable before running any commands:

```bash
export SHELV_API_KEY="sk_..."
```

## Quick example

```
Upload contract.pdf, wait for it to process, then hydrate it into my workspace so I can search through the clauses.
```

The agent will:

1. Upload the PDF to Shelv
2. Poll until processing completes
3. Download and extract the structured Markdown into `~/.openclaw/workspace/shelves/contract/`
4. Use `find`, `cat`, and `grep` to explore the result

## Requirements

- `curl`, `tar`, `jq`, and `shasum` (or `sha256sum`) must be available on the system
- macOS or Linux

## Links

- [Shelv](https://shelv.dev) — Dashboard and account management
- [Documentation](https://docs.shelv.dev) — Full API docs and guides
