# macos-local-voice

An [OpenClaw](https://openclaw.ai) skill for fully local speech-to-text and text-to-speech on macOS.

- **STT**: [yap](https://github.com/finnvoor/yap) — Apple on-device speech recognition (Speech.framework)
- **TTS**: `say` — macOS built-in text-to-speech
- **Voice detection**: `osascript` + AVFoundation — checks which voices are downloaded and their quality

**No API keys. No network. No cloud. Everything runs on your Mac.**

## Install

### Prerequisites

```bash
brew install finnvoor/tools/yap   # STT
brew install ffmpeg                # audio format conversion (optional but recommended)
```

### As an OpenClaw skill

```bash
# Option 1: via ClawHub (when published)
clawhub install macos-local-voice

# Option 2: manual
git clone https://github.com/strrl/openclaw-skill-macos-local-voice.git \
  ~/.openclaw/workspace/skills/macos-local-voice
```

## Usage

See [SKILL.md](./SKILL.md) for full agent instructions.

### Quick CLI test

```bash
# Transcribe audio
bash scripts/stt.sh recording.ogg zh_CN

# Text to speech (auto-selects best voice)
bash scripts/tts.sh "你好世界"

# List available Chinese voices
bash scripts/voices.sh list zh-CN

# Check if a specific voice is ready
bash scripts/voices.sh check "Yue (Premium)"

# Get best voice for a language
bash scripts/voices.sh best zh-CN
```

## Voice Quality

macOS voices come in three quality tiers:

| Quality | Level | Notes |
|---------|-------|-------|
| compact | 1 | Always available, low quality |
| enhanced | 2 | May need download |
| premium | 3 | Best quality, needs manual download |

To download premium voices: **System Settings → Accessibility → Spoken Content → System Voice → Manage Voices**

## License

MIT
