# x-grok-to-obsidian

Reusable OpenClaw skill to export Grok conversations from X (x.com) and convert them into Obsidian-ready Markdown files.

## What it does

Two-stage workflow:

1. **Capture JSON from X/Grok** in browser (network-level capture of `GrokConversationItemsByRestId`).
2. **Convert captured JSON to Markdown** with role-separated turns (`User` / `Grok`) and Obsidian frontmatter.

## Skill structure

- `SKILL.md` — skill metadata + usage instructions
- `scripts/export_grok_items_capture.js` — browser capture script (run in DevTools)
- `scripts/convert_grok_capture_to_md.py` — JSON → Markdown converter

## Quick usage

### 1) Capture from X/Grok

- Open `https://x.com/i/grok` while logged in.
- Open browser DevTools Console.
- Paste/run `scripts/export_grok_items_capture.js`.
- Download output JSON: `grok-network-capture-<timestamp>.json`.

### 2) Convert to Markdown

```bash
python3 scripts/convert_grok_capture_to_md.py \
  --input /path/to/grok-network-capture-*.json \
  --out /path/to/output-folder
```

## Converter defaults

- Frontmatter: `URL`, `created`, optional `source_tweets`
- Turn headings: `## User` / `## Grok`
- Turn separator: `---`
- API item order reversed to conversation order
- Reasoning/deepsearch excluded by default

## Notes

- X history loading is lazy; multi-pass discovery improves completeness.
- This project intentionally avoids shipping personal data and auth artifacts.

## Troubleshooting / operational notes

### 1) History count is too low (e.g., ~166 only)

- Increase discovery passes in `export_grok_items_capture.js` (`INDEX_PASSES`).
- Keep the tab focused while indexing.
- Re-run once; X history rendering is inconsistent and can return different visible subsets between runs.

### 2) Script hangs during capture loop

- The script uses per-conversation timeout watchdogs to avoid infinite waits.
- If a specific chat times out, it is retried in later passes.
- Blocking dialogs are auto-closed during waits.

### 3) 429 Too Many Requests after many conversations

- X GraphQL endpoint can rate-limit around large runs.
- Script reads `x-rate-limit-reset`, enters cooldown, then resumes automatically.
- The script also applies pacing between requests to reduce burst pressure.

### 4) Browser/tab crashes or script interrupted

- Capture script writes checkpoints into `localStorage`.
- Re-running in the same browser profile/session resumes from checkpoint state (targets + captured data + position).
- On successful completion, checkpoint state is cleared.

### 5) Indexed conversations > captured conversations

- Some items may still fail capture due to transient network issues/rate-limits.
- Re-run capture; checkpoint + retries usually recover most missing items.

## License

MIT
