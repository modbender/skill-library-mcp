---
name: qwen3-tts
description: >
  High-quality text-to-speech using Qwen3-TTS. 10 built-in speakers with
  emotional instruct control, voice cloning (3s of audio), natural-language
  voice design, 10+ languages, persistent named voices, and delivering audio
  via Telegram/WhatsApp as native voice messages. Auto-detects GPU hardware
  (CUDA, ROCm, Intel XPU, CPU).
version: "1.0"
author: daMustermann
repository: https://github.com/daMustermann/claw-qwen3-tts
license: MIT
requires:
  - python>=3.10
  - ffmpeg
  - sox
  - git
tags:
  - tts
  - audio
  - voice
  - speech
  - voice-cloning
  - voice-design
  - telegram
  - whatsapp
  - clawhub
---

# Qwen3-TTS Skill

You have access to a powerful text-to-speech system that can generate human-quality speech with 10 built-in speakers, design new voices from descriptions, clone existing voices from audio samples, and send audio via Telegram/WhatsApp as native voice messages.

## First-Time Setup

If the skill is not yet installed (no `~/clawd/skills/qwen3-tts` directory), run:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/daMustermann/claw-qwen3-tts/main/install.sh)
```

Or if already cloned but not set up (no `.venv/` directory):

```bash
bash ~/clawd/skills/qwen3-tts/install.sh
```

This auto-detects the GPU (CUDA, ROCm, Intel XPU, or CPU-only), creates a Python venv, and installs all dependencies. It takes 5–15 minutes on first run.

## Starting & Stopping the Server

Before any TTS operation, ensure the server is running:

```bash
# Start (idempotent — won't restart if already running)
bash ~/clawd/skills/qwen3-tts/scripts/start_server.sh

# Check health
bash ~/clawd/skills/qwen3-tts/scripts/health_check.sh

# Stop (when done)
bash ~/clawd/skills/qwen3-tts/scripts/stop_server.sh
```

The server runs at `http://localhost:8880`.

---

## Available Models

| Model ID | Use Case | Notes |
|----------|----------|-------|
| `custom-voice-1.7b` | High-quality TTS with built-in speakers — **default** | Best quality, ~5 GB VRAM |
| `custom-voice-0.6b` | Fast TTS with built-in speakers | Lightweight, ~2 GB VRAM |
| `voice-design` | Design new voices from natural language descriptions | Uses VoiceDesign model |
| `base-1.7b` | Basic TTS (auto-corrected to `custom-voice-1.7b`) | Use `custom-voice-*` instead |
| `base-0.6b` | Basic TTS (auto-corrected to `custom-voice-0.6b`) | Use `custom-voice-*` instead |

> **Important:** On the `/v1/audio/speech` endpoint, `base-*` and `voice-design` models are automatically corrected to the corresponding `custom-voice-*` model. Always prefer `custom-voice-1.7b` or `custom-voice-0.6b` for speech generation.

## Built-in Speakers

The `custom-voice-*` models include 10 built-in voices:

> **Chelsie** · **Ethan** · **Aidan** · **Serena** · **Ryan** · **Vivian** · **Claire** · **Lucas** · **Eleanor** · **Benjamin**

You can discover speakers dynamically: `curl http://localhost:8880/v1/speakers`

---

## Capabilities

### 1. Generate Speech from Text

**When to use:** User asks to speak text, read something aloud, generate audio, do a voiceover, narrate, or say something.

```bash
curl -X POST http://localhost:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "custom-voice-1.7b",
    "input": "TEXT_HERE",
    "voice": "default",
    "speaker": "Chelsie",
    "language": "en",
    "instruct": "",
    "response_format": "wav"
  }' \
  --output ~/clawd/skills/qwen3-tts/output/speech.wav
```

**Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `model` | no | `custom-voice-1.7b` | TTS model to use |
| `input` | **yes** | — | The text to synthesize |
| `voice` | no | `default` | `"default"` for built-in speakers, or a **saved voice name** (e.g. `"Angie"`) |
| `speaker` | no | `Chelsie` | Built-in speaker name (only when `voice` is `"default"`) |
| `language` | no | `en` | Language code: en, zh, ja, ko, de, fr, ru, pt, es, it |
| `instruct` | no | `""` | Emotional/style instruction (see below) |
| `response_format` | no | `wav` | Output format: wav, mp3, ogg, flac |
| `speed` | no | `1.0` | Speech speed multiplier |

