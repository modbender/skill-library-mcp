# 🎤 Qwen3-TTS — OpenClaw Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ClawHub](https://img.shields.io/badge/ClawHub-daMustermann%2Fclaw--qwen3--tts-purple.svg)](https://clawhub.dev/daMustermann/claw-qwen3-tts)

> High-quality text-to-speech for OpenClaw agents. 10 built-in speakers, voice cloning, voice design, emotional instruct control, 10+ languages, Telegram & WhatsApp voice messages. Auto-detects CUDA, ROCm, Intel XPU, or CPU.

---

## ⚡ Quick Start

```bash
# One-command install (clones repo, detects GPU, sets up everything)
bash <(curl -fsSL https://raw.githubusercontent.com/daMustermann/claw-qwen3-tts/main/install.sh)

# Or install from ClawHub
claw install daMustermann/claw-qwen3-tts

# Or clone manually
git clone https://github.com/daMustermann/claw-qwen3-tts.git ~/clawd/skills/qwen3-tts
bash ~/clawd/skills/qwen3-tts/install.sh
```

The installer auto-detects your GPU, creates an isolated Python virtual environment, and installs all dependencies. First run takes 5–15 minutes.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🎤 Generate Speech** | Human-quality TTS in 10+ languages (EN, ZH, JA, KO, DE, FR, RU, PT, ES, IT) |
| **🗣️ 10 Built-in Speakers** | Chelsie, Ethan, Aidan, Serena, Ryan, Vivian, Claire, Lucas, Eleanor, Benjamin |
| **🎭 Emotional Instruct** | Control tone and style — *"Speak happily"*, *"Whisper softly"*, *"用愤怒的语气"* |
| **🎨 Design Voices** | Create new voices from natural language descriptions |
| **🔄 Clone Voices** | Clone any voice from just 3 seconds of reference audio |
| **💾 Persist Voices by Name** | Save as "Angie", reuse forever with `voice: "Angie"` |
| **📱 Telegram & WhatsApp PTT** | Send audio as native push-to-talk voice messages |
| **🖥️ Auto-Detect Hardware** | NVIDIA CUDA, AMD ROCm, Intel XPU, or CPU-only |
| **🔌 OpenAI-Compatible API** | Drop-in replacement at `localhost:8880` |
| **🤖 Smart Model Routing** | Auto-corrects model selection to prevent errors |

---

## 🎯 Supported Hardware

| Hardware | Accelerator | Recommended Model | VRAM |
|----------|-------------|-------------------|------|
| NVIDIA GPU | CUDA | `custom-voice-1.7b` (high quality) | ~5 GB |
| AMD GPU | ROCm | `custom-voice-1.7b` or `custom-voice-0.6b` | ~2–5 GB |
| Intel GPU | XPU | `custom-voice-0.6b` (fast) | ~2 GB |
| CPU only | — | `custom-voice-0.6b` | ~4 GB RAM |

---

## 🔌 API Reference

The server runs at `http://localhost:8880` and exposes these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/audio/speech` | POST | Generate speech (built-in speakers or saved voices) |
| `/v1/audio/voice-design` | POST | Create speech with a natural-language voice description |
| `/v1/audio/voice-clone` | POST | Clone a voice from reference audio |
| `/v1/voices` | GET | List all saved voice profiles |
| `/v1/voices` | POST | Save a voice profile (name + embedding) |
| `/v1/voices/{name}` | GET | Get a specific voice profile |
| `/v1/voices/{name}` | PATCH | Rename or update a voice profile |
| `/v1/voices/{name}` | DELETE | Delete a voice profile |
| `/v1/audio/convert` | POST | Convert audio between formats (WAV/MP3/OGG/FLAC) |
| `/v1/audio/send/telegram` | POST | Send audio as Telegram PTT voice message |
| `/v1/audio/send/whatsapp` | POST | Send audio as WhatsApp PTT voice message |
| `/v1/models` | GET | List available TTS models |
| `/v1/speakers` | GET | List built-in speakers |
| `/health` | GET | Health check |

### Speech Generation

```bash
curl -X POST http://localhost:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "custom-voice-1.7b",
    "input": "Hello, this is a test of the Qwen3 text-to-speech system.",
    "voice": "default",
    "speaker": "Chelsie",
    "language": "en",
    "instruct": "Speak warmly and cheerfully",
    "response_format": "wav"
  }' \
  --output speech.wav
```

### Voice Design

```bash
curl -X POST http://localhost:8880/v1/audio/voice-design \
  -H "Content-Type: application/json" \
  -d '{
    "model": "voice-design",
    "input": "Welcome to our podcast!",
    "voice_description": "A warm, deep male voice with a slight British accent, calm and authoritative",
    "language": "en",
    "response_format": "wav"
  }' \
  --output designed_voice.wav
```

### Voice Cloning

```bash
curl -X POST http://localhost:8880/v1/audio/voice-clone \
  -F "reference_audio=@/path/to/reference.wav" \
  -F "reference_text=Transcript of the reference audio" \
  -F "input=New text to speak in the cloned voice" \
  -F "language=en" \
  -F "response_format=wav" \
  --output cloned.wav
```

- Minimum **3 seconds** of reference audio (10–30 seconds recommended)
- Accurate transcription of reference audio improves quality
- Supports **cross-language cloning** (clone from English → speak in Japanese)

---

## 🗣️ Voice Persistence

Every designed or cloned voice can be saved with a name you choose:

```
User: "Design a voice — a raspy pirate captain"
Agent: [generates audio] "Would you like to save this voice? What should I call it?"
User: "Call it Captain Hook"
Agent: "Voice saved as 'Captain Hook'! You can use it anytime."

