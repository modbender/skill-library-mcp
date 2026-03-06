# Homebrew Formula mlx-audio-server

[mlx-audio](https://github.com/Blaizzy/mlx-audio) is an audio processing library built on Apple's MLX framework for text-to-speech (TTS), speech-to-text (STT), and speech-to-speech (STS) on Apple Silicon.

Currently, it is a python package with a few cli tools such as `mlx_audio.server`. It's dependencies for server is not working properly (yet), and has no builtin support to run it as system service in background.

This Homebrew Formula re-packages it for homebrew with missing deps, and the main focus is to add LaunchAgent service support for the `mlx_audio.server` on macOS, so you can use it as an 24x7 local OpenAI-compatible API server.

## Installation

Tap and install:

```bash
# install the formula with cli tools, not only server
brew install --HEAD guoqiao/tap/mlx-audio-server

# start the mlx-audio.server as a LaunchAgent service
brew services start mlx-audio-server

# verify
curl -Ss http://localhost:8899/v1/models
```

## Usage
Here are examples to use `GLM-ASR-Nano-2512` model for STT with different ways:

with curl:
```
bash stt_glmasr.sh  path/to/audio
```

with openai python sdk:
```
uv run openai_api_transcribe.py path/to/audio
```

with Spokenly iOS/macOS app, as OpenAI Compatible API:
```
URL: http://<IP>:8899
Model: mlx-community/glm-asr-nano-2512-8bit
API KEY: <blank>
```
NOTE: `/v1` is not needed in URL here.


## About

This is a Homebrew tap for the mlx-audio Python package, providing fast and efficient audio processing on Apple Silicon using MLX framework.

For more information, visit the [mlx-audio repository](https://github.com/Blaizzy/mlx-audio).