**Language codes:** `en`, `zh`, `ja`, `ko`, `de`, `fr`, `ru`, `pt`, `es`, `it` — or full names like `English`, `Chinese`, `German`, etc.

**Instruct examples** (controls tone, emotion, and style):
- `"Speak happily and with excitement"`
- `"Whisper softly, as if telling a secret"`
- `"Read this in a calm, professional news anchor tone"`
- `"用愤怒的语气"` (Speak angrily — works in target language too)
- `""` (empty string = neutral default)

**When voice is a saved name:** If you pass `"voice": "Angie"` and a voice named "Angie" exists, the server uses voice cloning with the saved reference audio instead of a built-in speaker. The `speaker` field is ignored in this case.

### 2. Design a New Voice

**When to use:** User wants to create a custom voice, describe how a character should sound, design a persona's voice.

```bash
curl -X POST http://localhost:8880/v1/audio/voice-design \
  -H "Content-Type: application/json" \
  -d '{
    "model": "voice-design",
    "input": "TEXT_TO_SPEAK",
    "voice_description": "DESCRIBE THE VOICE IN NATURAL LANGUAGE",
    "language": "en",
    "response_format": "wav"
  }' \
  --output ~/clawd/skills/qwen3-tts/output/designed.wav
```

**Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `model` | no | `voice-design` | Must be `voice-design` |
| `input` | **yes** | — | Text to synthesize with the designed voice |
| `voice_description` | **yes** | — | Natural language description of the desired voice |
| `language` | no | `en` | Target language |
| `response_format` | no | `wav` | Output format |

**Example descriptions:**
- `"A warm, deep male voice with a slight British accent, calm and authoritative, like a BBC presenter in his 40s"`
- `"A young, energetic female voice, bright and cheerful, with a slight rasp"`
- `"An old wizard with a slow, mysterious, gravelly voice"`

The response includes a `X-Voice-Id` header — capture it to save the voice (see §4).

### 3. Clone a Voice

**When to use:** User provides a reference audio clip and wants to generate new speech in that voice.

```bash
curl -X POST http://localhost:8880/v1/audio/voice-clone \
  -F "reference_audio=@/path/to/reference.wav" \
  -F "reference_text=Transcript of the reference audio" \
  -F "input=New text to speak in the cloned voice" \
  -F "language=en" \
  -F "response_format=wav" \
  --output ~/clawd/skills/qwen3-tts/output/cloned.wav
```

**Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `reference_audio` | **yes** | — | Audio file to clone the voice from |
| `input` | **yes** | — | New text to synthesize in the cloned voice |
| `reference_text` | no | `""` | Transcription of the reference audio (improves quality) |
| `language` | no | `en` | Target language |
| `response_format` | no | `wav` | Output format |

**Guidelines:**
- Minimum **3 seconds** of reference audio
- Recommended **10–30 seconds** for best quality
- Providing an accurate `reference_text` transcription significantly improves results
- Supports **cross-language cloning** (clone from English → speak in Japanese)
- If `reference_text` is empty, uses x-vector-only mode (audio features only)

The response includes a `X-Voice-Id` header — capture it to save the voice (see §4).

### 4. ⭐ CRITICAL: Voice Save Prompting Rules

**YOU MUST FOLLOW THESE RULES:**

1. **After EVERY voice-design or voice-clone request**, ask the user:
   > "Would you like to save this voice for future use? What name should I give it?"

2. **If the user says yes**, capture the `X-Voice-Id` from the response headers and save it:
   ```bash
   curl -X POST http://localhost:8880/v1/voices \
     -H "Content-Type: application/json" \
     -d '{
       "name": "USER_CHOSEN_NAME",
       "source_voice_id": "VOICE_ID_FROM_X_VOICE_ID_HEADER",
       "description": "Description of the voice",
       "tags": ["tag1", "tag2"],
       "language": "en"
     }'
   ```

3. **When user requests TTS with a voice name** (e.g. "say this with Angie"):
   - Use `"voice": "Angie"` in the `/v1/audio/speech` request
   - The server automatically loads the saved reference audio and uses voice cloning
   - If the name doesn't exist, tell the user and offer to design or clone one

4. **When user asks to list voices:**
   ```bash
   curl http://localhost:8880/v1/voices
   ```
   Present the results as a formatted list with name, description, source, language, tags, and usage count. Voices are sorted by usage count (most used first).

5. **When user asks to delete a voice:** Confirm with the user first, then:
   ```bash
   curl -X DELETE http://localhost:8880/v1/voices/VOICE_NAME
   ```

