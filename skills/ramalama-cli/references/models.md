# Model Guide

This reference covers common open-weight models and practical selection tips for RamaLama workflows.

## Popular Models

### Chat/General Models

| Model | Params | Best For | Notes | Reference Source |
|-------|--------|----------|-------| ---------------- |
| `gpt-oss:20b` | 20B | Highest-quality local general chat + reasoning | Strong quality baseline for agent workflows; heavier memory/latency than 7B-12B class. | `rlcr://gpt-oss-20b` |
| `llama-3.1-8b-instruct` | 8B | Balanced default assistant behavior | Mature ecosystem and good tool-use behavior. Good first pick on 8-16GB VRAM systems. | `rlcr://llama-3.1-8b-instruct` |
| `mistral-small-3.2-24b-instruct` | 24B | Higher-quality chat when hardware allows | Better instruction quality than small 7B/8B class models, but significantly heavier. | `rlcr://mistral-small-3.2-24b-instruct` |
| `Qwen3-8B` | 8.2B | General chat + agent/tool use | Apache-2.0 and strong tool-use profile; good default where available. | `hf://unsloth/Qwen3-8B-GGUF:Q4_K_M` |
| `granite-3.3-8b-instruct` | 8B | Enterprise-safe agentic chat, RAG, and function calling | Apache-2.0 with strong reliability orientation for automation. | `hf://unsloth/granite-3.3-8b-instruct-GGUF:Q4_K_M` |
| `mistral-nemo-instruct-2407` | 12B | Multilingual chat and longer-context work | 128K context and strong multilingual behavior. | `hf://unsloth/Mistral-Nemo-Instruct-2407-GGUF:Q4_K_M` |

### Coding Models

| Model | Params | Best For | Notes | Reference Source |
|-------|--------|----------|-------| ---------------- |
| `Qwen3-Coder-30B-A3B-Instruct` | 30B (A3B active MoE) | Best-quality local coding assistance | Top recommendation when hardware permits. | `rlcr://qwen3-coder-30b-a3b-instruct` ; `hf://unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF:Q4_K_M` |
| `Qwen2.5-Coder Instruct` | 1.5B / 7B / 32B | Balanced code generation, debugging, and refactors | Practical default for local coding workflows. | `hf://unsloth/Qwen2.5-Coder-1.5B-Instruct-GGUF:Q4_K_M` ; `hf://unsloth/Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M` ; `hf://unsloth/Qwen2.5-Coder-32B-Instruct-GGUF:Q4_K_M` ; `rlcr://qwen2.5-coder-3b-instruct` |
| `DeepSeek-Coder-V2-Lite-Instruct` | 16B (2.4B active MoE) | Complex repo reasoning on high-end local systems | Use the Lite variant for local workflows; the full 236B variant is not a practical local default. | `hf://bartowski/DeepSeek-Coder-V2-Lite-Instruct-GGUF/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf` |
| `StarCoder2` | 3B / 7B / 15B | Permissive open coding baseline | Good choice when you need smaller checkpoints and broad OSS ecosystem compatibility. | `hf://second-state/StarCoder2-3B-GGUF/starcoder2-3b-Q4_K_M.gguf` ; `hf://second-state/StarCoder2-7B-GGUF/starcoder2-7b-Q4_K_M.gguf` ; `hf://second-state/StarCoder2-15B-GGUF/starcoder2-15b-Q4_K_M.gguf` |
| `Codestral-22B-v0.1` | 22B | Advanced code completion and infill | High coding quality; check license constraints before production deployment. | `hf://bartowski/Codestral-22B-v0.1-GGUF/Codestral-22B-v0.1-Q4_K_M.gguf` |
| `CodeLlama Instruct` | 7B / 13B / 34B | Legacy-compatible local coding assistant | Mature and widely quantized, but generally lower quality than newer coder families above. | `hf://TheBloke/CodeLlama-7B-Instruct-GGUF/codellama-7b-instruct.Q4_K_M.gguf` ; `hf://TheBloke/CodeLlama-13B-Instruct-GGUF/codellama-13b-instruct.Q4_K_M.gguf` ; `hf://TheBloke/CodeLlama-34B-Instruct-GGUF/codellama-34b-instruct.Q4_K_M.gguf` |

