# LLM Model Comparison

## Qwen3-14B (`qwen3-14b`)

| Item | Value |
|------|-------|
| Full path | `Qwen/Qwen3-14B-MLX-4bit` |
| Parameters | 14B (4bit quantized) |
| Max concurrency | 2 |
| Prompt cache | 10 |

**Strengths**: Chinese/English bilingual, built-in chain-of-thought reasoning (`<think>` mode), long context, strong instruction following.

**Best for**: Chinese tasks, deep reasoning, text correction/proofreading, translation, complex analysis.

## Gemma 3 12B (`gemma-3-12b`)

| Item | Value |
|------|-------|
| Full path | `mlx-community/gemma-3-text-12b-it-4bit` |
| Parameters | 12B (4bit quantized) |
| Max concurrency | 2 |
| Prompt cache | 10 |

**Strengths**: Strong English, code generation, logical reasoning, instruction-tuned.

**Best for**: English tasks, code generation, fast responses, straightforward Q&A.

## Selection Guide

| Scenario | Recommended |
|----------|-------------|
| Chinese text processing | `qwen3-14b` |
| Cantonese content | `qwen3-14b` |
| English writing | `gemma-3-12b` |
| Code generation | Either (both strong) |
| Deep multi-step reasoning | `qwen3-14b` (think mode) |
| Quick factual Q&A | `gemma-3-12b` |
| Translation (any direction) | `qwen3-14b` |

## Also Cached (Not Loaded)

These models are downloaded but not currently served:

- `mlx-community/gemma-3-12b-it-qat-4bit` — alternative Gemma 3 quantization
- `moxin-org/MiniCPM4-SALA-9B-8bit-mlx` — MiniCPM4 9B

To serve them, add entries to `~/.mlx-server/config.yaml` and restart the service.
