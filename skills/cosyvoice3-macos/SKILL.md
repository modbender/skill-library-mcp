---
name: cosyvoice3
description: |
  Local text-to-speech using Alibaba's CosyVoice3 on macOS Apple Silicon.
  Supports Chinese, English, Japanese, Korean, and 18+ Chinese dialects.
  Provides zero-shot voice cloning, cross-lingual synthesis, and fine-grained control.
  Use when: (1) User requests local TTS with high-quality Chinese/English voices. 
  (2) Need voice cloning from reference audio. (3) Offline/inference TTS is required.
  (4) User wants natural-sounding speech with emotion/dialect control.
---

# CosyVoice3 TTS

Local text-to-speech using Alibaba's CosyVoice3 on macOS Apple Silicon.

## Overview

CosyVoice3 is an advanced TTS system based on large language models, supporting:
- **9 languages**: Chinese, English, Japanese, Korean, German, Spanish, French, Italian, Russian
- **18+ Chinese dialects**: Cantonese, Sichuan, Dongbei, Shanghai, etc.
- **Zero-shot voice cloning**: Clone any voice from 3-10 seconds of audio
- **Cross-lingual synthesis**: Speak Chinese with English voice or vice versa
- **Fine-grained control**: Emotions, speed, volume via text tags

## Prerequisites

- macOS with Apple Silicon (M1/M2/M3)
- Python 3.10
- Conda installed
- ~5GB disk space for models

## Installation

Run the installation script:

```bash
cd /Users/lhz/.openclaw/workspace/skills/cosyvoice3/scripts
bash install.sh
```

This will:
1. Create conda environment `cosyvoice`
2. Install PyTorch (CPU version for Apple Silicon)
3. Install CosyVoice dependencies
4. Download Fun-CosyVoice3-0.5B model (~2GB)

## Usage

### Quick Start - Basic TTS

**重要**：CosyVoice3 需要在参考文本中添加 `<|endofprompt|>` 标记！

```bash
cd /Users/lhz/.openclaw/workspace/cosyvoice3-repo
export PATH="$HOME/miniconda3/bin:$PATH"
conda activate cosyvoice

python -c "
import sys
sys.path.append('third_party/Matcha-TTS')
from cosyvoice.cli.cosyvoice import AutoModel
import torchaudio

cosyvoice = AutoModel(model_dir='pretrained_models/Fun-CosyVoice3-0.5B')
for i, j in enumerate(cosyvoice.inference_zero_shot(
    '你好，这是CosyVoice3语音合成测试。', 
    '希望你以后能够做的比我还好呦。<|endofprompt|>',  # 注意这个标记！
    'asset/zero_shot_prompt.wav'
)):
    torchaudio.save('output.wav', j['tts_speech'], cosyvoice.sample_rate)
print('Generated: output.wav')
"
```

### Using the TTS Script

Generate speech from text:

```bash
cd /Users/lhz/.openclaw/workspace/skills/cosyvoice3/scripts
conda activate cosyvoice

# Basic TTS with default voice
python tts.py "你好，这是一个测试。"

# With custom reference audio for voice cloning
python tts.py "你好，这是克隆的声音。" --reference /path/to/reference.wav

# Cross-lingual (English text with Chinese voice)
python tts.py "Hello, this is cross-lingual synthesis." --reference asset/zero_shot_prompt.wav --lang en

# With speed control
python tts.py "这是一段快速的语音。" --speed 1.5

# Save to specific path
python tts.py "你好。" --output ~/Desktop/greeting.wav
```

### Available Assets

Reference audio files in `cosyvoice3-repo/asset/`:
- `zero_shot_prompt.wav` - Default Chinese female voice
- `cross_lingual_prompt.wav` - English prompt for cross-lingual

## Advanced Features

### Voice Cloning

Clone a voice from 3-10 seconds of reference audio:

```python
from cosyvoice.cli.cosyvoice import AutoModel
import torchaudio

cosyvoice = AutoModel(model_dir='pretrained_models/Fun-CosyVoice3-0.5B')

# Clone voice and generate
for i, j in enumerate(cosyvoice.inference_zero_shot(
    '这是克隆后的声音在说话。',
    'Reference text transcription',
    '/path/to/reference.wav'
)):
    torchaudio.save('cloned.wav', j['tts_speech'], cosyvoice.sample_rate)
```

### Fine-Grained Control

Control prosody with special tags:

```python
# Add laughter
"他突然[laughter]笑了起来[laughter]。"

# Add breathing
"他说完这句话[breath]，深吸一口气。"

# Strong emphasis
"这是<strong>非常重要</strong>的。"

# Combined
"在面对挑战时，他展现了非凡的<strong>勇气</strong>与<strong>智慧</strong>[breath]。"
```

### Dialect Support

Use instruct mode for dialects:

```python
cosyvoice = AutoModel(model_dir='pretrained_models/CosyVoice-300M-Instruct')

for i, j in enumerate(cosyvoice.inference_instruct(
    '你好，这是测试语音。',
    '中文男',
    '用四川话说这句话<|endofprompt|>'
)):
    torchaudio.save('sichuan.wav', j['tts_speech'], cosyvoice.sample_rate)
```

## Troubleshooting

### Model not found

If you get "model not found" errors, download models manually:

```bash
cd /Users/lhz/.openclaw/workspace/cosyvoice3-repo
export PATH="$HOME/miniconda3/bin:$PATH"
conda activate cosyvoice

python -c "
from modelscope import snapshot_download
snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512', local_dir='pretrained_models/Fun-CosyVoice3-0.5B')
"
```

### Memory issues

For long text, split into sentences:

```python
text = "很长的文本..."
sentences = text.split('。')
for sent in sentences:
    if sent.strip():
        # Process each sentence
```

### Audio format

Reference audio requirements:
- Format: WAV, MP3
- Sample rate: 16kHz+ (automatically resampled)
- Duration: 3-10 seconds optimal
- Content: Clear speech, minimal background noise

## Resources

### Scripts

- `install.sh` - Installation script for macOS
- `tts.py` - Main TTS script with CLI interface
- `download_models.py` - Download pretrained models

### References

- [CosyVoice GitHub](https://github.com/FunAudioLLM/CosyVoice)
- [Fun-CosyVoice3 Demo](https://funaudiollm.github.io/cosyvoice3/)

### Model Files

Located in `cosyvoice3-repo/pretrained_models/`:
- `Fun-CosyVoice3-0.5B/` - Main model (recommended)
- `CosyVoice2-0.5B/` - Previous version
- `CosyVoice-300M/` - Lighter model
- `CosyVoice-300M-SFT/` - SFT version
- `CosyVoice-300M-Instruct/` - Instruct version

## Notes

- First inference takes ~30 seconds (model warmup)
- Subsequent inferences are faster
- Apple Silicon uses CPU mode (no CUDA)
- RTF (real-time factor) ~0.3-0.5 on M-series chips
- Model files are cached locally after first download
