# 🎤 Local Whisper

[![ClawdHub](https://img.shields.io/badge/ClawdHub-whisper--mlx--local-orange)](https://clawdhub.com/skills/whisper-mlx-local)
[![GitHub](https://img.shields.io/badge/GitHub-ImpKind%2Flocal--whisper-blue?logo=github)](https://github.com/ImpKind/local-whisper)

**Transcribe voice messages for free.** Runs locally on your Mac.

## Why?

Voice transcription APIs charge per minute. This skill does the same thing **for free** — runs Whisper directly on your Mac's Apple Silicon.

- ✅ **Free** — no API costs, ever
- ✅ **Private** — audio stays on your machine
- ✅ **Fast** — ~1 second per voice message
- ✅ **Offline** — works without internet

## Install

```bash
git clone https://github.com/ImpKind/local-whisper
cd local-whisper
pip3 install -r requirements.txt
```

## Use

```bash
# Start daemon (keeps model loaded)
python3 scripts/daemon.py

# Transcribe
./scripts/transcribe.sh voice_message.ogg
```

## Auto-Start

```bash
cp com.local-whisper.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.local-whisper.plist
```

## Requirements

- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.9+

## License

MIT
