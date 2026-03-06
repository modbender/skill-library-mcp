# Create GPU Projects

Transform requests into complete, runnable GPU CLI projects.

## Workflow

1. **Identify task** → Training? Inference? Processing? API?
2. **Select GPU** → Match VRAM to model requirements
3. **Generate project** → gpu.jsonc + scripts + README

## Project Templates

### Image Generation (FLUX/SDXL)

```jsonc
{
  "$schema": "https://gpu-cli.sh/schema/v1/gpu.json",
  "project_id": "image-gen",
  "gpu_types": [{ "type": "RTX 4090" }],
  "min_vram": 24,
  "outputs": ["output/"],
  "ports": [8188],
  "download": [
    { "strategy": "hf", "source": "black-forest-labs/FLUX.1-schnell", "allow": "*.safetensors" }
  ]
}
```

### LLM Inference (vLLM)

```jsonc
{
  "$schema": "https://gpu-cli.sh/schema/v1/gpu.json",
  "project_id": "llm-server",
  "gpu_types": [{ "type": "A100 PCIe 80GB" }],
  "min_vram": 80,
  "ports": [8000],
  "persistent_proxy": true,
  "keep_alive_minutes": 10,
  "health_check_paths": ["/health", "/v1/models"],
  "download": [
    { "strategy": "hf", "source": "meta-llama/Llama-3.1-70B-Instruct", "timeout": 14400 }
  ]
}
```

Start with: `gpu run python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-3.1-70B-Instruct --port 8000`

### LoRA Training

```jsonc
{
  "$schema": "https://gpu-cli.sh/schema/v1/gpu.json",
  "project_id": "lora-training",
  "gpu_types": [{ "type": "RTX 4090" }],
  "min_vram": 24,
  "outputs": ["output/", "logs/", "checkpoints/"],
  "keep_alive_minutes": 10,
  "download": [
    { "strategy": "hf", "source": "stabilityai/stable-diffusion-xl-base-1.0", "allow": "*.safetensors" }
  ],
  "environment": {
    "python": { "requirements": "requirements.txt" }
  }
}
```

### Batch Processing (Whisper)

```jsonc
{
  "$schema": "https://gpu-cli.sh/schema/v1/gpu.json",
  "project_id": "transcription",
  "gpu_types": [{ "type": "RTX 4090" }],
  "min_vram": 12,
  "outputs": ["transcripts/"],
  "download": [
    { "strategy": "hf", "source": "openai/whisper-large-v3" }
  ],
  "environment": {
    "system": { "apt": [{ "name": "ffmpeg" }] }
  }
}
```

## Model Database

### Image Generation

| Model | Source | VRAM | GPU |
|-------|--------|------|-----|
| FLUX.1-dev | `black-forest-labs/FLUX.1-dev` | 24GB | RTX 4090 |
| FLUX.1-schnell | `black-forest-labs/FLUX.1-schnell` | 24GB | RTX 4090 |
| SDXL | `stabilityai/stable-diffusion-xl-base-1.0` | 12GB | RTX 4090 |
| SD 1.5 | `runwayml/stable-diffusion-v1-5` | 8GB | RTX 4070 Ti |

### LLMs

| Model | Source | VRAM (FP16) | VRAM (INT4) |
|-------|--------|-------------|-------------|
| Llama 3.1 8B | `meta-llama/Llama-3.1-8B-Instruct` | 20GB | 6GB |
| Llama 3.1 70B | `meta-llama/Llama-3.1-70B-Instruct` | 140GB | 40GB |
| Mistral 7B | `mistralai/Mistral-7B-Instruct-v0.3` | 16GB | 5GB |
| Qwen2.5 72B | `Qwen/Qwen2.5-72B-Instruct` | 150GB | 45GB |

### Audio/Video

| Model | Source | VRAM | Use Case |
|-------|--------|------|----------|
| Whisper large-v3 | `openai/whisper-large-v3` | 10GB | Transcription |
| XTTS-v2 | `coqui/XTTS-v2` | 8GB | Voice cloning |
| Hunyuan Video | `tencent/HunyuanVideo` | 80GB | Video gen |

## GPU Selection Matrix

| Workload | GPU | $/hr |
|----------|-----|------|
| SD 1.5/SDXL inference | RTX 4090 | $0.44 |
| FLUX inference | RTX 4090 | $0.44 |
| 7B LLM inference | RTX 4090 | $0.44 |
| 70B LLM (quantized) | A100 80GB | $1.79 |
| LoRA training SDXL | RTX 4090 | $0.44 |
| LoRA training FLUX | A100 80GB | $1.79 |
| LLM fine-tune 7B | A100 40GB | $1.29 |
| Video generation | A100 80GB | $1.79 |

## Response Format

```markdown
## Understanding Your Request

[Brief summary]

## Generated Project

### Files Created

1. **gpu.jsonc** - [GPU] @ $X/hr
2. **main.py** - [Description]
3. **requirements.txt** - Dependencies

### Quick Start

```bash
gpu run python main.py
```

### Cost Estimate

- GPU: [type] @ $X/hr
- Estimated time: [duration]
- **Total: ~$X**
```
