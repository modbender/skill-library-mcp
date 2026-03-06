---
name: summarizerx86
description: Summarize URLs or files with the summarize CLI (x86_64 infrastructure supported).
homepage: https://github.com/speechybubble/summarize
metadata: {"openclaw":{"emoji":"\ud83e\uddfe","requires":{"bins":["summarize"]},"install":[{"id":"npm","kind":"node","package":"@speechybubble/summarize","bins":["summarize"],"label":"Install summarize (npm, speechybubble)"},{"id":"brew","kind":"brew","formula":"speechybubble/tap/summarize","bins":["summarize"],"label":"Install summarize (brew, macOS)","os":["darwin"]}]},"clawdbot":{"emoji":"\ud83e\uddfe","requires":{"bins":["summarize"]},"install":[{"id":"npm","kind":"node","package":"@speechybubble/summarize","bins":["summarize"],"label":"Install summarize (npm, speechybubble)"},{"id":"brew","kind":"brew","formula":"speechybubble/tap/summarize","bins":["summarize"],"label":"Install summarize (brew, macOS)","os":["darwin"]}]}}
---

# Summarize

Fast CLI to summarize URLs, local files, and YouTube links.

## Quick start

```bash
summarize "https://example.com" --model google/gemini-3-flash-preview
summarize "/path/to/file.pdf" --model google/gemini-3-flash-preview
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
```

## Model + keys

Set the API key for your chosen provider:
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- xAI: `XAI_API_KEY`
- Google: `GEMINI_API_KEY` (aliases: `GOOGLE_GENERATIVE_AI_API_KEY`, `GOOGLE_API_KEY`)

Default model is `google/gemini-3-flash-preview` if none is set.

## Useful flags

- `--length short|medium|long|xl|xxl|<chars>`
- `--max-output-tokens <count>`
- `--extract-only` (URLs only)
- `--json` (machine readable)
- `--firecrawl auto|off|always` (fallback extraction)
- `--youtube auto` (Apify fallback if `APIFY_API_TOKEN` set)

## Config

Optional config file: `~/.summarize/config.json`

```json
{ "model": "openai/gpt-5.2" }
```

Optional services:
- `FIRECRAWL_API_KEY` for blocked sites
- `APIFY_API_TOKEN` for YouTube fallback
