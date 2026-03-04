---
name: mlx-audio-server
description: Local 24x7 OpenAI-compatible API server for STT/TTS, powered by MLX on your Mac.
metadata: {"openclaw":{"always":true,"emoji":"🦞","homepage":"https://github.com/guoqiao/skills/blob/main/mlx-audio-server/mlx-audio-server/SKILL.md","os":["darwin"],"requires":{"bins":["brew"]}}}
---

# MLX Audio Server

Local 24x7 OpenAI-compatible API server for STT/TTS, powered by MLX on your Mac.

[mlx-audio](https://github.com/Blaizzy/mlx-audio): The best audio processing library built on Apple's MLX framework, providing fast and efficient text-to-speech (TTS), speech-to-text (STT), and speech-to-speech (STS) on Apple Silicon.

[guoqiao/tap/mlx-audio-server](https://github.com/guoqiao/homebrew-tap/blob/main/Formula/mlx-audio-server.rb): Homebrew Formula to install `mlx-audio` with `brew`, and run `mlx_audio.server` as a LaunchAgent service on macOS.

## Requirements

- `mlx`: macOS with Apple Silicon
- `brew`: used to install deps if not available

## Installation

```bash
bash ${baseDir}/install.sh
```
This script will:
- install ffmpeg/jq with brew if missing.
- install homebrew formula `mlx-audio-server` from `guoqiao/tap`
- start brew service for `mlx-audio-server`

## Usage

STT/Speech-To-Text(default model: **mlx-community/glm-asr-nano-2512-8bit**):
```bash
# input will be converted to wav with ffmpeg, if not yet.
# output will be transcript text only.
bash ${baseDir}/run_stt.sh <audio_or_video_path>
```

TTS/Text-To-Speech(default model: **mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16**):
```bash
# audio will be saved into a tmp dir, with default name `speech.wav`, and print to stdout.
bash ${baseDir}/run_tts.sh "Hello, Human!"
# or you can specify a output dir
bash ${baseDir}/run_tts.sh "Hello, Human!" ./output
# output will be audio path only.
```
You can use both scripts directly, or as example/reference.
