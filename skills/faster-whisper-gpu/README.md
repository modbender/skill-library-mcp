# 🎙️ Faster Whisper GPU - OpenClaw Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CUDA](https://img.shields.io/badge/CUDA-11.8%2B-green.svg)](https://developer.nvidia.com/cuda-downloads)

> High-performance local speech-to-text transcription using Faster Whisper with NVIDIA GPU acceleration.

## ✨ Why This Skill?

- **🔒 Privacy First**: Your audio never leaves your machine
- **⚡ GPU Accelerated**: 10-20x faster than CPU transcription
- **💰 Zero API Costs**: Unlimited transcriptions, forever free
- **🌍 99 Languages**: Automatic language detection
- **🎯 Perfect for OpenClaw**: Seamless integration with your agent workflows

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install faster-whisper torch
```

### 2. Verify GPU Support

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 3. Transcribe!

```bash
python transcribe.py audio.mp3
```

## 📖 Usage Examples

### Basic Transcription
```bash
python transcribe.py meeting.mp3
```

### Portuguese Audio to SRT Subtitles
```bash
python transcribe.py podcast.mp3 --language pt --format srt --output podcast.srt
```

### High-Accuracy Mode
```bash
python transcribe.py interview.mp3 --model large-v3 --vad_filter --word_timestamps
```

### Translate to English
```bash
python transcribe.py japanese.mp3 --task translate --format txt
```

## 🛠️ Requirements

### Hardware
- NVIDIA GPU with 4GB+ VRAM (recommended)
- Or CPU-only mode (slower)

### Software
- Python 3.8+
- NVIDIA Drivers
- CUDA Toolkit 11.8+ or 12.x

## 📊 Performance

| Model | VRAM | Speed (RTX 4090) | Accuracy |
|-------|------|------------------|----------|
| tiny | 1 GB | ~32x realtime | Basic |
| base | 1 GB | ~16x realtime | Good |
| small | 2 GB | ~6x realtime | Better |
| medium | 5 GB | ~2x realtime | Great |
| large-v3 | 10 GB | ~1x realtime | Best |

## 🌍 Supported Languages

99 languages including: Portuguese, English, Spanish, French, German, Italian, Japanese, Chinese, Russian, and more.

## 🔧 Troubleshooting

### CUDA Out of Memory
```bash
# Use smaller model or CPU
python transcribe.py audio.mp3 --model tiny --device cpu
```

### Slow Performance
- Check GPU is being used: `nvidia-smi`
- Ensure CUDA is properly installed
- Try reducing model size

## 🤝 Contributing

Contributions welcome! This is an open-source project for the OpenClaw community.

## 📜 License

MIT License - See [LICENSE](LICENSE)

## 🙏 Credits

- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) by SYSTRAN
- [OpenAI Whisper](https://github.com/openai/whisper) - Original model
- [CTranslate2](https://github.com/OpenNMT/CTranslate2) - Inference engine

---

Made with ❤️ for the OpenClaw community