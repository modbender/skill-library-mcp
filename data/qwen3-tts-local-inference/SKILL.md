---
name: qwen3-tts-local-inference
description: >
  Generate speech from text using Qwen3-TTS via direct Python inference — no
  server required. Use when: (1) converting text to speech / synthesising audio,
  (2) creating voiceovers or spoken content, (3) cloning a voice from reference
  audio, (4) generating TTS with built-in speakers or custom voice descriptions.
  Supports custom-voice (9 speakers), voice-design (natural language), and
  voice-clone (~3 s reference). Outputs .wav files. Both 0.6B (small, default)
  and 1.7B (large) models available. Runs entirely offline after model download.
---

# Qwen3-TTS — Local Inference (No Server)

Run Qwen3-TTS directly in Python — no HTTP server, no REST API. Call a script
or import the engine in your own code.

## Quick reference

| Mode | What it does | Key args |
|------|-------------|----------|
| **custom-voice** | 9 built-in speakers, optional emotion/style | `--speaker`, `--instruct` |
| **voice-design** | Describe the voice in natural language | `--instruct` (required) |
| **voice-clone** | Clone from ~3 s reference audio | `--ref-audio`, `--ref-text` |

**Available Speakers**

The CustomVoice model includes 9 premium voices:

| Speaker | Language | Description |
|---------|----------|-------------|
| Vivian | Chinese | Bright, slightly edgy young female |
| Serena | Chinese | Warm, gentle young female |
| Uncle_Fu | Chinese | Seasoned male, low mellow timbre |
| Dylan | Chinese (Beijing) | Youthful Beijing male, clear |
| Eric | Chinese (Sichuan) | Lively Chengdu male, husky |
| Ryan | English | Dynamic male, rhythmic |
| Aiden | English | Sunny American male |
| Ono_Anna | Japanese | Playful female, light nimble |
| Sohee | Korean | Warm female, rich emotion |

**Languages:** Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian, Auto

---

## 1 — Setup

Install dependencies once (from the skill directory):

**First-time setup** (one-time):

```bash
bash scripts/setup.sh
```

Custom download location:

```bash
python scripts/download_models.py --model-dir /path/to/models
```

Models are stored under `{baseDir}/models/` by default. Override with
`QWEN_TTS_MODEL_DIR` env var or `--model-dir` flag.

---

## 2 — Generate speech (CLI)

### Custom Voice (default)

```bash
cd {baseDir}
python scripts/tts.py "Hello, how are you today?" --speaker Ryan --language English
```

With emotion/style instruction:

```bash
python scripts/tts.py "Great news everyone!" --speaker Aiden --instruct "cheerful and energetic"
```

### Voice Design

Describe the voice in natural language:

```bash
python scripts/tts.py "Welcome to our show!" \
  --mode voice-design \
  --language English \
  --instruct "Warm, confident female voice in her 30s with a slight British accent"
```

### Voice Clone

Clone a voice from a short (~3 s) reference audio clip:

```bash
python scripts/tts.py "This is spoken in the cloned voice." \
  --mode voice-clone \
  --language English \
  --ref-audio path/to/reference.wav \
  --ref-text "Transcript of the reference audio."
```

### Common options

| Flag | Purpose |
|------|---------|
| `-o output.wav` | Save to exact file path instead of auto-named file |
| `--output-dir DIR` | Override output directory (default: `tts_output/`) |
| `--model-dir DIR` | Override model directory |
| `--json` | Print result as JSON |
| `-v` | Verbose logging |

---

## 3 — Python API

Use the engine directly in code:

```python
import sys
sys.path.insert(0, "{baseDir}/scripts")

from inference import TTSInferenceEngine

engine = TTSInferenceEngine(
    model_dir="{baseDir}/models",   # optional, uses default if omitted
    output_dir="./tts_output",       # optional
)

result = engine.generate_custom_voice(
    text="Hello world!",
    language="English",
    speaker="Ryan",
    instruct="calm and professional",
)
print(result)
# {"file": "tts_output/custom_voice_20260218_...wav", "duration_s": 1.23, "inference_s": 4.56}
```

Available methods:
- `engine.generate_custom_voice(text, language, speaker, instruct)`
- `engine.generate_voice_design(text, language, instruct)`
- `engine.generate_voice_clone(text, language, ref_audio, ref_text)`
- `engine.status()` — returns loaded variant, device, paths

---

## 4 — Configuration

All settings are controlled via environment variables. Set them before running.

| Variable | Default | Description |
|----------|---------|-------------|
| `QWEN_TTS_MODEL_SIZE` | `small` | `small` (0.6B) or `large` (1.7B) |
| `QWEN_TTS_MODEL_DIR` | `{baseDir}/models` | Where model weights are stored |
| `QWEN_TTS_DEVICE` | auto (`cuda:0` or `cpu`) | Inference device |
| `QWEN_TTS_DTYPE` | auto (`bfloat16` / `float32`) | Model precision |
| `QWEN_TTS_OUTPUT_DIR` | `./tts_output` | Where generated .wav files are saved |

Switch to the 1.7B model:

```bash
set QWEN_TTS_MODEL_SIZE=large
python scripts/tts.py "Hello world"
```

Use a custom model directory:

```bash
set QWEN_TTS_MODEL_DIR=D:\my-models\qwen-tts
python scripts/tts.py "Hello world"
```

---

## Important notes

- **Small model (0.6B) is the default.** It uses less RAM and is faster.
  Switch to `large` (1.7B) for higher quality.
- **CPU inference is slow.** Expect 30-120 s per sentence for the 1.7B model.
  The 0.6B model is roughly 2x faster.
- Only **one model variant** is loaded at a time. Switching modes (e.g.
  custom-voice to voice-clone) triggers a model swap.
- Output `.wav` files land in `tts_output/` by default.
- Models are downloaded to `{baseDir}/models/` by default. Run
  `download_models.py --size all` to pre-download both sizes for offline use.
- Voice Design mode has **no 0.6B variant** — it always uses the 1.7B model
  regardless of `QWEN_TTS_MODEL_SIZE`.
