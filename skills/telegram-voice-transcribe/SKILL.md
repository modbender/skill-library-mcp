---
name: telegram-voice-transcribe
description: "Transcribe Telegram voice messages and audio notes into text using the OpenAI Whisper API. Use when (1) a user sends a voice message or audio note via Telegram and you need to read or understand its content, (2) you receive a message with a voice file_id in the Telegram message metadata, (3) the user explicitly asks you to transcribe an audio file. Produces the transcript as plain text so you can respond naturally. Requires OPENAI_API_KEY env var and optionally TELEGRAM_BOT_TOKEN for file_id mode. NOT for live audio streams, video transcription, or non-Telegram audio pipelines (though the script supports local files and URLs too)."
---

# telegram-voice-transcribe

Transcribe Telegram voice notes into text via OpenAI Whisper (`whisper-1`).

## Quick Workflow

1. **Detect** a voice message: look for `voice.file_id` or `audio.file_id` in the inbound message metadata.
2. **Run** the transcription script:
   ```bash
   python3 ~/openclaw/skills/telegram-voice-transcribe/scripts/transcribe.py \
     --file-id <file_id> --language es
   ```
3. **Read** the JSON output — `transcript` field contains the text.
4. **Respond** to the user based on the transcript content (treat it like typed text).

## Script Modes

| Mode | Flag | When to use |
|---|---|---|
| Telegram file_id | `--file-id <id>` | Standard case — voice message in Telegram |
| Local file | `--file <path>` | Testing, or file already downloaded |
| URL | `--url <https://...>` | Audio hosted externally |

Always pass `--language es` for Spanish speakers to improve speed and accuracy.

## Output

```json
{"transcript": "Hola, necesito que hagas un cambio en el juego", "language": "es", "duration_s": 4.2}
```

If `error` key is present, surface it to the user and check setup.

## Environment Requirements

- `OPENAI_API_KEY` — required (set via `openclaw configure`)
- `TELEGRAM_BOT_TOKEN` — required for `--file-id` mode

See [references/setup.md](references/setup.md) for full setup, hooks integration, costs, and local Whisper alternative.

## Error Handling

| Error | Fix |
|---|---|
| `OPENAI_API_KEY not set` | Configure key via `openclaw configure --section env` |
| `TELEGRAM_BOT_TOKEN required` | Add bot token to env |
| `openai package not installed` | `pip install openai` |
| Telegram `400 Bad Request` | file_id expired — Telegram file_ids expire after ~48h |
| File too large | Whisper API limit is 25MB; split audio or use local Whisper |
