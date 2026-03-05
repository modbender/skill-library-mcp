---
name: simplemem
version: 1.0.0
description: Efficient Lifelong Memory for LLM Agents - semantic compression, cross-session memory, and intent-aware retrieval
metadata: {"openclaw": {"emoji": "🧠", "requires": {"bins": ["python"], "env": ["OPENAI_API_KEY"]}, "primaryEnv": "OPENAI_API_KEY", "homepage": "https://github.com/aiming-lab/SimpleMem"}}
---

# SimpleMem Skill

Integrates SimpleMem: Efficient Lifelong Memory for LLM Agents into OpenClaw.

## What it does

SimpleMem provides semantic memory compression and retrieval for agents:
- **Store**: Compresses interactions into compact memory units
- **Synthesize**: Merges related memories on-the-fly
- **Retrieve**: Intent-aware planning for efficient context retrieval

## Installation

```powershell
# Install Python dependency
pip install simplemem

# Or via repo
git clone https://github.com/aiming-lab/SimpleMem.git
cd SimpleMem
pip install -r requirements.txt
```

## Configuration (Optional - Full Features)

For full SimpleMem features, set your OpenAI API key:
```powershell
$env:OPENAI_API_KEY = "your-openai-key"
```

**Without API key**: Uses JSON fallback (basic keyword search)
**With API key**: Uses full SimpleMem with semantic embeddings

## Usage

### PowerShell Script

```powershell
# Agregar memoria
.\simplemem.ps1 -Action add -Content "El usuario prefiere cafe con leche de avena"

# Buscar memorias
.\simplemem.ps1 -Action search -Query "cafe"

# Ver estadisticas
.\simplemem.ps1 -Action stats
```

### Python API

```python
from simplemem import SimpleMemSystem, set_config, SimpleMemConfig

# With API key (full features)
config = SimpleMemConfig()
config.openai_api_key = "your-key"
set_config(config)
system = SimpleMemSystem()

# Add memory
system.add("User preference: coffee with oat milk", user_id="user1")

# Retrieve
results = system.retrieve("What does user like?", user_id="user1")
```

## Key Features

- **Cross-session memory**: Persistent across conversations (64% better than Claude-Mem)
- **Semantic compression**: 43.24% F1 on LoCoMo benchmark
- **Fast retrieval**: 388ms average retrieval time
- **Multi-index**: Semantic + Lexical + Symbolic layers
- **Fallback**: JSON-based storage when no API key available

## Files

- `simplemem.py` - Main Python wrapper
- `simplemem.ps1` - PowerShell CLI script
- `data/` - Storage directory (created on first use)

## Credits

- Repo: https://github.com/aiming-lab/SimpleMem
- Paper: https://arxiv.org/abs/2601.02553
- Discord: https://discord.gg/KA2zC32M
