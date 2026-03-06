# M2Wise Reference

This document provides an index to all M2Wise reference documentation.

## Table of Contents

- [API Reference](references/api.md) - Core classes and methods
- [Memory System](references/memory.md) - Memory types and extraction
- [Wisdom System](references/wisdom.md) - Wisdom generation and evolution
- [EXAMPLES.md](EXAMPLES.md) - Usage examples

---

## Quick Links

### Installation

```bash
pip install m2wise
```

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# SiliconFlow (recommended for Chinese)
export M2WISE_SILICONFLOW_API_KEY="sk-..."
```

### Basic Usage

```python
from m2wise import M2Wise, M2WiseConfig

engine = M2Wise(config=M2WiseConfig(data_dir="./data"))

# Add conversation
engine.add([{"role": "user", "content": "I prefer concise answers"}], user_id="alice")

# Search
bundle = engine.search("query", user_id="alice")

# Generate wisdom
engine.sleep(user_id="alice")

# Publish wisdom
engine.dream(user_id="alice")
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `data_dir` | str | "./data" | Storage directory |
| `embedder` | str | "openai" | Embedding provider |
| `vector_store` | str | "faiss" | Vector storage |
| `similarity_threshold` | float | 0.7 | Retrieval threshold |

### Memory Types

| Type | Description |
|------|-------------|
| `preference` | User preferences |
| `fact` | Factual information |
| `explicit` | Direct memory requests |
| `commitment` | User commitments |

### Wisdom Types

| Type | Description |
|------|-------------|
| `principle` | Interaction principles |
| `schema` | Behavioral patterns |
| `skill` | Operational skills |
| `causal_hypothesis` | Causal assumptions |

### Core Methods

| Method | Description |
|--------|-------------|
| `engine.add()` | Add conversation to memory |
| `engine.search()` | Search memories and wisdom |
| `engine.sleep()` | Generate wisdom drafts |
| `engine.dream()` | Verify and publish wisdom |
| `engine.list_wisdom()` | List all wisdom |
| `engine.forget()` | Delete memory or wisdom |

---

## Additional Resources

- GitHub: https://github.com/your-repo/m2wise
- PyPI: https://pypi.org/project/m2wise/
- Documentation: See project docs/

---

For complete API details, see [references/api.md](references/api.md)
For memory system details, see [references/memory.md](references/memory.md)
For wisdom system details, see [references/wisdom.md](references/wisdom.md)
