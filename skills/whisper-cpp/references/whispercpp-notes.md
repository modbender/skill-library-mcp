# whisper.cpp notes for OpenClaw

## Why a wrapper

OpenClaw’s `tools.media.audio.models` CLI integration expects **plain transcript on stdout**.
The raw `whisper-cli` binary can print extra progress/timestamps depending on flags and version.
The wrapper `openclaw-whisper-stt` standardizes:

- model selection (`OPENCLAW_WHISPER_MODEL=base|small`)
- output formatting (writes .txt then `cat`)

## Performance guidance

- `base` is a good default for CPU-only boxes.
- `small` is more accurate but slower.

## Debug checklist

1) Confirm OpenClaw can find the wrapper:

```bash
which openclaw-whisper-stt
openclaw config get tools.media.audio.models
```

2) Run wrapper manually:

```bash
openclaw-whisper-stt /path/to/audio.wav
OPENCLAW_WHISPER_MODEL=small openclaw-whisper-stt /path/to/audio.wav
```

3) Follow logs while testing a Telegram voice note:

```bash
openclaw logs --follow
```
