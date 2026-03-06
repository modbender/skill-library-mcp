---
name: local-whisper-cpp
description: Local speech-to-text using whisper-cli (whisper.cpp).
metadata:
  {
    "openclaw":
      {
        "emoji": "🌬️",
        "requires": { "bins": ["whisper-cli"] },
      },
  }
---

# Local Whisper (cpp)

Transcribe audio files locally using `whisper-cli` and the `large-v3-turbo` model.

## Usage

You can use the wrapper script:
- `scripts/whisper-local.sh <audio-file>`

Or call the binary directly:
- `whisper-cli -m /usr/share/whisper.cpp-model-large-v3-turbo/ggml-large-v3-turbo.bin -f <file> -l auto -nt`

## Scripts

- **Location:** `scripts/whisper-local.sh` (inside skill folder)
- **Model:** `/usr/share/whisper.cpp-model-large-v3-turbo/ggml-large-v3-turbo.bin`
- **GPU:** Enabled via `whisper-cli`.

## Setup

Download the model to `/usr/share/whisper.cpp-model-large-v3-turbo/`:
```bash
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin?download=true -O /usr/share/whisper.cpp-model-large-v3-turbo/ggml-large-v3-turbo.bin
```
