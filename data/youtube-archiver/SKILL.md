---
name: youtube-archiver
description: Archive YouTube playlists into markdown notes with metadata, transcripts, AI summaries, and tags. Use when a user asks to import/sync YouTube playlists, archive Watch Later or Liked videos, enrich YouTube notes, batch process video notes, or automate recurring YouTube-to-markdown sync jobs with cron.
---

# YouTube Archiver

Use this skill to import YouTube playlists into markdown files and optionally enrich notes with transcript, summary, and tagging.

## Requirements

- Python 3.7+
- `yt-dlp` (`pip install yt-dlp` or `brew install yt-dlp`)
- A browser signed into YouTube (for private playlists like Liked/Watch Later)
- **macOS**: terminal needs Full Disk Access to read browser cookies
- **Windows**: browser cookie extraction can be flaky; `cookies_file` export is the safer path
- **Linux**: works on desktop installs; headless servers need `cookies_file`

## First-run setup flow (interactive)

If no config exists at `<output>/.config.json`, ask these questions before running scripts.

### Required questions

1. Where should archived notes be stored?
   - Default: `./YouTube-Archive`
2. Which playlists should be archived?
   - Accept playlist IDs or URLs
   - Default: `LL` (Liked Videos), `WL` (Watch Later)
3. Which browser is signed into YouTube for cookie auth?
   - Default: `chrome`

### Optional enrichment questions

Ask only if the user wants summaries/tags.

1. Generate AI summaries? (yes/no)
2. Summary provider? (`openai`, `gemini`, `anthropic`, `openrouter`, `ollama`, `none`)
3. Summary model name?
4. API key env var name?
5. Enable auto-tagging? (yes/no)
6. Tagging provider/model/env var?
7. Keep default tags or define custom vocabulary?

## First-run execution sequence

1. Run init:
   - `python3 <skill>/scripts/yt-import.py --output <output-dir> --init`
2. Edit `<output-dir>/.config.json` from the user’s answers.
3. Verify auth with dry run:
   - `python3 <skill>/scripts/yt-import.py --output <output-dir> --dry-run`
4. Run real import.
5. Run enrichment (optional):
   - `python3 <skill>/scripts/yt-enrich.py --output <output-dir> --limit 10`

## One-shot quick start

Use this for immediate manual sync:

```bash
python3 <skill>/scripts/yt-import.py --output <output-dir>
python3 <skill>/scripts/yt-enrich.py --output <output-dir> --limit 10
```

Useful import flags:
- `--dry-run`
- `--playlist <ID>` (repeatable)
- `--no-summary`
- `--no-tags`
- `--cookies <path/to/cookies.txt>`
- `--browser <name>`

Useful enrich flags:
- `--dry-run`
- `--limit <N>`
- `--strict-config`

## Idempotency and safety behavior

- Import skips already archived videos by `video_id`.
- Filenames include video ID: `Title [video_id].md`.
- Enrichment skips notes where frontmatter has `enriched: true`.
- Lockfile prevents concurrent runs: `<output-dir>/.yt-archiver.lock`.

## Automation with cron (single-agent default)

Offer cron only after one successful manual run.

Example schedule (daily 11:00):

1. Import new videos
2. Enrich a bounded batch

Example task text:

- `Run yt-import.py for <output-dir>, then run yt-enrich.py --limit 10 for the same output.`

Keep it single-agent by default. Do not assume multi-agent routing.

## Troubleshooting and provider details

Read these references when needed:

- Provider setup, model suggestions, cost: `references/providers.md`
- Common failures and fixes: `references/troubleshooting.md`
- Default summary prompt template: `references/default-summary-prompt.md`
