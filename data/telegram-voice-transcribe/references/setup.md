# Setup Guide — telegram-voice-transcribe

## Prerequisites

```bash
pip install openai          # Whisper API client
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key (platform.openai.com) |
| `TELEGRAM_BOT_TOKEN` | Only for `--file-id` mode | Bot token from @BotFather |

Add to OpenClaw Gateway environment:
```bash
openclaw configure --section env
# OPENAI_API_KEY=sk-...
# TELEGRAM_BOT_TOKEN=bot123456:ABC...
```

Or export in your shell / `.env` file.

## OpenClaw Telegram Integration

When a user sends a voice message, OpenClaw forwards the raw Telegram update.
The inbound message metadata includes a `voice` or `audio` object with a `file_id`.

### How to wire it up

OpenClaw supports **pre-processing hooks** in `~/openclaw/config/hooks.js` (if available).
Add a voice handler that calls `transcribe.py` before the message reaches the agent:

```js
// hooks.js — example pre-process hook
const { execFileSync } = require('child_process');
const path = require('path');
const SCRIPT = path.resolve(__dirname, '../skills/telegram-voice-transcribe/scripts/transcribe.py');

module.exports = {
  async beforeMessage(msg) {
    const voice = msg.raw?.voice || msg.raw?.audio;
    if (!voice) return msg;                        // not a voice message
    try {
      const out = execFileSync('python3', [SCRIPT, '--file-id', voice.file_id], {
        env: { ...process.env },
        timeout: 30_000,
      });
      const { transcript, language, duration_s } = JSON.parse(out);
      // Prepend transcript to message text so the agent sees it
      msg.text = `[🎙 Transcripción (${language}, ${duration_s}s)]: ${transcript}`;
    } catch (e) {
      msg.text = '[Error al transcribir el audio]';
    }
    return msg;
  }
};
```

### Without hooks (manual agent workflow)

If pre-processing hooks are not available, the agent uses this skill reactively:
when it receives a voice message it calls `transcribe.py` itself via `exec`.

The agent needs the `file_id` from the inbound message metadata — this is available
in the `[System Message]` context when the Telegram channel is configured.

## Script Usage Examples

```bash
# Transcribe by Telegram file_id
python3 transcribe.py --file-id BQACAgIAAx...

# Transcribe local file
python3 transcribe.py --file recording.ogg

# Force Spanish language (faster + more accurate for ES)
python3 transcribe.py --file-id BQACAgI... --language es

# Output
# {"transcript": "Hola, qué tal va el juego?", "language": "es", "duration_s": 3.1}
```

## Costs (OpenAI Whisper API)

- **$0.006 / minute** of audio
- A typical 10-second voice note ≈ $0.001
- 100 voice notes/day of ~15s each ≈ $0.15/day

## Local Whisper (Free Alternative)

Replace the OpenAI call in `transcribe.py` with:

```python
import whisper
model = whisper.load_model("small")   # or "base", "medium", "large"
result = model.transcribe(audio_path, language=language)
return {"transcript": result["text"].strip(), "language": result["language"], "duration_s": 0}
```

Install: `pip install openai-whisper torch`
Note: Requires ~1-2GB RAM for `small` model; GPU optional but speeds things up.
