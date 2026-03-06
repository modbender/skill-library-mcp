---
name: openclaw-whatsapp-gif
description: Source and send relevant reaction GIFs in WhatsApp chats using safe filters and deterministic ranking. Use when the user asks for a GIF/meme/reaction, or when a short visual reaction is better than plain text for celebration, humor, acknowledgment, empathy, or agreement.
metadata:
  optional_api_keys:
    - TENOR_API_KEY
    - GIPHY_API_KEY
  operational_behavior:
    downloads_remote_media: true
    web_scrape_fallback_default: false
    writes_temp_cache: true
    telemetry_logging_default: false
---

# WhatsApp GIF

Source safe, context-matching GIFs and send exactly one high-quality result to WhatsApp.

## Workflow

1. Decide if GIF is appropriate.
2. Build concise search query from user intent (2-5 words).
3. Run `scripts/find_gif.py` to fetch and rank candidates.
4. Send top result with `message` tool to WhatsApp (prefer local-file payload mode).
5. If send fails, retry once with next candidate.
6. If still failing or no results, send concise fallback text.

## Decision rules

Prefer GIF when:
- The user explicitly asks for GIF/meme/reaction.
- A brief emotional signal is enough.
- Tone benefits from a visual response.

Avoid GIF when:
- Topic is serious/sensitive (medical, legal, conflict, grief).
- Group context is formal or unclear.
- User asked for text-only response.

## Script usage

Use these deterministic helpers:

```bash
python3 skills/openclaw-whatsapp-gif/scripts/find_gif.py "congrats celebration" --limit 5 --json
python3 skills/openclaw-whatsapp-gif/scripts/find_gif.py "great job" --limit 3 --json --target "+1234567890"
python3 skills/openclaw-whatsapp-gif/scripts/send_gif.py "+1234567890" "great job celebration" --json
python3 skills/openclaw-whatsapp-gif/scripts/send_gif.py "+1234567890" "great job celebration" --delivery-mode local --json
python3 skills/openclaw-whatsapp-gif/scripts/send_gif.py "+1234567890" "great job celebration" --payload-only
```

Behavior:
- Reads `TENOR_API_KEY` and/or `GIPHY_API_KEY`.
- Applies safe filtering (`contentfilter=low` / `rating=g` + blocklist).
- Uses retry + backoff for network fetches.
- Ranks by keyword overlap + lightweight preference.
- If no API keys or no provider results, uses built-in safe fallback catalog.
- Optional web scraping fallback is available only when `allowWebScrapeFallback` is enabled in `references/policy.json`.
- Expands intent queries using common reaction aliases.
- Deduplicates repeated URLs across providers.
- Returns URL only (default) or candidate list (`--json`).
- With `--target`, prints a ready-to-send WhatsApp `message` payload in JSON.
- With `send_gif.py --payload-only`, prints only the final message payload for direct tool handoff.
- `send_gif.py` validates media size/type, retries next candidates when a URL is bad, and writes to OS temp cache.
- Telemetry logging is disabled by default and can be enabled by policy or CLI flag.
- Remote URL fallback is disabled by default and must be explicitly enabled in policy.
- Runtime policy is configurable in `references/policy.json`.

## WhatsApp send pattern

Use `message` with:
- `action: "send"`
- `channel: "whatsapp"`
- `target: <chat id/recipient>`
- `media: <gif/mp4 url>`
- `caption: <optional short line>`
- `gifPlayback: true`

If provider rejects `.gif`, retry using next candidate URL (prefer MP4).

## Fallback

If no suitable GIF or delivery fails twice:
- Send concise text preserving intent.
- Do not keep retrying in a loop.

## References

- Provider notes: `references/providers.md`
