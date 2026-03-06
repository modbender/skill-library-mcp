---
name: perplexity
description: Use Perplexity API for web-grounded AI search. Use when user needs up-to-date information with source citations, factual queries about current events, or research-style answers. Default when user mentions Perplexity or needs current information with references.
---

# Perplexity AI Search (Safe Edition)

## Overview

This skill provides access to the Perplexity API for web-grounded AI search. It combines large language models with real-time web search, providing accurate, up-to-date answers with source citations.

This is a **security-hardened** version that fixes command injection vulnerabilities found in the original `perplexity-bash` skill.

## When to Use Perplexity vs. Built-in Search

**Use Perplexity when:**
- You need **current information** (news, prices, events, recent developments)
- The user asks for **source citations** or references
- The user specifically mentions Perplexity or wants research-style answers

**Use built-in web search when:**
- Simple factual queries
- Quick information lookup
- Basic URL or content retrieval

## Model Selection Guide

| Model | Use Case | Cost |
|-------|----------|------|
| `sonar` | Default search, most queries | Low |
| `sonar-pro` | Advanced search, deeper understanding | Medium |
| `sonar-reasoning` | Complex multi-step reasoning | Medium |
| `sonar-reasoning-pro` | Advanced reasoning with deep content | High |

## Quick Start

### Basic Search

```bash
# Simple query (uses sonar by default)
scripts/perplexity_search.sh "What is the capital of Germany?"

# With a different model
scripts/perplexity_search.sh -m sonar-pro "Latest AI developments"

# Markdown format with citations
scripts/perplexity_search.sh -f markdown "Tesla stock analysis"
```

### Advanced Usage

```bash
# High context for comprehensive results
scripts/perplexity_search.sh -m sonar-reasoning -c high -f markdown \
  "Compare AI models performance benchmarks"

# With custom system prompt
scripts/perplexity_search.sh -s "You are a technology analyst." \
  "Analyze current tech trends"
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-m, --model` | Model to use | `sonar` |
| `-t, --max-tokens` | Maximum tokens (1-4096) | `4096` |
| `--temperature` | Sampling temperature (0.0-1.0) | `0.0` |
| `-c, --context` | Search context: low/medium/high | `medium` |
| `-s, --system` | System prompt | (none) |
| `-f, --format` | Output: text/markdown/json | `text` |
| `--list-models` | List available models | |

## Search Context Size

- **low** - Faster, fewer sources. Good for simple queries.
- **medium** (default) - Balanced for most use cases.
- **high** - Most comprehensive. Best for research.

## Setup Requirements

### API Key Configuration

**Option 1: Config file (recommended)**
Create `config.json` in the skill directory:
```json
{
  "apiKey": "pplx-your-key-here"
}
```

**Option 2: Environment variable**
```bash
export PERPLEXITY_API_KEY="your-key-here"
```

Priority: Config file > environment variable.

### Dependencies

- `bash` (4.0+)
- `curl`
- `python3` (for JSON construction only - no user input is eval'd)

## Security Notes

This version addresses the following vulnerabilities found in the original:

1. **No command injection** - User input is passed to Python via environment variables, never interpolated into code strings
2. **Input validation** - All parameters are validated (numeric ranges, allowed model names, allowed context values)
3. **API key protection** - The Authorization header is passed to curl via a temporary config file (`curl -K`, mode 600) and the request body via stdin (`--data @-`), so neither the API key nor the body appear in process listings (`ps aux`)
4. **Query length limit** - Queries are capped at 8000 characters to prevent denial-of-wallet attacks
5. **Strict model allowlist** - Only known valid models are accepted

## Cost Awareness

Perplexity API is not free. Be mindful of usage:

- **Simple queries**: ~$0.005-$0.015 per query
- **Deep research**: ~$0.015-$0.03+ per query
- Default to `sonar` for most queries to keep costs low.

## Troubleshooting

- **Error: No API key found** - Set up API key as described above
- **Error: curl not found** - Install curl for your system
- **Error: Invalid model** - Use `--list-models` to see available models
