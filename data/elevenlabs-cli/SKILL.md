---
name: elevenlabs-cli
description: CLI for ElevenLabs AI audio platform - text-to-speech, speech-to-text, voice cloning, and more
homepage: https://github.com/hongkongkiwi/elevenlabs-cli
metadata:
  clawdbot:
    emoji: "🎙️"
    requires:
      env: ["ELEVENLABS_API_KEY"]
    primaryEnv: "ELEVENLABS_API_KEY"
---

# ElevenLabs CLI

> **Unofficial CLI**: This is an independent, community-built CLI client. It is not officially released by ElevenLabs.

A comprehensive command-line interface for the ElevenLabs AI audio platform with 100% SDK coverage. Generate speech, transcribe audio, clone voices, and more.

## External Endpoints

This skill instructs the CLI to call the following external services:

| Endpoint | Purpose | Data Sent |
|----------|---------|-----------|
| `https://api.elevenlabs.io/*` | ElevenLabs API | API key (auth), text/audio content, voice settings |
| `https://github.com/hongkongkiwi/elevenlabs-cli/*` | Package downloads | None (public) |

## Security & Privacy

- **API Key**: Your ElevenLabs API key is sent only to `api.elevenlabs.io` for authentication
- **Audio/Text Content**: Text and audio files you process are sent to ElevenLabs API
- **No Local Persistence**: The CLI does not store your data locally beyond specified output files
- **No Telemetry**: No usage data is sent to any third party

## Trust Statement

By using this skill, you will send your ElevenLabs API key and audio/text content to ElevenLabs servers. Only install this skill if you trust ElevenLabs with your data. This is an unofficial community-maintained CLI.

---

## Installation

### Homebrew (macOS/Linux)

```bash
brew tap hongkongkiwi/tap
brew install elevenlabs-cli
```

### Scoop (Windows)

```powershell
scoop bucket add elevenlabs-cli https://github.com/hongkongkiwi/scoop-elevenlabs-cli
scoop install elevenlabs-cli
```

### Snap (Linux)

```bash
sudo snap install elevenlabs-cli
```

### Cargo (All Platforms)

```bash
cargo install elevenlabs-cli
```

### Docker

```bash
docker pull ghcr.io/hongkongkiwi/elevenlabs-cli:latest
docker run --rm -e ELEVENLABS_API_KEY=your-key ghcr.io/hongkongkiwi/elevenlabs-cli tts "Hello!"
```

## Prerequisites