### Embedding Models

| Model | Params | Dimensions | Notes | Reference Source |
|-------|--------|------------|-------| ---------------- |
| `BAAI/bge-m3` | ~570M class | 1024 | Top multilingual retrieval default. Supports dense, sparse, and multi-vector retrieval in one model. | `hf://BAAI/bge-m3` |
| `nomic-ai/nomic-embed-text-v1.5` | ~100M class | 768 (Matryoshka-resizable) | Strong quality/latency tradeoff for local RAG; supports task-prefixed prompts. | `hf://nomic-ai/nomic-embed-text-v1.5` |
| `intfloat/e5-large-v2` | ~335M | 1024 | Reliable retrieval baseline with broad community usage. | `hf://intfloat/e5-large-v2` |
| `jinaai/jina-embeddings-v3` | ~500M class | up to 1024 (Matryoshka/task-adapted) | Strong multilingual retrieval with task-adapter support; tune dimensions for speed/quality. | `hf://jinaai/jina-embeddings-v3` |
| `sentence-transformers/all-MiniLM-L6-v2` | ~22M | 384 | Fastest lightweight option for edge and high-throughput CPU workloads. | `hf://sentence-transformers/all-MiniLM-L6-v2` |

## Model Selection Guide

### By Task Type

- **Quick questions**: 1B–4B instruct models (e.g., Granite 2B, Gemma 2 2B)
- **General chat**: 7B–12B instruct models (Qwen 2.5 7B, Mistral Nemo)
- **Coding**: code-specialized 7B+ models (Qwen3-Coder, Qwen2.5-Coder, StarCoder2)
- **Complex reasoning**: larger 30B+ class models or MoE families
- **Creative/design**: 9B–27B instruct models with higher context and temperature tuning
- **Embeddings**: BGE-M3 / Nomic / E5 depending on language mix + latency needs

### Tool Use Support

Models with generally good tool/function calling behavior:

- Qwen 2.5 Instruct family
- Llama 3.1 Instruct family
- Mistral Instruct family
- Granite Instruct family

Tip: for any model, improve tool reliability with explicit JSON schemas, strict system instructions, and low temperature.

For Hugging Face GGUF models, pin specific variants with either `:<tag>` or `/<file.gguf>`:

```bash
ramalama pull hf://unsloth/Qwen2.5-Coder-32B-Instruct-GGUF:Q4_K_M
ramalama pull hf://unsloth/Qwen2.5-Coder-32B-Instruct-GGUF/Qwen2.5-Coder-32B-Instruct-Q4_K_M.gguf
```

## OpenClaw Integration

Use this guide to pick a model before calling RamaLama commands in skills.

Recommended pattern:

1. Choose model class from the task section above.
2. Start with one-shot validation:
   ```bash
   ramalama run <model> "Reply with a 1-line readiness check."
   ```
3. For services, switch to:
   ```bash
   ramalama serve <model>
   ```
4. For RAG, package docs then query with `--rag`:
   ```bash
   ramalama rag ./docs my-rag
   ramalama run --rag my-rag <model> "Answer from docs only."
   ```

## Hardware Considerations

- **8GB VRAM**: target ~7B class for comfortable performance; 13B may require aggressive quantization/offload.
- **16GB VRAM**: 7B–14B runs well; some 20B+ models are possible with quantization/offload tradeoffs.
- **CPU offload**: llama.cpp can offload to CPU/RAM, but latency rises significantly as offload increases.
- **Macs**: try `--nocontainer` first to use native Metal paths where available.
- **Larger models**: expect slower startup and generation; reduce context (`-c`) first when memory pressure appears.
