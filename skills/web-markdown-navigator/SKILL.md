---
name: web-markdown-navigator
description: Fetch webpages and return clean markdown instead of raw HTML. Use for URL reading, extraction, and summarization tasks where the user wants markdown output; use browser fallback for JS-heavy/SPA pages when extraction is thin.
---

# Web Markdown Navigator

Use this skill for deterministic URL → markdown extraction.

## Quick flow

1. Run script:
   - `cd /Users/pedrogonzalez/clawd/skills/web-markdown-navigator/scripts`
   - `node fetch-markdown.mjs "<url>" --max-chars 50000`
2. If exit code `0`, return markdown output.
3. If exit code `3` or `4`, or output is thin/boilerplate, use `browser` tool fallback to capture rendered content and return markdown summary.

## Script

`node scripts/fetch-markdown.mjs <url> [--max-chars N] [--timeout-ms N] [--json]`

Behavior:
- Layer 1: Fetch HTML + Mozilla Readability + Turndown markdown conversion.
- Layer 2: Fallback plain-text markdown if extraction is too thin.
- URL safety checks block localhost/private literal IPv4 hosts.

## Output requirements

- Return markdown only (no raw HTML dump).
- Preserve source URL in response.
- If truncated, include truncation note.
- If fallback was needed, mention method used (`readability` or `fallback-text`).

## Error handling

- `1` bad args
- `2` invalid/blocked URL
- `3` network/fetch/content-type failure
- `4` extraction failure/thin output

For extended notes and troubleshooting, read:
- `/Users/pedrogonzalez/clawd/skills/web-markdown-navigator/references/usage.md`