User: "Say 'Ahoy mateys!' with voice Captain Hook"
Agent: [generates using saved voice]
```

Voices are stored locally in `voices/` and persist across sessions. The agent automatically prompts to save after every voice design or clone operation.

---

## 🎭 Built-in Speakers & Instruct

The `custom-voice` models come with **10 built-in speakers**, each with a unique voice:

> Chelsie · Ethan · Aidan · Serena · Ryan · Vivian · Claire · Lucas · Eleanor · Benjamin

You can also control the **emotional tone** with the `instruct` parameter:

```json
{ "instruct": "Speak happily and with excitement" }
{ "instruct": "Whisper softly, as if telling a secret" }
{ "instruct": "用愤怒的语气" }
```

---

## 🧠 Available Models

| Model ID | HuggingFace ID | Use Case | VRAM |
|----------|----------------|----------|------|
| `custom-voice-0.6b` | `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` | Fast TTS with built-in speakers | ~2 GB |
| `custom-voice-1.7b` | `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` | High-quality TTS with built-in speakers | ~5 GB |
| `base-0.6b` | `Qwen/Qwen3-TTS-12Hz-0.6B-Base` | Basic TTS (auto-corrected to custom-voice) | ~2 GB |
| `base-1.7b` | `Qwen/Qwen3-TTS-12Hz-1.7B-Base` | Basic TTS (auto-corrected to custom-voice) | ~5 GB |
| `voice-design` | `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` | Voice design from descriptions | ~5 GB |

> **Smart routing:** If you request a `base-*` model on the `/v1/audio/speech` endpoint, the server auto-corrects to the corresponding `custom-voice-*` model to prevent errors.

---

## 📱 Messaging Integration

### Telegram

Configure your bot token in `config.json`, then the agent sends audio as native PTT voice messages using `sendVoice` (OGG/Opus format).

```bash
curl -X POST http://localhost:8880/v1/audio/send/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "audio_file": "/path/to/speech.wav",
    "chat_id": "123456789",
    "bot_token": "YOUR_BOT_TOKEN"
  }'
```

### WhatsApp

Configure your WhatsApp Business API credentials in `config.json`, then audio is sent as native voice messages.

```bash
curl -X POST http://localhost:8880/v1/audio/send/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "audio_file": "/path/to/speech.wav",
    "phone_number_id": "PHONE_ID",
    "recipient": "+14155551234",
    "access_token": "YOUR_ACCESS_TOKEN"
  }'
```

---

## 🔧 Manual Setup

If you prefer manual setup instead of using `install.sh`:

```bash
cd ~/clawd/skills/qwen3-tts
bash scripts/setup_env.sh        # Detect GPU, create venv, install deps
bash scripts/start_server.sh     # Start the TTS server
bash scripts/health_check.sh     # Verify it's running
```

### Server Lifecycle

```bash
bash scripts/start_server.sh     # Start (idempotent — won't restart if already running)
bash scripts/stop_server.sh      # Gracefully stop
bash scripts/health_check.sh     # Returns OK or UNHEALTHY
```

---

## ⚙️ Configuration

Copy the template and customize:

```bash
cp config.json.template config.json
```

The config file controls server settings, default model, audio output, voice storage, and messaging credentials. See [`config.json.template`](config.json.template) for all options.

---

## 📁 Project Structure

```
claw-qwen3-tts/
├── SKILL.md                     # OpenClaw skill definition
├── README.md                    # This file
├── LICENSE                      # MIT License
├── install.sh                   # One-command installer
├── config.json.template         # Configuration template
├── .gitignore
├── scripts/
│   ├── detect_gpu.sh            # GPU hardware detection
│   ├── setup_env.sh             # Venv + dependency setup
│   ├── start_server.sh          # Start the TTS server
│   ├── stop_server.sh           # Stop the TTS server
│   ├── health_check.sh          # Server health check
│   └── convert_to_ogg_opus.sh   # Audio format conversion
├── server/
│   ├── tts_server.py            # FastAPI server (all endpoints)
│   ├── model_loader.py          # Model download & loading
│   ├── voice_manager.py         # Voice profile CRUD
│   ├── voice_designer.py        # Natural-language voice design
│   ├── voice_cloner.py          # Voice cloning pipeline
│   ├── audio_converter.py       # Audio format conversion
│   └── messaging/
│       ├── telegram_sender.py   # Telegram PTT delivery
│       └── whatsapp_sender.py   # WhatsApp PTT delivery
├── voices/                      # Saved voice profiles (per-install)
├── output/                      # Generated audio files (transient)
├── models/                      # Cached model weights (auto-downloaded)
└── requirements/
    ├── base.txt                 # Core Python dependencies
    ├── cuda.txt                 # NVIDIA CUDA extras
    ├── rocm.txt                 # AMD ROCm extras
    ├── intel.txt                # Intel XPU extras
    └── cpu.txt                  # CPU-only PyTorch
```

---

## 📋 Requirements

- **OS:** Linux (CachyOS, Arch, Ubuntu, Fedora, Debian, openSUSE, NixOS)
- **Python:** 3.10+
- **ffmpeg:** Required for audio format conversion
- **sox:** Required for audio processing
- **git:** Required for installation
- **Disk:** ~10 GB for models

---

## 🤝 Contributing

Contributions welcome! Please open an issue or PR on [GitHub](https://github.com/daMustermann/claw-qwen3-tts).

---

## 📜 Credits

- **Model:** [Qwen3-TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base) by the Qwen team (Alibaba Cloud)
- **Author:** [daMustermann](https://github.com/daMustermann)
- **License:** MIT
