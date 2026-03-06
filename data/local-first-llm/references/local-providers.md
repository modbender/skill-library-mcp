# Local LLM Provider Setup

## Ollama (Recommended)

**Install**

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

**Start server**

```bash
ollama serve
```

**Pull recommended models**

```bash
ollama pull llama3.2          # 3B — fast, great for simple tasks
ollama pull mistral           # 7B — good balance of speed/quality
ollama pull deepseek-r1:7b    # 7B — strong reasoning
ollama pull nomic-embed-text  # embeddings
```

**Test**

```bash
curl http://localhost:11434/api/generate \
  -d '{"model":"llama3.2","prompt":"Hello","stream":false}'
```

---

## LM Studio

Download from https://lmstudio.ai

1. Install and launch LM Studio
2. Download a model from the Discover tab
3. Go to **Local Inference Server** → click **Start**
4. Default: `http://localhost:1234` (OpenAI-compatible)

**Test**

```bash
curl http://localhost:1234/v1/models
```

---

## llamafile

Download from https://github.com/Mozilla-Ocho/llamafile/releases

```bash
chmod +x phi-2.Q4_K_M.llamafile
./phi-2.Q4_K_M.llamafile --server --nobrowser --port 8080
```

**Test**

```bash
curl http://localhost:8080/v1/models
```

---

## Model Selection Guide

| Use Case             | Recommended Model | Provider  |
| -------------------- | ----------------- | --------- |
| Quick Q&A / chat     | `llama3.2:3b`     | Ollama    |
| Summarization        | `mistral:7b`      | Ollama    |
| Code tasks           | `deepseek-r1:7b`  | Ollama    |
| Reasoning / analysis | `deepseek-r1:14b` | Ollama    |
| Low-memory host      | `phi-2`           | llamafile |

---

## Checking Provider Status

Run `check_local.py` to see what's running:

```bash
python3 skills/local-first-llm/scripts/check_local.py
```

Example output:

```json
{
  "any_available": true,
  "best": {
    "provider": "ollama",
    "url": "http://localhost:11434",
    "models": ["llama3.2", "mistral"]
  },
  "providers": [
    { "available": true, "provider": "ollama", "models": ["llama3.2", "mistral"] },
    { "available": false, "provider": "lm-studio", "models": [] },
    { "available": false, "provider": "llamafile", "models": [] }
  ]
}
```
