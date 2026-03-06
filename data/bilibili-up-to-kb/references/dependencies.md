# Dependency Installation Guide

## Required Tools

### 1. yt-dlp (Video Downloader)
```bash
# macOS
brew install yt-dlp

# Linux
pip install yt-dlp

# Windows
winget install yt-dlp
```

### 2. ffmpeg (Audio Processing)
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg

# Windows
winget install ffmpeg
```

### 3. whisper.cpp (Local Speech-to-Text)
```bash
# macOS (recommended)
brew install whisper-cpp

# Linux — build from source
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp && make -j

# Set the binary path
export WHISPER_CLI=/path/to/whisper-cpp/bin/whisper-cli
```

#### Download Whisper Model

**海外 / Outside China:**
```bash
mkdir -p ~/.whisper-cpp
# Small model (recommended for Chinese)
curl -L -o ~/.whisper-cpp/ggml-small.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"

# OR medium model (better accuracy, slower)
curl -L -o ~/.whisper-cpp/ggml-medium.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin"
```

**国内 / China (HuggingFace 镜像):**
```bash
mkdir -p ~/.whisper-cpp
# 使用 hf-mirror.com 镜像下载
curl -L -o ~/.whisper-cpp/ggml-small.bin \
  "https://hf-mirror.com/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"

# OR medium model
curl -L -o ~/.whisper-cpp/ggml-medium.bin \
  "https://hf-mirror.com/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin"
```

> **Note:** 如果镜像也无法访问，可尝试设置 `HF_ENDPOINT=https://hf-mirror.com` 环境变量，或使用 VPN。

Set model path: `export WHISPER_MODEL=~/.whisper-cpp/ggml-small.bin`

### 4. summarize CLI (Optional — for automated transcript cleaning)
```bash
# macOS
brew install steipete/tap/summarize

# Requires a GEMINI_API_KEY for LLM-based cleaning
export GEMINI_API_KEY=your_key_here
```

If `summarize` is not installed, the cleaning script will pass through the raw transcript, and the agent will handle cleaning interactively.

## Verify Installation
```bash
yt-dlp --version
ffmpeg -version | head -1
whisper-cli --help 2>&1 | head -3
ls ~/.whisper-cpp/ggml-small.bin
```