- **ElevenLabs API key** - Get one free at [ElevenLabs API Keys](https://elevenlabs.io/app/settings/api-keys)

## Configuration

```bash
# Set API key via environment variable
export ELEVENLABS_API_KEY="your-api-key"

# Or save to config file (~/.config/elevenlabs-cli/config.toml)
elevenlabs config set api_key your-api-key

# Set default voice and model
elevenlabs config set default_voice Brian
elevenlabs config set default_model eleven_multilingual_v2
```

## Commands Reference

### Text-to-Speech (`tts`)

Convert text to natural speech with 100+ voices.

```bash
# Basic usage - speaks text and saves to file
elevenlabs tts "Hello, world!"

# Specify voice and model
elevenlabs tts "Hello!" --voice Rachel --model eleven_v3

# Save to specific file
elevenlabs tts "Hello!" --output speech.mp3

# Read text from file
elevenlabs tts --file script.txt --output audiobook.mp3

# Adjust voice settings
elevenlabs tts "Hello!" --stability 0.5 --similarity-boost 0.75 --style 0.3

# Play audio after generation (requires audio feature)
elevenlabs tts "Hello!" --play

# Specify language for multilingual models
elevenlabs tts "Bonjour!" --language fr

# Use seed for reproducible output
elevenlabs tts "Hello!" --seed 12345
```

### Speech-to-Text (`stt`)

Transcribe audio with speaker diarization and timestamps.

```bash
# Transcribe audio file
elevenlabs stt audio.mp3

# Enable speaker diarization (identify speakers)
elevenlabs stt meeting.mp3 --diarize --num-speakers 3

# Output as subtitles
elevenlabs stt video.mp3 --format srt --output subtitles.srt

# With word-level timestamps
elevenlabs stt audio.mp3 --timestamps word

# Record from microphone and transcribe
elevenlabs stt --record --duration 10
```

### Voice Management (`voice`)

Manage voices including cloning and settings.

```bash
# List all voices
elevenlabs voice list

# Get voice details
elevenlabs voice get <voice-id>

# Clone a voice from audio samples
elevenlabs voice clone --name "My Voice" --samples sample1.mp3,sample2.mp3

# Clone from directory of samples
elevenlabs voice clone --name "My Voice" --samples-dir ./samples/

# Get voice settings
elevenlabs voice settings <voice-id>

# Edit voice settings
elevenlabs voice edit-settings <voice-id> --stability 0.6 --similarity-boost 0.8

# Delete a voice
elevenlabs voice delete <voice-id>

# Share a voice publicly
elevenlabs voice share <voice-id>

# Find similar voices
elevenlabs voice similar --voice-id <voice-id>
elevenlabs voice similar --text "deep male voice with british accent"
```

### Sound Effects (`sfx`)

Generate sound effects from text descriptions.

```bash
# Generate sound effect
elevenlabs sfx "door creaking slowly in a haunted house"

# Specify duration (0.5-22 seconds)
elevenlabs sfx "thunder rumbling" --duration 10 --output thunder.mp3
```

### Audio Isolation (`isolate`)

Remove background noise from audio.

```bash
# Remove background noise
elevenlabs isolate noisy_audio.mp3 --output clean_audio.mp3
```

### Voice Changer (`voice-changer`)

Transform voice in audio files to a different voice.

```bash
# Transform voice in audio file
elevenlabs voice-changer input.mp3 --voice Rachel --output transformed.mp3

# Record from microphone and transform
elevenlabs voice-changer --record --duration 10 --voice Rachel --output output.mp3
```

### Dubbing (`dub`)

Translate and dub video/audio to other languages.

```bash
# Create dubbing project
elevenlabs dub create --file video.mp4 --source-lang en --target-lang es

# Check dubbing status
elevenlabs dub status <dubbing-id>

# Download dubbed file
elevenlabs dub download <dubbing-id> --output dubbed.mp4
```

### Dialogue (`dialogue`)

Generate multi-voice dialogues.

```bash
# Create dialogue with multiple voices
elevenlabs dialogue --inputs "Hello there!:Brian,Hi! How are you?:Rachel,I'm great thanks!:Brian"

# Save to file
elevenlabs dialogue --inputs "..." --output dialogue.mp3
```

### Agents (`agent`)

Manage conversational AI agents.

```bash
# List agents
elevenlabs agent list

# Create agent
elevenlabs agent create --name "Support Bot" --voice-id <voice-id> --first-message "Hello!"

# Get agent details
elevenlabs agent get <agent-id>

# Delete agent
elevenlabs agent delete <agent-id>
```

### Knowledge Base (`knowledge`)

Manage documents for RAG.

```bash
# List documents
elevenlabs knowledge list

# Add document from URL
elevenlabs knowledge add-from-url --url https://example.com/doc --name "Documentation"

# Add document from file
elevenlabs knowledge add-from-file --file document.pdf --name "PDF Doc"
```

### History (`history`)

View and manage generation history.

```bash
# List generation history
elevenlabs history list

# Download audio from history
elevenlabs history download <history-item-id> --output audio.mp3
```

### Usage & User

```bash
# Get user info
elevenlabs user info

# Get usage statistics
elevenlabs usage stats
```

### Configuration (`config`)

```bash
# Set config value
elevenlabs config set api_key your-key

# Get config value
elevenlabs config get api_key

# List all config
elevenlabs config list
```

### Utilities

```bash
# Generate shell completions
elevenlabs completions bash > ~/.bash_completion.d/elevenlabs
elevenlabs completions zsh > "${fpath[1]}/_elevenlabs"
elevenlabs completions fish > ~/.config/fish/completions/elevenlabs.fish

# Update CLI to latest version
elevenlabs update

# Interactive mode (REPL)
elevenlabs interactive
```

## Output Formats

| Format | Description |
|--------|-------------|
| `mp3_44100_128` | MP3 44.1kHz 128kbps (default) |
| `mp3_44100_192` | MP3 44.1kHz 192kbps |
| `wav_44100` | WAV 44.1kHz |
| `pcm_16000` | PCM 16kHz |
| `opus_48000_128` | Opus 48kHz 128kbps |

## Models

### TTS Models

| Model | Description |
|-------|-------------|
| `eleven_multilingual_v2` | Best quality, 29 languages (default) |
| `eleven_flash_v2_5` | Lowest latency |
| `eleven_v3` | Expressive, emotional speech |

### STT Models

| Model | Description |
|-------|-------------|
| `scribe_v1` | High accuracy transcription (default) |
| `scribe_v1_base` | Faster, lower cost |

## Related Resources

- **Main Repository**: [hongkongkiwi/elevenlabs-cli](https://github.com/hongkongkiwi/elevenlabs-cli)
- **Homebrew Tap**: [hongkongkiwi/homebrew-elevenlabs-cli](https://github.com/hongkongkiwi/homebrew-elevenlabs-cli)
- **Scoop Bucket**: [hongkongkiwi/scoop-elevenlabs-cli](https://github.com/hongkongkiwi/scoop-elevenlabs-cli)
- **ElevenLabs API Docs**: https://elevenlabs.io/docs/api-reference
- **API Keys**: https://elevenlabs.io/app/settings/api-keys

## Tags

elevenlabs, tts, text-to-speech, stt, speech-to-text, audio, voice, voice-cloning, voice-synthesis, ai, cli