6. **When user asks to rename a voice:**
   ```bash
   curl -X PATCH http://localhost:8880/v1/voices/OLD_NAME \
     -H "Content-Type: application/json" \
     -d '{"name": "NEW_NAME"}'
   ```

7. **When user asks to update a voice's metadata** (description, tags, language):
   ```bash
   curl -X PATCH http://localhost:8880/v1/voices/VOICE_NAME \
     -H "Content-Type: application/json" \
     -d '{"description": "Updated description", "tags": ["new", "tags"]}'
   ```

8. **Voice names are case-insensitive** but stored in the casing the user provided.

9. **No duplicate names allowed.** If a name already exists, the save will fail (409). Ask the user for a different name or offer to delete the existing one first.

10. **Voice profiles are stored locally** in `~/clawd/skills/qwen3-tts/voices/` and persist across server restarts. Each voice consists of:
    - `<name>.json` — metadata
    - `<name>.pt` — embedding tensor
    - `<name>_sample.wav` — reference audio sample (used for re-cloning)

### 5. Convert Audio Formats

**When to use:** User needs audio in a specific format, or you need to prepare audio for messaging.

```bash
curl -X POST http://localhost:8880/v1/audio/convert \
  -F "audio=@input.wav" \
  -F "target_format=mp3" \
  --output output.mp3
```

Supported formats: **wav**, **mp3**, **ogg** (Opus), **flac**

You can also use the shell script directly:
```bash
bash ~/clawd/skills/qwen3-tts/scripts/convert_to_ogg_opus.sh input.wav output.ogg
```

### 6. Send via Telegram (PTT Voice Message)

**When to use:** User is interacting via Telegram, or explicitly asks to send audio to a Telegram chat.

```bash
curl -X POST http://localhost:8880/v1/audio/send/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "audio_file": "/path/to/audio.wav",
    "chat_id": "CHAT_ID",
    "bot_token": "BOT_TOKEN",
    "caption": "Optional caption"
  }'
```

- `bot_token` is optional if already configured in `config.json`
- Audio is auto-converted to OGG/Opus and sent via Telegram's `sendVoice` API
- Displays as a native PTT waveform voice message in the chat

### 7. Send via WhatsApp (PTT Voice Message)

**When to use:** User is interacting via WhatsApp, or explicitly asks to send audio there.

```bash
curl -X POST http://localhost:8880/v1/audio/send/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "audio_file": "/path/to/audio.wav",
    "phone_number_id": "PHONE_ID",
    "recipient": "+14155551234",
    "access_token": "ACCESS_TOKEN"
  }'
```

- `phone_number_id` and `access_token` are optional if already configured in `config.json`
- Audio is auto-converted to OGG/Opus and sent as a native WhatsApp voice message

### 8. Discovery Endpoints

Use these to dynamically discover available models and speakers:

```bash
# List all available TTS models
curl http://localhost:8880/v1/models

# List built-in speakers
curl http://localhost:8880/v1/speakers

# Server health check (device info, voice count, version)
curl http://localhost:8880/health
```

---

## How to Respond

**After generating speech:**
1. Tell the user the audio has been generated
2. Provide the output file path
3. If it was voice-design or voice-clone, **always ask to save the voice** (Rule §4.1)
4. If the user is on Telegram/WhatsApp, offer to send it as a voice message

**After saving a voice:**
- Confirm the name and tell the user they can use it anytime with that name
- Example: *"Voice saved as 'Captain Hook'! You can reference it anytime with `voice: Captain Hook`."*

**After sending via Telegram/WhatsApp:**
- Confirm successful delivery

**When choosing a speaker:** If the user doesn't specify, default to `"Chelsie"`. If they describe the kind of voice they want (but not a full voice-design request), pick the most fitting built-in speaker.

**When choosing a model:** Default to `custom-voice-1.7b`. Only use `custom-voice-0.6b` if the user asks for speed, or if the system has limited VRAM/memory.

---

## Configuration

The agent can update `~/clawd/skills/qwen3-tts/config.json` to set:
- **Telegram:** bot token and default chat ID
- **WhatsApp:** phone number ID and access token
- **Default model:** `custom-voice-1.7b` or `custom-voice-0.6b`
- **Default audio format:** wav, mp3, ogg, flac
- **Device override:** auto, cuda:0, xpu:0, cpu

If `config.json` doesn't exist, copy the template:
```bash
cp ~/clawd/skills/qwen3-tts/config.json.template ~/clawd/skills/qwen3-tts/config.json
```
