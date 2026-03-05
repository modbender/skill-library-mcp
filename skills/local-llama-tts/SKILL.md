---
name: local-llama-tts
description: Local text-to-speech using llama-tts (llama.cpp) and OuteTTS-1.0-0.6B model.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔊",
        "requires": { "bins": ["llama-tts"] },
      },
  }
---

# Local Llama TTS

Synthesize speech locally using `llama-tts` and the `OuteTTS-1.0-0.6B` model.

## Usage

You can use the wrapper script:
- `scripts/tts-local.sh [options] "<text>"`

### Options
- `-o, --output <file>`: Output WAV file (default: `output.wav`)
- `-s, --speaker <file>`: Speaker reference file (optional)
- `-t, --temp <value>`: Temperature (default: `0.4`)

## Scripts

- **Location:** `scripts/tts-local.sh` (inside skill folder)
- **Model:** `/data/public/machine-learning/models/text-to-speach/OuteTTS-1.0-0.6B-Q4_K_M.gguf`
- **Vocoder:** `/data/public/machine-learning/models/text-to-speach/WavTokenizer-Large-75-Q4_0.gguf`
- **GPU:** Enabled via `llama-tts`.

## Setup

1. **Model:** Download from [OuteAI/OuteTTS-1.0-0.6B-GGUF](https://huggingface.co/OuteAI/OuteTTS-1.0-0.6B-GGUF/resolve/main/OuteTTS-1.0-0.6B-Q4_K_M.gguf?download=true)
2. **Vocoder:** Download from [ggml-org/WavTokenizer](https://huggingface.co/ggml-org/WavTokenizer/resolve/main/WavTokenizer-Large-75-Q5_1.gguf?download=true) (Note: Felix uses a Q4_0 version, Q5_1 is linked here as a high-quality alternative).

Place files in `/data/public/machine-learning/models/text-to-speach/` or update `scripts/tts-local.sh`.

## Sampling Configuration
The model card recommends the following settings (hardcoded in the script):
- **Temperature:** 0.4
- **Repetition Penalty:** 1.1
- **Repetition Range:** 64
- **Top-k:** 40
- **Top-p:** 0.9
- **Min-p:** 0.05
