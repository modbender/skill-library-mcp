---
name: step-asr
description: Transcribe audio files to text via Step ASR streaming API (HTTP SSE). Supports Chinese and English, multiple audio formats (PCM, WAV, MP3, OGG/OPUS), real-time streaming output, and terminology correction prompts.
version: 1.0.0
metadata:
  openclaw:
    emoji: "\U0001F399"
    requires:
      bins:
        - python3
      env:
        - STEPFUN_API_KEY
    primaryEnv: STEPFUN_API_KEY
    homepage: https://platform.stepfun.com/docs/zh/api-reference/audio/asr-stream
---

# Step ASR - Streaming Speech-to-Text

Transcribe audio files using the Step (StepFun) ASR API with HTTP SSE streaming.

## Quick start

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.wav
```

## Usage examples

Basic transcription (Chinese, streaming output):

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.wav
```

Specify language and save to file:

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.mp3 --language en --out /tmp/transcript.txt
```

Use a prompt for terminology correction:

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.pcm --prompt "Related terms: OpenClaw, StepFun, ASR"
```

Output as JSON (includes usage stats):

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.ogg --json
```

Non-streaming mode (only print final result):

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.wav --no-stream
```

Specify audio format explicitly (for raw PCM files without extension):

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/raw_audio --format-type pcm --sample-rate 16000
```

## Supported audio formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| PCM    | `.pcm`, `.raw` | Raw PCM, default codec `pcm_s16le` |
| WAV    | `.wav`    | WAV container format |
| MP3    | `.mp3`    | |
| OGG/OPUS | `.ogg`, `.opus` | |

## All options

| Flag | Default | Description |
|------|---------|-------------|
| `--language` | `zh` | Language code (`zh` or `en`) |
| `--model` | `step-asr` | ASR model name |
| `--out` | *(stdout)* | Save transcription to file |
| `--prompt` | *(none)* | Hint text to improve accuracy for domain-specific terms |
| `--format-type` | *(auto)* | Audio format: `pcm`, `mp3`, `ogg` (auto-detected from extension) |
| `--sample-rate` | `16000` | Audio sample rate in Hz |
| `--no-stream` | `false` | Only print the final complete result |
| `--json` | `false` | Output as JSON with usage statistics |
| `--no-itn` | `false` | Disable inverse text normalization |
| `--no-rerun` | `false` | Disable second-pass error correction |

## API key

Set `STEPFUN_API_KEY` environment variable, or configure it in `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    "step-asr": {
      apiKey: "YOUR_STEPFUN_API_KEY"
    }
  }
}
```

Get your API key from [Step Platform](https://platform.stepfun.com/).
