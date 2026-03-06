---
title: mdnew_to_mdx.sh
description: Convert docs pages into cleaned MDX via markdown.new.
updatedAt: 2026-02-25
---

# `mdnew_to_mdx.sh`

Converts a webpage into local `.mdx` using Cloudflare `markdown.new`, then cleans common docs-site UI artifacts.

## Location

- Script path: `scripts/mdnew_to_mdx.sh`

## Usage

```bash
scripts/mdnew_to_mdx.sh <source_url> <output_mdx_path>
```

Example:

```bash
scripts/mdnew_to_mdx.sh \
  https://docs.convex.dev/agents/agent-usage \
  docs/convex/agent-usage.mdx
```

## What it does

1. Fetches `https://markdown.new/<source_url>`.
2. Extracts only the `Markdown Content` section.
3. Reads source `title` and `description` from upstream frontmatter (if present).
4. Writes normalized frontmatter:
   - `title`
   - `description`
   - `sourceUrl`
   - `retrievedAt` (UTC date, `YYYY-MM-DD`)
5. Removes common artifacts:
   - "Skip to main content"
   - docs nav/header copy text
   - auto-generated on-page anchor list items
   - Docusaurus direct-link anchor fragments inside headings
6. Collapses excessive blank lines.

## Notes

- Requires: `bash`, `curl`, `awk`, `mktemp`.
- Overwrites output file if it already exists.
- Rerun the script to refresh local MDX when source docs change.
