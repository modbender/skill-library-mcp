---
name: faster-whisper-gpu
description: High-performance local speech-to-text transcription using Faster Whisper with NVIDIA GPU acceleration. Transcribe audio files locally without sending data to external services.
homepage: https://github.com/FelipeOFF/faster-whisper-gpu
metadata:
  clawdbot:
    emoji: 🎙️
    category: audio
    tags:
      - transcription
      - stt
      - speech-to-text
      - whisper
      - gpu
      - cuda
      - local
      - privacy
    requires:
      bins:
        - python3
      python_packages:
        - faster-whisper
        - torch
    install:
      - id: pip
        kind: pip
        packages:
          - faster-whisper
          - torch
        label: Install faster-whisper and PyTorch
---

# 🎙️ Faster Whisper GPU

High-performance local speech-to-text transcription using [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) with NVIDIA GPU acceleration.

## ✨ Features

- **🚀 GPU Accelerated**: Uses NVIDIA CUDA for blazing-fast transcription
- **🔒 100% Local**: No data leaves your machine. Complete privacy.
- **💰 Free Forever**: No API costs. Run unlimited transcriptions.
- **🌍 Multilingual**: Supports 99 languages with automatic detection
- **📁 Multiple Formats**: Input: MP3, WAV, FLAC, OGG, M4A. Output: TXT, SRT, JSON
- **🎯 Multiple Models**: From tiny (fast) to large-v3 (most accurate)
- **🎬 Subtitle Generation**: Create SRT files with word-level timestamps

## 📋 Requirements

### Hardware
- **NVIDIA GPU** with CUDA support (recommended: 4GB+ VRAM)
- Or CPU-only mode (slower but works on any machine)

### Software
- Python 3.8+
- NVIDIA drivers (for GPU support)
- CUDA Toolkit 11.8+ or 12.x

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install faster-whisper torch

# Verify GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Basic Usage

```bash
# Transcribe an audio file (auto-detects GPU)
python transcribe.py audio.mp3

# Specify language explicitly
python transcribe.py audio.mp3 --language pt

# Output as SRT subtitles
python transcribe.py audio.mp3 --format srt --output subtitles.srt

# Use larger model for better accuracy
python transcribe.py audio.mp3 --model large-v3
```

## 🔧 Advanced Usage

### Command Line Options

```bash
python transcribe.py <audio_file> [options]

Options:
  --model {tiny,base,small,medium,large-v1,large-v2,large-v3}
                        Model size to use (default: base)
  --language LANG       Language code (e.g., 'pt', 'en', 'es'). Auto-detect if not specified.
  --format {txt,srt,json,vtt}
                        Output format (default: txt)
  --output FILE         Output file path (default: stdout)
  --device {cuda,cpu}   Device to use (default: cuda if available)
  --compute_type {int8,int8_float16,int16,float16,float32}
                        Computation precision (default: float16)
  --task {transcribe,translate}
                        Task: transcribe or translate to English (default: transcribe)
  --vad_filter          Enable voice activity detection filter
  --vad_parameters MIN_DURATION_ON,MIN_DURATION_OFF
                        VAD parameters as comma-separated values
  --condition_on_previous_text
                        Condition on previous text (default: True)
  --initial_prompt PROMPT
                        Initial prompt to guide transcription
  --word_timestamps     Include word-level timestamps (for SRT/JSON)
  --hotwords WORDS      Comma-separated hotwords to boost recognition
```

### Examples

#### Portuguese Transcription with SRT Output
```bash
python transcribe.py meeting.mp3 --language pt --format srt --output meeting.srt
```

#### English Translation from Any Language
```bash
python transcribe.py japanese_audio.mp3 --task translate --format txt
```

#### High-Accuracy Mode with Large Model
```bash
python transcribe.py podcast.mp3 --model large-v3 --vad_filter --word_timestamps
```

#### CPU-Only Mode (no GPU)
```bash
python transcribe.py audio.mp3 --device cpu --compute_type int8
```

## 🐍 Python API

```python
from faster_whisper import WhisperModel

# Load model
model = WhisperModel("base", device="cuda", compute_type="float16")

# Transcribe
segments, info = model.transcribe("audio.mp3", language="pt")

print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

## 📊 Model Sizes & VRAM Requirements

| Model    | Parameters | VRAM Required | Relative Speed | Accuracy |
|----------|------------|---------------|----------------|----------|
| tiny     | 39 M       | ~1 GB         | ~32x           | Basic    |
| base     | 74 M       | ~1 GB         | ~16x           | Good     |
| small    | 244 M      | ~2 GB         | ~6x            | Better   |
| medium   | 769 M      | ~5 GB         | ~2x            | Great    |
| large-v3 | 1550 M     | ~10 GB        | 1x             | Best     |

*Benchmarks measured on NVIDIA RTX 4090*

## 🔍 Supported Languages

Faster Whisper supports 99 languages including:
- **Portuguese** (`pt`)
- **English** (`en`)
- **Spanish** (`es`)
- **French** (`fr`)
- **German** (`de`)
- **Italian** (`it`)
- **Japanese** (`ja`)
- **Chinese** (`zh`)
- **Russian** (`ru`)
- **And 90+ more...**

## 🛠️ Troubleshooting

### CUDA Out of Memory
```bash
# Use smaller model
python transcribe.py audio.mp3 --model tiny

# Or use CPU
python transcribe.py audio.mp3 --device cpu

# Or reduce precision
python transcribe.py audio.mp3 --compute_type int8
```

### Model Download Issues
Models are automatically downloaded on first use to `~/.cache/huggingface/hub/`.
If behind a proxy, set:
```bash
export HF_HOME=/path/to/custom/cache
```

### Slow Transcription
- Ensure GPU is being used: check `nvidia-smi` during transcription
- Use smaller model for faster results
- Enable VAD filter to skip silent parts

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

Faster Whisper is developed by [SYSTRAN](https://github.com/SYSTRAN/faster-whisper) and based on OpenAI's Whisper.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Original model
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) - Optimized implementation
- [CTranslate2](https://github.com/OpenNMT/CTranslate2) - Fast inference engine

---

**Made with ❤️ for the OpenClaw community**