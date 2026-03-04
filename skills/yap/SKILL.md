---
name: yap
description: Fast on-device speech-to-text using Apple Speech.framework (macOS 26+).
homepage: https://github.com/finnvoor/yap
metadata: {"openclaw":{"emoji":"🗣️","os":["darwin"],"requires":{"bins":["yap"]},"install":[{"id":"brew","kind":"brew","formula":"finnvoor/tools/yap","bins":["yap"],"label":"Install yap (brew)"}]}}
---

# yap

Use `yap` for fast on-device transcription on macOS using Apple's Speech.framework.

## Quick start

```bash
yap transcribe /path/to/audio.mp3
yap transcribe /path/to/audio.m4a --locale de-DE
yap transcribe /path/to/video.mp4 --srt -o captions.srt
```

## Options

- `--locale <locale>` — Language locale (e.g., `de-DE`, `en-US`, `zh-CN`)
- `--censor` — Redact certain words/phrases
- `--txt` / `--srt` — Output format (default: txt)
- `-o, --output-file` — Save to file instead of stdout

## Advantages over Whisper

- Native Apple Speech.framework (optimized for Apple Silicon)
- No model download required
- Faster processing
- Lower memory usage

## Notes

- Requires macOS 26 (Tahoe) or later
- Supported languages depend on installed Apple Speech models
