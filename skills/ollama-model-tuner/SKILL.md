---
summary: "Ollama Model Tuner: Locally fine-tune prompts, LoRAs, and models with Ollama for custom tasks."
description: "Optimize Ollama models/prompts using local datasets, eval metrics, and iterative tuning. No cloud needed."
triggers:
  - "tune ollama"
  - "optimize ollama model"
  - "fine-tune local LLM"
  - "ollama prompt engineer"
read_when:
  - "ollama tune" in message
  - "model fine-tune" in message
---

# Ollama Model Tuner v1.0.0

## 🎯 Purpose
- Prompt engineering & A/B testing
- Modelfile customization
- LoRA fine-tuning with local data
- Performance benchmarking

## 🚀 Quick Start
```
!ollama-model-tuner --model llama3 --dataset ./data.json --task classification
```

## Files
- `scripts/tune.py`: Python tuner with eval loop
- `prompts/system.md`: Base system prompts

## Supported
Ollama 0.3+, Python 3.10+, datasets in JSONL/CSV.
