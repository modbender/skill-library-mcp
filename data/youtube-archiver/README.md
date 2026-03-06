# YouTube Archiver

An [OpenClaw](https://github.com/openclaw/openclaw) skill that archives YouTube playlists as markdown notes with AI-generated summaries, full transcripts, and auto-assigned tags.

## What It Does

- Archives YouTube playlists as individual markdown files
- Each video gets: metadata, full transcript, AI summary, and topic tags
- Two-phase pipeline: fast import (metadata only), then enrichment (AI calls)
- Works with any LLM provider (OpenAI, Gemini, Anthropic, Ollama, OpenRouter) or none at all
- Runs on macOS, Linux, and Windows

## Example Output

```markdown
---
title: "How to Self-Host Everything"
channel: "TechChannel"
url: https://www.youtube.com/watch?v=abc123
video_id: abc123
published: 2026-01-15
tags: ["youtube-archive", "self-hosted", "tutorial"]
enriched: true
---

# How to Self-Host Everything

## Summary
## Key Takeaways
- ...

## Transcript
> [!note]- Full Transcript
> ...
```

## Requirements

- Python 3.7+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (`pip install yt-dlp`)
- A browser signed into YouTube (for private playlists)

No other dependencies. All HTTP calls use Python's stdlib `urllib`.

## Install (OpenClaw)

```bash
clawhub install youtube-archiver
```

Or clone this repo into your OpenClaw skills directory.

Then ask your agent: **"Archive my YouTube playlists"** and it will walk you through setup.

## Manual Usage (without OpenClaw)

The scripts work standalone too:

```bash
# Initialize config
python3 scripts/yt-import.py --output ~/YouTube-Archive --init

# Edit .config.json with your playlists and preferences

# Import videos (fast, metadata only)
python3 scripts/yt-import.py --output ~/YouTube-Archive

# Enrich with summaries + transcripts
python3 scripts/yt-enrich.py --output ~/YouTube-Archive --limit 10
```

## Configuration

All preferences live in `.config.json` in the output directory:

```json
{
  "playlists": [
    {"id": "LL", "name": "Liked Videos"},
    {"id": "WL", "name": "Watch Later"}
  ],
  "browser": "chrome",
  "summary": {
    "provider": "openai",
    "model": "gpt-5-mini",
    "api_key_env": "OPENAI_API_KEY"
  },
  "tagging": {
    "provider": "gemini",
    "model": "gemini-3-flash",
    "api_key_env": "GEMINI_API_KEY"
  },
  "tags": [
    "tutorial", "programming", "devops", "ai", "productivity",
    "design", "hardware", "open-source", "career", "self-hosted"
  ]
}
```

Works without any API keys. Summaries are skipped, tags fall back to keyword matching.

## How It Works

1. **Import** pulls playlist metadata via `yt-dlp` using browser cookies for auth
2. Each video becomes a markdown file with YAML frontmatter in a playlist subfolder
3. **Enrichment** extracts transcripts (via yt-dlp subtitles), generates summaries, and assigns tags
4. Idempotent: skips already-archived videos by `video_id`, skips already-enriched notes
5. Lockfile prevents concurrent runs

## Providers

| Provider | Cost | Notes |
|----------|------|-------|
| OpenAI | ~$0.003/video | `gpt-5-mini` recommended |
| Gemini | Free tier | Good for tagging |
| Anthropic | ~$0.005/video | `claude-haiku-4-5` |
| Ollama | Free (local) | Any model, no API key |
| OpenRouter | Varies | Access to all models |
| None | Free | Metadata + transcripts only |

## Platform Notes

- **macOS**: Terminal needs Full Disk Access to read browser cookies
- **Windows**: Cookie extraction can be flaky; exporting a `cookies.txt` file is more reliable
- **Linux**: Works on desktop; headless servers need `cookies_file`

## License

MIT
