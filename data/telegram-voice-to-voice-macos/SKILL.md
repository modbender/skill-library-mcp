---
name: telegram-voice-to-voice-macos
description: "Telegram voice-to-voice for macOS Apple Silicon: transcribe inbound .ogg voice notes with yap (Speech.framework) and reply with Telegram voice notes via say+ffmpeg. Not compatible with Linux/Windows."
metadata: {"openclaw":{"os":["darwin"],"requires":{"bins":["yap","ffmpeg","say","defaults"]}}}
---

# Telegram voice-to-voice (macOS Apple Silicon only)

This is an **OpenClaw skill**.

## Requirements

- macOS on Apple Silicon.
- `yap` CLI available in `PATH` (Speech.framework transcription).
  - Project: https://github.com/finnvoor/yap (by finnvoor)
- `ffmpeg` available in `PATH`.

## Compatibility note (important)

This skill is **macOS-only** (uses `say` + Speech.framework). The skill registry cannot enforce OS restrictions, so installing/running it on Linux/Windows will result in runtime failures.

## Persistent reply mode (voice vs text)

Store a small per-user preference file in the workspace:

- State file: `voice_state/telegram.json`
- Key: Telegram sender user id (string)
- Values:
  - `"voice"` (default): reply with a Telegram voice note
  - `"text"`: reply with a single text message

If the file does not exist or the sender id is missing: assume `"voice"`.

### Toggle commands

If an inbound **text** message is exactly:

- `/audio off` → set state to `"text"` and confirm with a short text reply.
- `/audio on` → set state to `"voice"` and confirm with a short text reply.

## Getting the inbound audio (.ogg)

Telegram voice notes often show up as `<media:audio>` in message text.
OpenClaw saves the attachment to disk (typically `.ogg`) under:

- `~/.openclaw/media/inbound/`

Recommended approach:

1) If the inbound message context includes an attachment path, use it.
2) Otherwise, take the most recent `*.ogg` from `~/.openclaw/media/inbound/`.

## Transcription

Default locale: **macOS system locale**.

Optional env:

- `YAP_LOCALE` — override the transcription locale (e.g. `it-IT`, `en-US`).

Preferred:

- `yap transcribe --locale "${YAP_LOCALE:-<system>}" <path.ogg>`
  - If `YAP_LOCALE` is not set, the helper script will use the macOS system locale (from `defaults read -g AppleLocale`).

If transcription fails or is empty: ask the user to repeat or send text.

Helper script:

- `scripts/transcribe_telegram_ogg.sh [path.ogg]`

## Reply behavior

### Mode: voice (default)

Voice default: **SYSTEM** (uses the current macOS system voice). You can override by passing a specific voice name to the helper script.

1) Generate the reply text.
2) Convert reply text to an OGG/Opus voice note using:

- `scripts/tts_telegram_voice.sh "<reply text>" [SYSTEM|VoiceName]`

The script prints the generated `.ogg` path to stdout.

3) Send the `.ogg` back to Telegram as a **voice note** (not a generic audio file):

- use the `message` tool with `asVoice: true` and `media: <path.ogg>`
- optionally set `replyTo` to thread the response

Notes:

- Use `SYSTEM` to rely on the current macOS system voice (recommended).

### Mode: text

Reply with a single text message:

- `Transcription: <...>`
- `Reply: <...>`
