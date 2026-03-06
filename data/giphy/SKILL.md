---
name: giphy-gif
description: Search and send contextual Giphy GIFs in Discord. Use when a user asks for a GIF or when a brief visual reaction (celebration, humor, emotion) improves the flow.
---

# Giphy GIF Search

Find a relevant GIF from Giphy and send it naturally in Discord.

## Behavior Rules

- Send GIFs when explicitly requested.
- Also allow proactive GIFs (without explicit request) when the moment clearly fits: celebration, shared humor, or strong emotional beats.
- Keep proactive usage occasional (at most one GIF for a moment, avoid back-to-back GIF-only replies).
- Prefer text-only in serious or information-dense conversation.
- Keep results safe-for-work (`rating=g`).

## API Key (Easy Setup)

This skill reads only one variable: `GIPHY_API_KEY`.

### Option A: Temporary (current shell session)

```bash
export GIPHY_API_KEY="your-api-key"
```

### Option B: Persistent for OpenClaw (recommended)

Add to `~/.openclaw/.env`:

```bash
GIPHY_API_KEY=your-api-key
```

Then restart OpenClaw so the environment is reloaded.

### Validation

- If `GIPHY_API_KEY` is present, the skill works.
- If missing, ask the user to set it and retry.

## Workflow

1. Build a Giphy Search API URL with user intent as query.
2. URL-encode the query text.
3. Request one result from Giphy.
4. Extract the first GIF page URL from `data[0].url`.
5. Send that URL to Discord.

## API Request Template

Use this endpoint shape:

`https://api.giphy.com/v1/gifs/search?api_key=<KEY>&q=<ENCODED_QUERY>&limit=1&rating=g&lang=en`

## Output Rule

- If a GIF URL is found: send only the URL (Discord auto-embeds).
- If no result is found: send a short fallback text and ask for a better keyword.

## Good Query Examples

- `happy dance`
- `facepalm reaction`
- `mind blown`
- `awkward silence`

## Fallback Message

"I couldn’t find a GIF with the vibe you’re looking for. Could you give me a bit more specific keywords?"
