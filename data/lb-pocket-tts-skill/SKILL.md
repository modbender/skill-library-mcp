---
id: pocket-tts
name: Pocket-TTS
version: 1.0.0
author: Leonardo Balland
description: Generate speech from text using Kyutai Pocket TTS - lightweight, CPU-friendly, streaming TTS with voice cloning. English only. ~6x real-time on M4 MacBook Air.
categories:
  - text-to-speech
  - documentation
tags:
  - kyutai
  - text-to-speech
  - tts
  - cpu
  - streaming
  - voice-cloning
homepage: https://kyutai.org/blog/2026-01-13-pocket-tts
repository: https://github.com/kyutai-labs/pocket-tts
documentation: https://github.com/kyutai-labs/pocket-tts/tree/main/docs
---

# Pocket TTS

Lightweight CPU-friendly text-to-speech with voice cloning. No GPU required.

## When to Use

- Generating speech from text on CPU without GPU
- Voice cloning from audio samples
- Streaming audio generation (low latency)
- Local TTS without API dependencies
- Real-time speech synthesis (~6x faster than real-time)

---

## Key Features

- **100M parameters** - Small, efficient model
- **CPU-optimized** - No GPU needed, uses only 2 cores
- **~6x real-time** - Fast generation on modern CPUs
- **~200ms latency** - To first audio chunk (streaming)
- **Voice cloning** - From 3-10s audio samples
- **24kHz mono WAV** - High-quality output
- **English only** - More languages planned

---

## Installation

```bash
pip install pocket-tts
# or
uv add pocket-tts
```

---

## CLI Commands

### Generate Speech

```bash
# Basic generation (default voice)
pocket-tts generate --text "Hello world"

# Custom voice (local file, URL, or safetensors)
pocket-tts generate --voice ./my_voice.wav
pocket-tts generate --voice "hf://kyutai/tts-voices/alba-mackenna/casual.wav"
pocket-tts generate --voice ./voice.safetensors

# Quality tuning
pocket-tts generate --temperature 0.7 --lsd-decode-steps 3
```

**See** `docs/generate.md` for full CLI reference.

### Start Web Server

```bash
# Start FastAPI server with web UI
pocket-tts serve

# Custom host/port
pocket-tts serve --host localhost --port 8080
```

**See** `docs/serve.md` for server options.

### Export Voice Embeddings

Convert audio files to `.safetensors` for faster loading:

```bash
# Single file
pocket-tts export-voice voice.mp3 voice.safetensors

# Batch conversion
pocket-tts export-voice voices/ embeddings/ --truncate
```

**See** `docs/export_voice.md` for export options.

---

## Python API

### Basic Usage

```python
from pocket_tts import TTSModel
import scipy.io.wavfile

# Load model
model = TTSModel.load_model()

# Get voice state
voice = model.get_state_for_audio_prompt(
    "hf://kyutai/tts-voices/alba-mackenna/casual.wav"
)

# Generate audio
audio = model.generate_audio(voice, "Hello world!")

# Save
scipy.io.wavfile.write("output.wav", model.sample_rate, audio.numpy())
```

### Load Model

```python
model = TTSModel.load_model(
    config="b6369a24",       # Model variant
    temp=0.7,                # Temperature (0.5-1.0)
    lsd_decode_steps=1,      # Generation steps (1-5)
    eos_threshold=-4.0       # End-of-sequence threshold
)
```

### Voice State

```python
# From audio file/URL
voice = model.get_state_for_audio_prompt("./voice.wav")
voice = model.get_state_for_audio_prompt("hf://kyutai/tts-voices/alba-mackenna/casual.wav")

# From safetensors (fast loading)
voice = model.get_state_for_audio_prompt("./voice.safetensors")
```

### Streaming Generation

```python
# Stream audio chunks
for chunk in model.generate_audio_stream(voice, "Long text..."):
    # Process/save/play each chunk as generated
    print(f"Chunk: {chunk.shape[0]} samples")
```

### Multi-Voice Management

```python
# Preload multiple voices
voices = {
    "casual": model.get_state_for_audio_prompt("hf://kyutai/tts-voices/alba-mackenna/casual.wav"),
    "announcer": model.get_state_for_audio_prompt("./announcer.safetensors"),
}

# Use different voices
audio1 = model.generate_audio(voices["casual"], "Hey there!")
audio2 = model.generate_audio(voices["announcer"], "Breaking news!")
```

**See** `docs/python-api.md` for complete API reference.

---

## Available Voices

Pre-made voices from `hf://kyutai/tts-voices/`:

- `alba-mackenna/casual.wav` (default, female)
- `jessica-jian/casual.wav` (female)
- `voice-donations/Selfie.wav` (male, marius)
- `voice-donations/Butter.wav` (male, javert)
- `ears/p010/freeform_speech_01.wav` (male, jean)
- `vctk/p244_023.wav` (female, fantine)
- `vctk/p262_023.wav` (female, eponine)
- `vctk/p303_023.wav` (female, azelma)

Or clone any voice from your own audio samples.

---

## Voice Cloning Tips

- **Clean audio** - Remove background noise (use [Adobe Podcast Enhance](https://podcast.adobe.com/en/enhance))
- **Length** - 3-10 seconds of speech is ideal
- **Quality** - Input quality affects output quality
- **Format** - WAV, MP3, or any common audio format supported

---

## Performance Tips

- **CPU-only** - GPU provides no speedup (model too small, batch size 1)
- **2 cores** - Uses only 2 CPU cores efficiently
- **Streaming** - Low latency (<200ms to first chunk)
- **Safetensors** - Pre-process voices to `.safetensors` for instant loading

---

## Output Format

All commands output WAV files:
- **Sample rate**: 24 kHz
- **Channels**: Mono
- **Bit depth**: 16-bit PCM

---

## Links

- [GitHub](https://github.com/kyutai-labs/pocket-tts)
- [Tech Report](https://kyutai.org/blog/2026-01-13-pocket-tts)
- [Paper (arXiv)](https://arxiv.org/abs/2509.06926)
- [HuggingFace Model](https://huggingface.co/kyutai/pocket-tts)
- [Voice Repository](https://huggingface.co/kyutai/tts-voices)
- [Live Demo](https://kyutai.org/pocket-tts)
