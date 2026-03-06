---
name: ollama-hub
description: Manage, benchmark, and switch between local Ollama models with
  performance comparison.
---


# Ollama Hub

Manage and benchmark local Ollama models.

**Use when** listing models, pulling new ones, benchmarking performance, or comparing models.

## Requirements

- Ollama installed and running (`ollama serve` or systemd service)
- No API keys needed

## Instructions

1. **List installed models**:
   ```bash
   ollama list                    # name, size, modified date
   ollama show <model>            # detailed info (parameters, template, license)
   ```

2. **Pull / remove models**:
   ```bash
   ollama pull llama3.3:70b       # download a model
   ollama pull mistral:latest     # latest version
   ollama rm <model>              # remove (confirm with user first!)
   ```

3. **Benchmark a model**:
   ```bash
   # Time a response
   time ollama run <model> "Explain quantum computing in 3 sentences" --verbose 2>&1

   # Extract tokens/sec from verbose output
   ollama run <model> "Hello" --verbose 2>&1 | grep "eval rate"
   ```

4. **Compare models** — run same prompt across multiple models:
   ```
   ## 📊 Ollama Model Benchmark
   **Prompt:** "Explain quantum computing in 3 sentences"
   **Hardware:** [CPU/GPU specs]

   | Model | Size | Tokens/sec | Response Time | Quality |
   |-------|------|-----------|--------------|---------|
   | llama3.3:8b | 4.7GB | 42 t/s | 2.1s | ⭐⭐⭐⭐ |
   | mistral:7b | 4.1GB | 48 t/s | 1.8s | ⭐⭐⭐ |
   | phi3:mini | 2.3GB | 65 t/s | 1.2s | ⭐⭐⭐ |
   ```

5. **Check Ollama status**:
   ```bash
   curl -s http://localhost:11434/api/tags | jq .    # API check
   systemctl status ollama                            # service status
   ollama ps                                          # running models
   ```

## Model Naming

Format: `name:tag` — e.g., `llama3.3:8b`, `mistral:latest`, `codellama:13b-instruct`

Common tags: `latest`, `7b`, `13b`, `70b`, `instruct`, `code`

## Edge Cases

- **Ollama not running**: Start with `ollama serve` or `systemctl start ollama`.
- **Insufficient disk space**: Check `df -h` before pulling large models. 70B models need ~40GB.
- **Insufficient RAM**: Models need RAM ≈ model size. 7B ≈ 8GB RAM, 70B ≈ 48GB RAM.
- **GPU vs CPU**: Performance varies dramatically. Note hardware in benchmarks.
- **Model not found**: Check spelling. Use `ollama list` to see available names. Search at [ollama.com/library](https://ollama.com/library).
- **Slow downloads**: Large models take time. Use `ollama pull` with patience; it supports resume.

## Troubleshooting

- **Port 11434 in use**: Another Ollama instance may be running. `lsof -i :11434`.
- **CUDA errors**: Check GPU drivers with `nvidia-smi`. Reinstall Ollama if needed.
- **Model corrupted**: Remove and re-pull: `ollama rm <model> && ollama pull <model>`.
