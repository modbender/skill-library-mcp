# qwenspeak setup

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/psyb0t/docker-qwenspeak/main/install.sh | sudo bash
```

This creates `~/.qwenspeak/` with docker-compose, authorized_keys, and work directory, then drops a `qwenspeak` command into `/usr/local/bin`.

## Models

Download the models you need:

```bash
pip install -U "huggingface_hub[cli]"

# Speech tokenizer (required by all models)
huggingface-cli download Qwen/Qwen3-TTS-Tokenizer-12Hz --local-dir ./Qwen3-TTS-Tokenizer-12Hz

# CustomVoice: 9 preset speakers + emotion control
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --local-dir ./Qwen3-TTS-12Hz-1.7B-CustomVoice
huggingface-cli download Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice --local-dir ./Qwen3-TTS-12Hz-0.6B-CustomVoice

# VoiceDesign: natural language voice descriptions
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --local-dir ./Qwen3-TTS-12Hz-1.7B-VoiceDesign

# Base: voice cloning from reference audio
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-Base --local-dir ./Qwen3-TTS-12Hz-1.7B-Base
huggingface-cli download Qwen/Qwen3-TTS-12Hz-0.6B-Base --local-dir ./Qwen3-TTS-12Hz-0.6B-Base
```

## Starting

```bash
# Add your SSH key
cat ~/.ssh/id_rsa.pub >> ~/.qwenspeak/authorized_keys

# CPU mode
qwenspeak start -d -m /path/to/models

# GPU mode (requires NVIDIA Container Toolkit)
qwenspeak start -d -m /path/to/models --processing-unit cuda

# With resource limits
qwenspeak start -d -m /path/to/models --memory 4g --swap 2g --cpus 4

# Custom port
qwenspeak start -d --port 2223

# GPU with specific device
qwenspeak start -d --processing-unit cuda --gpus 0
```

All flags persist to `~/.qwenspeak/.env` — next `start` reuses the last values.

## Management

```bash
qwenspeak stop                # stop
qwenspeak upgrade             # pull latest image, asks to stop/restart
qwenspeak uninstall           # stop and remove everything
qwenspeak status              # show status
qwenspeak logs                # show container logs
```

## Configuration

| Flag               | Env var                      | Default | Description                          |
| ------------------ | ---------------------------- | ------- | ------------------------------------ |
| `--port`           | `QWENSPEAK_PORT`             | `2222`  | SSH port                             |
| `-m`               | `QWENSPEAK_MODELS_DIR`       | `./models` | Models directory                  |
| `-l`               | `QWENSPEAK_LOGS_DIR`         | `./logs`   | Logs directory                    |
| `--processing-unit`| `QWENSPEAK_PROCESSING_UNIT`  | `cpu`   | Device: cpu, cuda, rocm              |
| `--gpus`           | `QWENSPEAK_GPUS`             | `all`   | GPUs to expose                       |
| `--log-retention`  | `QWENSPEAK_LOG_RETENTION`    | `7d`    | Log retention (s, m, h, d, w)        |
| `--max-queue`      | `QWENSPEAK_MAX_QUEUE`        | `50`    | Max queued jobs                      |
| `--cpus`           | `QWENSPEAK_CPUS`             | `0`     | CPU limit (0 = unlimited)            |
| `--memory`         | `QWENSPEAK_MEMORY`           | `0`     | RAM limit (0 = unlimited)            |
| `--swap`           | `QWENSPEAK_SWAP`             | `0`     | Swap limit (0 = no swap)             |

## Memory Requirements

- **0.6B float32**: ~2.4GB weights + overhead — fits in 4GB
- **1.7B float32**: ~7GB weights — needs 10GB+
- **1.7B bfloat16 (GPU)**: ~3.5GB weights — fits in 6GB VRAM
- **float16 on CPU**: don't. produces inf/nan garbage

## GPU Notes

FlashAttention-2 is included and auto-enables on GPU. It requires fp16/bf16 — if your dtype is float32, it auto-switches to bfloat16.
