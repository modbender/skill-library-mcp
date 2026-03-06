---
name: voice-log
description: Background voice journaling with Soniox realtime STT for OpenClaw. Requires SONIOX_API_KEY. Get/create your Soniox API key at https://soniox.com/speech-to-text. Use when the user asks to start or stop passive speech logging (especially commands like "start voice journal", "start voice log", and "end voice journal"), or asks for a summary/transcript of the last N minutes of conversation.
metadata: {"openclaw":{"requires":{"bins":["node","arecord|rec|ffmpeg"],"env":{"SONIOX_API_KEY":"required - Soniox API key"},"note":"Captures microphone audio locally and streams audio to Soniox realtime STT only while journal is running."}}}
---

# Voice log

Conversation journal that uses Soniox realtime STT in a background daemon that:
- Captures microphone audio continuously.
- Keeps a text-only log file, with live conversation logs bucketed by minute.
- Keeps only the latest 60 minutes (for now).

## Commands

Run from this skill directory:

```bash
npm install
node scripts/voice_journal_ctl.js start
node scripts/voice_journal_ctl.js end
node scripts/voice_journal_ctl.js status
node scripts/voice_journal_ctl.js last 10
```

## OpenClaw trigger handling

When user says:
- `start voice journal`: run `node scripts/voice_journal_ctl.js start`.
- `start voice log`: run `node scripts/voice_journal_ctl.js start`.
- `start voice log ["en","de"]`: run `node scripts/voice_journal_ctl.js start '["en","de"]'`.
- `end voice journal`: run `node scripts/voice_journal_ctl.js end`.
- `summarize what we talked about for last 10 minutes`: run `node scripts/voice_journal_ctl.js last 10`, then summarize the returned text.

Always:
- Reply with only the requested outcome in one short sentence.
- Do not paste raw command output or transcript snippets unless the user explicitly asks for raw transcript/log text.
- If no text exists in range, report that explicitly.
- Never fabricate transcript text.

## Required env

Set:
- `SONIOX_API_KEY` (required)
- Get/create key: https://soniox.com/speech-to-text

Optional:
- None. Runtime settings are intentionally hard-coded except language hints passed in the `start` command.

## Fixed defaults

- Data directory: `./.data` under this skill.
- Soniox websocket endpoint: SDK default (`SONIOX_API_WS_URL`).
- Soniox model: `stt-rt-v4`.
- `last` output cap: `1800` chars by default, or override per command with `--max-chars`.
- Daemon environment: only `SONIOX_API_KEY` (and optional language hints) is forwarded; unrelated host env secrets are not inherited.

## Audio capture defaults

Auto-selects available command by platform. Recommended:
- Linux: `arecord -q -f S16_LE -r 16000 -c 1 -t raw`
- macOS: `sox -q -d -t raw -b 16 -e signed-integer -r 16000 -c 1 -`
