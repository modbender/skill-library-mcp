---
name: voice-assistant
description: >
  Windows voice companion for OpenClaw. Custom wake word via Porcupine,
  local STT via faster-whisper, streamed responses over the gateway WebSocket,
  and ElevenLabs TTS with natural chime/thinking sounds. Supports multi-turn
  conversation with automatic follow-up listening, mic suppression to prevent
  feedback, and a system tray with pause/resume. Recommended voices:
  Matilda (XrExE9yKIg1WjnnlVkGX, free tier) or Ivy (MClEFoImJXBTgLwdLI5n,
  paid tier). Fully customizable wake word, voice, hotkey, and silence thresholds.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "os": ["win32"],
        "requires":
          {
            "bins": ["python"],
            "env":
              [
                "GATEWAY_TOKEN",
                "GATEWAY_URL",
                "ELEVENLABS_API_KEY",
                "PORCUPINE_ACCESS_KEY",
              ],
          },
        "primaryEnv": "ELEVENLABS_API_KEY",
      },
  }
---

# Voice Assistant for OpenClaw

A Python companion app that gives OpenClaw a voice. Say a wake word (or press a
hotkey), speak naturally, and hear the AI respond — then keep talking for
multi-turn conversation.

```
Mic → Porcupine wake word → faster-whisper STT → OpenClaw Gateway → ElevenLabs TTS → Speaker
```

## Quick Start

```bash
# 1. Navigate to the skill scripts
cd {baseDir}/scripts

# 2. Create a virtual environment and install dependencies
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# 3. Copy .env.example to .env and fill in your keys
copy .env.example .env

# 4. Run the assistant
venv\Scripts\python src\assistant.py
```

## Requirements

| Service | What you need | Cost |
|---------|--------------|------|
| **OpenClaw gateway** | Running locally on `ws://127.0.0.1:18789` with a gateway token | — |
| **ElevenLabs** | API key + voice ID (free tier works with default voices) | Free+ |
| **Picovoice** | Access key from [picovoice.ai](https://picovoice.ai) (free tier works) | Free |
| **Python** | 3.10+ (tested on 3.14) | — |
| **Microphone** | Any input device | — |

## Configuration (.env)

```ini
# OpenClaw Gateway
GATEWAY_URL=ws://127.0.0.1:18789
GATEWAY_TOKEN=your-gateway-token

# ElevenLabs TTS
ELEVENLABS_API_KEY=your-api-key
ELEVENLABS_VOICE_ID=XrExE9yKIg1WjnnlVkGX  # Matilda (free tier) — or MClEFoImJXBTgLwdLI5n for Ivy (paid)
ELEVENLABS_MODEL_ID=eleven_v3

# Porcupine Wake Word
PORCUPINE_ACCESS_KEY=your-access-key
PORCUPINE_MODEL_PATH=              # path to custom .ppn file (optional)

# Whisper STT
WHISPER_MODEL=base                  # tiny, base, small, medium, large

# Tuning
WAKE_SENSITIVITY=0.7               # 0.0–1.0 (higher = more sensitive)
SILENCE_TIMEOUT=1.5                # seconds of silence to stop recording
HOTKEY=ctrl+shift+k                # global keyboard shortcut
```

## Custom Wake Word

1. Go to [Picovoice Console](https://console.picovoice.ai/)
2. Create a custom wake word (e.g. "Hey Claudia", "Hey OpenClaw")
3. Download the `.ppn` file for your platform
4. Set `PORCUPINE_MODEL_PATH` in `.env` to the file path
5. Without a custom model, falls back to built-in "hey google"

## Personalized Voice Sounds

The assistant plays short audio clips when activated ("Yep!", "Hi!") and while
thinking ("Hmm...", "Let me think..."). Generate these in your chosen ElevenLabs
voice:

```bash
cd {baseDir}/scripts
venv\Scripts\python generate_chime_sounds.py
venv\Scripts\python generate_thinking_sounds.py
```

Re-run these after changing `ELEVENLABS_VOICE_ID`.

## Running in Background

Use `start.bat` to launch without a console window (runs via `pythonw.exe`).
The assistant appears as a system tray icon with Pause/Resume/Quit controls.

For auto-start on Windows, create a shortcut to `start.bat` in `shell:startup`.

## How It Works

1. **Wake** — Porcupine detects the wake word (or user presses hotkey)
2. **Chime** — Plays a random activation sound ("Yep!", "Hi!")
3. **Record** — Records speech until 1.5s of silence (2s grace period for initial silence)
4. **Thinking** — Plays a filler sound ("Hmm...", "Let me think...")
5. **Transcribe** — faster-whisper converts audio to text locally (CPU, int8)
6. **Gateway** — Sends text to OpenClaw gateway via WebSocket, streams response
7. **Speak** — ElevenLabs converts response to speech, plays through speakers
8. **Follow-up** — Automatically listens for 5s after speaking for conversation continuity
9. **Idle** — Returns to wake word listening after 5s of silence

Mic suppression keeps the microphone muted during all speaker output to prevent
feedback loops.

## Detailed Architecture

See [references/architecture.md](references/architecture.md) for source file
breakdown, WebSocket protocol details, and audio pipeline internals.

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for common
issues with mic detection, gateway connection, TTS errors, and wake word tuning.
