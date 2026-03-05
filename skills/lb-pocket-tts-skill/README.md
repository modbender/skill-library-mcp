# Pocket TTS Documentation Skill

Complete Kyutai Pocket TTS documentation packaged as an OpenClaw AgentSkill.

Pocket TTS is a lightweight text-to-speech (TTS) model that runs efficiently on CPUs without requiring GPUs. Features voice cloning, streaming audio generation, and ~6x real-time performance on modern CPUs.

## Contents

- **CLI Commands** (`generate`, `serve`, `export-voice`)
- **Python API** (TTSModel, voice states, streaming)
- **Voice Cloning** (from audio files or safetensors)
- **Performance Tips** (CPU optimization, latency reduction)
- **Complete Reference Docs** (from official GitHub repo)

## Structure

```
docs/
├── generate.md       # CLI generate command reference
├── serve.md          # CLI serve command (FastAPI server)
├── export_voice.md   # Voice export (audio → safetensors)
├── python-api.md     # Complete Python API reference
├── *.png             # Architecture diagrams
└── *.ipynb           # Example notebooks
```

## Key Features

- **100M parameters** - Small model size
- **CPU-only** - No GPU required
- **~6x real-time** - On M4 MacBook Air
- **~200ms latency** - To first audio chunk
- **Streaming** - Generate audio on-the-fly
- **Voice cloning** - Clone any voice from 3-10s audio
- **English only** (more languages planned)

## Installation

Via ClawHub:
```bash
clawhub install lb-pocket-tts
```

Or manually: Download and extract into your OpenClaw workspace `skills/` folder.

## Usage

This skill triggers automatically when you ask questions about:
- Text-to-speech generation
- Voice cloning
- CPU-friendly TTS
- Kyutai Pocket TTS CLI or Python API
- Streaming audio generation

## Quick Start

### CLI
```bash
pip install pocket-tts

# Generate speech
pocket-tts generate --text "Hello world"

# Start web server
pocket-tts serve
```

### Python
```python
from pocket_tts import TTSModel

model = TTSModel.load_model()
voice = model.get_state_for_audio_prompt("hf://kyutai/tts-voices/alba-mackenna/casual.wav")
audio = model.generate_audio(voice, "Hello world!")
```

## Source

Documentation extracted from [kyutai-labs/pocket-tts](https://github.com/kyutai-labs/pocket-tts) official repository.

## Links

- [GitHub](https://github.com/kyutai-labs/pocket-tts)
- [Tech Report](https://kyutai.org/blog/2026-01-13-pocket-tts)
- [HuggingFace Model](https://huggingface.co/kyutai/pocket-tts)
- [Voice Repository](https://huggingface.co/kyutai/tts-voices)
- [Live Demo](https://kyutai.org/pocket-tts)

## License

Documentation content: Apache 2.0 (from Pocket TTS project)
