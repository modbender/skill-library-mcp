---
name: venice-transcribe
description: Transcribe audio to text using Venice AI's Whisper-based speech recognition. Supports WAV, MP3, FLAC, M4A, AAC formats with optional timestamps.
homepage: https://venice.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "🎤",
        "requires": { "bins": ["uv"], "env": ["VENICE_API_KEY"] },
        "primaryEnv": "VENICE_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Venice Transcribe

Transcribe audio files to text using Venice AI's speech recognition (Whisper-based).

**API Base URL:** `https://api.venice.ai/api/v1`
**Documentation:** [docs.venice.ai](https://docs.venice.ai)

## Setup

1. Get your API key from [venice.ai](https://venice.ai) → Settings → API Keys
2. Set the environment variable:

```bash
export VENICE_API_KEY="your_api_key_here"
```

---

## Transcribe Audio

Convert audio files to text.

```bash
uv run {baseDir}/scripts/transcribe.py --file recording.mp3
```

**Options:**

- `--file` (required): Audio file path
- `--output`: Save transcription to file (default: prints to stdout)
- `--model`: ASR model (default: `openai/whisper-large-v3`)
- `--format`: Output format: `json` or `text` (default: `json`)
- `--timestamps`: Include word/segment timestamps
- `--language`: Language hint (ISO 639-1 code, e.g., `en`, `es`, `fr`)

**Supported audio formats:**
- WAV, WAVE
- MP3
- FLAC  
- M4A, AAC
- MP4 (audio track)

---

## Examples

**Basic transcription:**
```bash
uv run {baseDir}/scripts/transcribe.py --file meeting.mp3
```

**Get just the text (no JSON):**
```bash
uv run {baseDir}/scripts/transcribe.py --file audio.wav --format text
```

**With timestamps:**
```bash
uv run {baseDir}/scripts/transcribe.py --file podcast.mp3 --timestamps
```

**Spanish audio with language hint:**
```bash
uv run {baseDir}/scripts/transcribe.py --file spanish.mp3 --language es
```

**Save to file:**
```bash
uv run {baseDir}/scripts/transcribe.py --file interview.mp3 --output transcript.json
```

---

## Output Format

**JSON format (default):**
```json
{
  "text": "Hello, this is a transcription test.",
  "duration": 3.5
}
```

**JSON with timestamps:**
```json
{
  "text": "Hello world",
  "duration": 2.1,
  "timestamps": {
    "word": [
      {"word": "Hello", "start": 0.0, "end": 0.5},
      {"word": "world", "start": 0.6, "end": 1.0}
    ],
    "segment": [
      {"text": "Hello world", "start": 0.0, "end": 1.0}
    ]
  }
}
```

**Text format:**
```
Hello, this is a transcription test.
```

---

## Runtime Note

This skill uses `uv run` which automatically installs Python dependencies (httpx) via [PEP 723](https://peps.python.org/pep-0723/) inline script metadata. No manual Python package installation required - `uv` handles everything.

---

## API Reference

| Endpoint | Description | Method |
|----------|-------------|--------|
| `/audio/transcriptions` | Transcribe audio to text | POST (multipart) |

Full API docs: [docs.venice.ai](https://docs.venice.ai)

