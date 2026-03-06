---
name: voiceclaw
description: "Local voice I/O for OpenClaw agents. Transcribe inbound audio/voice messages using local Whisper (whisper.cpp) and generate voice replies using local Piper TTS. Requires whisper, piper, and ffmpeg pre-installed on the system. All inference runs on-device — no network calls, no cloud APIs, no API keys. Use when an agent receives a voice/audio message and should respond in both voice and text, or when any text response should be synthesized and sent as audio. Triggers on: voice messages, audio attachments, respond in voice, send as audio, speak this, voiceclaw."
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["whisper", "piper", "ffmpeg"] },
        "network": "none",
        "env":
          [
            { "name": "WHISPER_BIN", "description": "Path to whisper binary (default: auto-detected via which)" },
            { "name": "WHISPER_MODEL", "description": "Path to ggml-base.en.bin model file (default: ~/.cache/whisper/ggml-base.en.bin)" },
            { "name": "PIPER_BIN", "description": "Path to piper binary (default: auto-detected via which)" },
            { "name": "VOICECLAW_VOICES_DIR", "description": "Path to directory containing .onnx voice model files (default: ~/.local/share/piper/voices)" }
          ]
      }
  }
---

# VoiceClaw

Local-only voice I/O for OpenClaw agents.

- **STT:** `transcribe.sh` — converts audio to text via local Whisper binary
- **TTS:** `speak.sh` — converts text to speech via local Piper binary
- **Network calls: none** — both scripts run fully offline
- **No cloud APIs, no API keys required**

---

## Prerequisites

The following must be installed on the system before using this skill:

| Requirement | Purpose |
|---|---|
| `whisper` binary | Speech-to-text inference |
| `ggml-base.en.bin` model file | Whisper STT model |
| `piper` binary | Text-to-speech synthesis |
| `*.onnx` voice model files | Piper TTS voices |
| `ffmpeg` | Audio format conversion |

See **README.md** for installation and setup instructions.

---

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `WHISPER_BIN` | auto-detected via `which` | Path to whisper binary |
| `WHISPER_MODEL` | `~/.cache/whisper/ggml-base.en.bin` | Path to Whisper model file |
| `PIPER_BIN` | auto-detected via `which` | Path to piper binary |
| `VOICECLAW_VOICES_DIR` | `~/.local/share/piper/voices` | Directory containing `.onnx` voice model files |

---

## Verify Setup

```bash
which whisper && echo "STT binary: OK"
which piper   && echo "TTS binary: OK"
which ffmpeg  && echo "ffmpeg: OK"
ls "${WHISPER_MODEL:-$HOME/.cache/whisper/ggml-base.en.bin}" && echo "STT model: OK"
ls "${VOICECLAW_VOICES_DIR:-$HOME/.local/share/piper/voices}"/*.onnx 2>/dev/null | head -1 && echo "TTS voices: OK"
```

---

## Inbound Voice: Transcribe

```bash
# Transcribe audio → text (supports ogg, mp3, m4a, wav, flac)
TRANSCRIPT=$(bash scripts/transcribe.sh /path/to/audio.ogg)
```

Override model path:
```bash
WHISPER_MODEL=/path/to/ggml-base.en.bin bash scripts/transcribe.sh audio.ogg
```

---

## Outbound Voice: Speak

```bash
# Step 1: Generate WAV (local Piper — no network)
WAV=$(bash scripts/speak.sh "Your response here." /tmp/reply.wav en_US-lessac-medium)

# Step 2: Convert to OGG Opus (Telegram voice requirement)
ffmpeg -i "$WAV" -c:a libopus -b:a 32k /tmp/reply.ogg -y -loglevel error

# Step 3: Send via message tool (filePath=/tmp/reply.ogg)
```

Override voice directory:
```bash
VOICECLAW_VOICES_DIR=/path/to/voices bash scripts/speak.sh "Hello." /tmp/reply.wav
```

---

## Available Voices

| Voice | Style |
|---|---|
| `en_US-lessac-medium` | Neutral American (default) |
| `en_US-amy-medium` | Warm American female |
| `en_US-joe-medium` | American male |
| `en_US-kusal-medium` | Expressive American male |
| `en_US-danny-low` | Deep American male (fast) |
| `en_GB-alba-medium` | British female |
| `en_GB-northern_english_male-medium` | Northern British male |

---

## Agent Behavior Rules

1. **Voice in → Voice + Text out.** Always respond with both a voice reply and a text reply when a voice message is received.
2. **Include the transcript.** Show *"🎙️ I heard: [transcript]"* at the top of every text reply to a voice message.
3. **Keep voice responses concise.** Piper TTS works best under ~200 words — summarize for audio, include full detail in text.
4. **Local only.** Never use a cloud TTS/STT API. Only the local `whisper` and `piper` binaries.
5. **Send voice before text.** Send the audio file first, then follow with the text reply.

---

## Full Example

```bash
# 1. Transcribe inbound voice message
TRANSCRIPT=$(bash path/to/voiceclaw/scripts/transcribe.sh /path/to/voice.ogg)

# 2. Compose reply and generate audio
RESPONSE="Deployment complete. All checks passed."
WAV=$(bash path/to/voiceclaw/scripts/speak.sh "$RESPONSE" /tmp/reply_$$.wav)
ffmpeg -i "$WAV" -c:a libopus -b:a 32k /tmp/reply_$$.ogg -y -loglevel error

# 3. Send voice + text
# message(action=send, filePath=/tmp/reply_$$.ogg, ...)
# reply: "🎙️ I heard: $TRANSCRIPT\n\n$RESPONSE"
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `whisper: command not found` | Ensure whisper binary is installed and in PATH |
| Whisper model not found | Set `WHISPER_MODEL=/path/to/ggml-base.en.bin` |
| `piper: command not found` | Ensure piper binary is installed and in PATH |
| Voice model missing | Set `VOICECLAW_VOICES_DIR=/path/to/voices/` |
| OGG won't play on Telegram | Ensure `-c:a libopus` flag in ffmpeg command |
