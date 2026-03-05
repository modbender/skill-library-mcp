---
name: mlx-stt
description: Speech-To-Text with MLX (Apple Silicon) and opensource models (default GLM-ASR-Nano-2512) locally.
version: 1.0.7
author: guoqiao
metadata: {"openclaw":{"always":true,"emoji":"🦞","homepage":"https://github.com/guoqiao/skills/blob/main/mlx-stt/mlx-stt/SKILL.md","os":["darwin"],"requires":{"bins":["brew"]}}}
triggers:
- "/mlx-stt <audio>"
- "STT ..."
- "ASR ..."
- "Transcribe ..."
- "Convert audio to text ..."
---

# MLX STT

Speech-To-Text/ASR/Transcribe with MLX (Apple Silicon) and opensource models (default GLM-ASR-Nano-2512) locally.

Free and Accurate. No api key required. No server required.

## Requirements

- `mlx`: macOS with Apple Silicon
- `brew`: used to install deps if not available

## Installation

```bash
bash ${baseDir}/install.sh
```
This script will use `brew` to install these cli tools if not available:
- `ffmpeg`: convert audio format when needed
- `uv`: install python package and run python script
- `mlx_audio`: do the real job

## Usage

To transcribe an audio file, run this script:

```bash
bash  ${baseDir}/mlx-stt.sh <audio_file_path>
```

- First run could be a little slow, since it will need to download model.
- The transcript result will be printed to stdout.
