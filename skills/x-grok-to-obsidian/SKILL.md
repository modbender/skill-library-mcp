---
name: x-grok-to-obsidian
description: Export Grok conversations from X (x.com) via browser-network capture and convert them into Obsidian-ready Markdown files. Use when a user wants to back up Grok chat history, preserve User vs Grok turns, and generate Markdown notes with YAML frontmatter (URL, created) from captured JSON.
---

Export Grok conversations in two stages.

## Stage 1 — Capture conversation JSON from X/Grok

Run the browser script in Chrome DevTools Console on `https://x.com/i/grok` while logged in.

Use script: `scripts/export_grok_items_capture.js`

Behavior:
- Intercept only `GrokConversationItemsByRestId` responses (`fetch` + `XHR`)
- Load chat history with multi-pass scrolling
- Open each discovered conversation to trigger backend responses
- Save one JSON file with conversation metadata + ordered item payload

Quick settings (edit at top of script before run):
- `INDEX_PASSES` (default `3`)
- `CAPTURE_PASSES` (default `3`)
- `MAX_CHATS` (`null` = all, or number for test)

Output:
- `grok-network-capture-<timestamp>.json` downloaded by browser

## Stage 2 — Convert JSON to Obsidian Markdown

Run Python converter locally:

```bash
python3 scripts/convert_grok_capture_to_md.py \
  --input /path/to/grok-network-capture-*.json \
  --out /path/to/output-folder
```

Converter defaults:
- Frontmatter fields: `URL`, `created`
- Body starts immediately with `# <title>` (no blank line before header)
- Turn headings: `## User` / `## Grok` (no numbering)
- Turn separator: `---`
- Turn order: reverse API item order (API is newest-first)
- Reasoning/deepsearch omitted by default

Useful flags:
- `--include-reasoning` include `thinking_trace` blocks
- `--separator "---"` customize turn separator
- `--overwrite` overwrite same-title files instead of creating `Title 2.md`

## Notes

- Prefer several index/capture passes because X history rendering is lazy and inconsistent.
- If discovered chat count is unexpectedly low, re-run Stage 1 with higher pass counts.
- Keep scripts generic; avoid user-specific absolute paths.
