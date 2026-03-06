---
name: mlx-local-inference
description: >
  Full local AI inference stack on Apple Silicon Macs via MLX.
  Includes: LLM chat (Qwen3-14B, Gemma3-12B), speech-to-text ASR (Qwen3-ASR, Whisper),
  text embeddings (Qwen3-Embedding 0.6B/4B), OCR (PaddleOCR-VL), TTS (Qwen3-TTS),
  and an automatic transcription daemon with LLM correction.
  All models run locally via MLX with OpenAI-compatible APIs.
  Use when the user needs local AI capabilities: text generation, speech recognition,
  embeddings/vector search, OCR, text-to-speech, or batch audio transcription —
  without cloud API calls.
metadata: { "openclaw": { "os": ["darwin"], "requires": { "anyBins": ["python3"] } } }
---

# MLX Local Inference Stack

Full local AI inference on Apple Silicon Macs. All services expose OpenAI-compatible APIs.

## Services Overview

| Service | Port | Access | Models |
|---------|------|--------|--------|
| **LLM + Whisper + Embedding** | 8787 | LAN (`0.0.0.0`) | qwen3-14b, gemma-3-12b, whisper-large-v3-turbo, qwen3-embedding-0.6b/4b |
| **ASR (Qwen3-ASR)** | 8788 | localhost only | Qwen3-ASR-1.7B-8bit |
| **Transcribe Daemon** | — | file-based | Uses ASR + LLM |

LaunchAgents: `com.mlx-server` (8787), `com.mlx-audio-server` (8788), `com.mlx-transcribe-daemon`

---

## 1. LLM — Local Chat Completions

### Models

| Model ID | Params | Best For |
|----------|--------|----------|
| `qwen3-14b` | 14B 4bit | Chinese, deep reasoning (built-in think mode) |
| `gemma-3-12b` | 12B 4bit | English, code generation |

### API

```bash
curl -X POST http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-14b",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

Add `"stream": true` for streaming.

### Python

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8787/v1", api_key="unused")
response = client.chat.completions.create(
    model="qwen3-14b",
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.7, max_tokens=2048
)
print(response.choices[0].message.content)
```

### Qwen3 Think Mode

Qwen3 may include `<think>...</think>` chain-of-thought tags. Strip them:
```python
import re
text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
```

### Model Selection Guide

| Scenario | Recommended |
|----------|-------------|
| Chinese text | `qwen3-14b` |
| Cantonese | `qwen3-14b` |
| English writing | `gemma-3-12b` |
| Code generation | Either |
| Deep reasoning | `qwen3-14b` (think mode) |
| Quick Q&A | `gemma-3-12b` |

---

## 2. ASR — Speech-to-Text

### Qwen3-ASR (best for Chinese/Cantonese)

```bash
curl -X POST http://127.0.0.1:8788/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "model=mlx-community/Qwen3-ASR-1.7B-8bit" \
  -F "language=zh"
```

### Whisper (multilingual, 99 languages)

```bash
curl -X POST http://localhost:8787/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "model=whisper-large-v3-turbo"
```

### ASR Model Comparison

| | Qwen3-ASR (port 8788) | Whisper (port 8787) |
|---|---|---|
| Chinese/Cantonese | **Strong** | Average |
| Multilingual | No | Yes (99 langs) |
| LAN access | No (localhost) | Yes |
| Loading | On-demand | Always loaded |

### Supported audio formats

wav, mp3, m4a, flac, ogg, webm

### Long audio

Split into 10-min chunks first:
```bash
ffmpeg -y -ss 0 -t 600 -i long.wav -ar 16000 -ac 1 chunk_000.wav
```

---

## 3. Embeddings — Text Vectorization

### Models

| Model ID | Size | Use Case |
|----------|------|----------|
| `qwen3-embedding-0.6b` | 0.6B 4bit | Fast retrieval, low latency |
| `qwen3-embedding-4b` | 4B 4bit | High-accuracy semantic matching |

### API

```bash
curl -X POST http://localhost:8787/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-embedding-0.6b", "input": "text to embed"}'
```

### Batch

```bash
curl -X POST http://localhost:8787/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-embedding-4b", "input": ["text 1", "text 2"]}'
```

---

## 4. OCR — Image Text Extraction

### Default Model: PaddleOCR-VL-1.5-6bit

| Item | Value |
|------|-------|
| Model ID | `paddleocr-vl-6bit` |
| Speed | ~185 t/s |
| Memory | ~3.3 GB |
| Prompt | `OCR:` |

### CLI

```bash
cd ~/.mlx-server/venv
python -m mlx_vlm.generate \
  --model mlx-community/PaddleOCR-VL-1.5-6bit \
  --image image.jpg \
  --prompt "OCR:" \
  --max-tokens 512 --temp 0.0
```

### Python

```python
from mlx_vlm import generate, load
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

model, processor = load("mlx-community/PaddleOCR-VL-1.5-6bit")
config = load_config("mlx-community/PaddleOCR-VL-1.5-6bit")
prompt = apply_chat_template(processor, config, "OCR:", num_images=1)
out = generate(model, processor, prompt, "image.jpg",
               max_tokens=512, temperature=0.0, verbose=False)
print(out.text if hasattr(out, "text") else out)
```

### Notes
- Prompt must be exactly `OCR:` for PaddleOCR-VL
- `temperature=0.0` for deterministic output
- RGBA images must be converted to RGB first
- Venv: `~/.mlx-server/venv`

---

## 5. TTS — Text-to-Speech

### Model: Qwen3-TTS (cached, not auto-served)

| Item | Value |
|------|-------|
| Model | Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit |
| Memory | ~2GB |
| Feature | Custom voice cloning |

### CLI

```bash
~/.mlx-server/venv/bin/mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit \
  --text "你好，这是一段测试语音"
```

### As API (via mlx_audio.server on port 8788)

```bash
curl -X POST http://127.0.0.1:8788/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
    "input": "你好世界"
  }' --output speech.wav
```

---

## 6. Transcribe Daemon — Automatic Batch Transcription

Drop audio files into `~/transcribe/` for automatic processing:

1. Daemon detects file (polls every 15s)
2. **Phase 1**: Transcribe via Qwen3-ASR → `filename_raw.md`
3. **Phase 2**: Correct via Qwen3-14B LLM → `filename_corrected.md`
4. Move results to `~/transcribe/done/`

### LLM Correction Rules
- Fix homophone errors (的/得/地, 在/再)
- Preserve Cantonese characters (嘅、唔、咁、喺、冇、佢)
- Add punctuation and paragraphs
- Remove filler words

### Supported formats
wav, mp3, m4a, flac, ogg, webm

---

## Service Management

```bash
# LLM + Whisper + Embedding server (port 8787)
launchctl kickstart -k gui/$(id -u)/com.mlx-server

# ASR server (port 8788)
launchctl kickstart -k gui/$(id -u)/com.mlx-audio-server

# Transcribe daemon
launchctl kickstart gui/$(id -u)/com.mlx-transcribe-daemon

# Logs
tail -f ~/.mlx-server/logs/server.log
tail -f ~/.mlx-server/logs/mlx-audio-server.err.log
tail -f ~/.mlx-server/logs/transcribe-daemon.err.log
```

## Requirements

- Apple Silicon Mac (M1/M2/M3/M4)
- Python 3.10+ with mlx, mlx-lm, mlx-audio, mlx-vlm
- Recommended: 32GB+ RAM for running multiple models
