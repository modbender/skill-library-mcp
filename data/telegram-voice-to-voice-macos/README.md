# telegram-voice-to-voice-macos

An **OpenClaw skill** for a Telegram voice-to-voice workflow on **macOS Apple Silicon only**.

It handles inbound Telegram voice notes (`.ogg`), transcribes locally with `yap` (Speech.framework), generates a reply, and sends the reply back as a Telegram **voice note** using macOS `say` + `ffmpeg`.

## Requirements

- macOS on Apple Silicon
- `yap` in `PATH` (Speech.framework transcription)
  - https://github.com/finnvoor/yap
- `ffmpeg` in `PATH`

## Compatibility

This skill is **macOS-only** (uses `say` and Speech.framework). The registry cannot enforce OS restrictions, so running it on Linux/Windows will fail at runtime.

## Configuration

### Transcription locale

- If `YAP_LOCALE` is set, it will be used (e.g. `it-IT`, `en-US`).
- If `YAP_LOCALE` is not set, the helper script falls back to the **macOS system locale** (from `defaults read -g AppleLocale`).

### TTS voice

- Default is `SYSTEM` (uses the current macOS system voice).
- You can pass a specific voice name to the TTS helper script if needed.

## Files and paths

- Inbound Telegram audio is typically saved by OpenClaw under:
  - `~/.openclaw/media/inbound/`
- Per-user reply mode state:
  - `voice_state/telegram.json`

## Behavior

- Default reply mode: `voice`
- Toggle per user via Telegram text messages:
  - `/audio off` → reply in text
  - `/audio on` → reply with voice note

## Skill instructions

See `SKILL.md` for the full, canonical behavior description used by OpenClaw.
