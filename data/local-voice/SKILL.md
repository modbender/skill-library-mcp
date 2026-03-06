---
name: local-voice
description: Local text-to-speech (TTS) and speech-to-text (STT) using FluidAudio on Apple Silicon. Sub-second voice synthesis and transcription running entirely on-device via the Apple Neural Engine. Use when setting up local voice capabilities, voice assistant integration, or replacing cloud TTS/STT services.
---

# Local Voice (FluidAudio TTS/STT)

Sub-second local voice AI for Apple Silicon Macs using FluidAudio's CoreML models.

## Features

- **TTS**: Kokoro model with 54 voices, ~0.6-0.8s latency
- **STT**: Parakeet TDT v3, ~0.2-0.3s latency, 25 languages
- **100% local**: No cloud, no cost, works offline
- **Neural Engine**: Runs on Apple's ANE for efficiency

## Requirements

- macOS 14+ on Apple Silicon (M1/M2/M3/M4)
- Swift 5.9+
- espeak-ng (for TTS phoneme fallback)

## Quick Setup

### 1. Install Dependencies

```bash
brew install espeak-ng
```

### 2. Build the Daemon

```bash
cd /path/to/skill/sources
swift build -c release
```

### 3. Install Binary and Framework

```bash
mkdir -p ~/clawd/bin
cp .build/release/StellaVoice ~/clawd/bin/
cp -R .build/arm64-apple-macosx/release/ESpeakNG.framework ~/clawd/bin/
install_name_tool -add_rpath @executable_path ~/clawd/bin/StellaVoice
```

### 4. Create LaunchAgent

```bash
cat > ~/Library/LaunchAgents/com.stella.tts.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stella.tts</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HOME/clawd/bin/StellaVoice</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.clawdbot/logs/stella-tts.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.clawdbot/logs/stella-tts.err.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.stella.tts.plist
```

## API Endpoints

The daemon listens on `http://127.0.0.1:18790`:

### TTS - Text to Speech

```bash
# Simple text to WAV
curl -X POST http://127.0.0.1:18790/synthesize -d "Hello world" -o output.wav

# With speed control (0.5-2.0)
curl -X POST "http://127.0.0.1:18790/synthesize?speed=1.2" -d "Fast!" -o output.wav

# JSON endpoint
curl -X POST http://127.0.0.1:18790/synthesize/json \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "speed": 1.0, "deEss": true}'
```

### STT - Speech to Text

```bash
curl -X POST http://127.0.0.1:18790/transcribe \
  --data-binary @audio.wav \
  -H "Content-Type: audio/wav"
# Returns: {"text": "transcribed text"}
```

### Health Check

```bash
curl http://127.0.0.1:18790/health
# Returns: ok
```

## Voice Options

Default voice is `af_sky`. Change by modifying the source code.

**Top Kokoro voices (American female):**
- `af_heart` (A grade) - warm, natural
- `af_bella` (A-) - expressive
- `af_sky` (C-) - clear, light

**All 54 voices**: See references/VOICES.md

## Expressiveness

### Speed Control
- `speed=0.8` → Calm, relaxed
- `speed=1.0` → Natural pace
- `speed=1.2` → Energetic, upbeat

### Punctuation (automatic)
- `!` → Excited tone
- `?` → Rising intonation
- `.` → Neutral, falling
- `...` → Pauses

### SSML Tags
```
<phoneme ph="kəkˈɔɹO">Kokoro</phoneme>
<sub alias="Doctor">Dr.</sub>
<say-as interpret-as="date">2024-01-15</say-as>
```

## Helper Script

See `scripts/stella-tts.sh` for a convenient wrapper:

```bash
scripts/stella-tts.sh "Hello world" output.wav
scripts/stella-tts.sh "Hello world" output.mp3  # Auto-converts
```

## Integration Example

For voice assistants, update your voice proxy to use local endpoints:

```javascript
// STT
const response = await fetch('http://127.0.0.1:18790/transcribe', {
    method: 'POST',
    headers: { 'Content-Type': 'audio/wav' },
    body: audioData
});
const { text } = await response.json();

// TTS
const audio = await fetch('http://127.0.0.1:18790/synthesize', {
    method: 'POST',
    body: textToSpeak
});
```

## Troubleshooting

**Library not loaded (ESpeakNG)**
- Ensure ESpeakNG.framework is in the same directory as the binary
- Run `install_name_tool -add_rpath @executable_path /path/to/binary`

**Slow first request**
- First request loads models (~8-10s)
- Subsequent requests are sub-second

**x86 vs ARM**
- Must build and run on ARM64 native (not Rosetta)
- Check with `uname -m` (should show `arm64`)

## Source Code

The daemon source is in `sources/` directory. It's a Swift package using:
- FluidAudio (TTS + STT models)
- Hummingbird (HTTP server)

Rebuild after modifying:
```bash
cd sources && swift build -c release
```
