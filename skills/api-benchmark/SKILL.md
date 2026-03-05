---
name: api-benchmark
description: Benchmark token generation speed across multiple LLM API providers. Measures TTFT (Time To First Token), tokens-per-second throughput, and total generation time. Use when comparing performance of different API providers, models, or testing API connectivity. Requires OpenCLAW config with provider definitions.
compatibility: Requires Python 3 with requests library. Reads target configuration from ~/.openclaw/openclaw.json. Supports anthropic-messages, openai-completions, and openai-responses API formats.
metadata:
  author: Polar
  version: "1.0.2"
  requires:
    config:
      - ~/.openclaw/openclaw.json
    env:
      - OPENCLAW_CONFIG
---

# API Token Speed Benchmark

This skill benchmarks token generation speed across multiple LLM API providers.

## When to use this skill

Use this skill when you need to:
- Compare token generation speed across different API providers
- Measure latency and throughput of LLM models
- Verify API connectivity and authentication
- Test new API endpoints or models

## How to run benchmarks

### List available targets

```bash
python3 main.py --targets
```

### Run benchmark on a specific target

```bash
python3 main.py run --label <target-label>
```

### Run benchmark on all targets

```bash
python3 main.py run --all
```

### Run preflight check (verify API connectivity)

```bash
python3 main.py check --label <target-label>
python3 main.py check --all
```

### Options

- `-l, --label`: Specific target label to benchmark
- `-a, --all`: Run on all available targets
- `-r, --repeat`: Number of runs per prompt level (default: 1)
- `-c, --category`: Run specific prompt category (can repeat: -c short -c medium). Options: short, medium, long
- `-q, --quiet`: Quiet mode - suppress progress output
- `--timeout N`: Request timeout in seconds (default: 120)
- `--table`: Output as formatted table (default: JSON)

## Configuration

The tool reads configuration from `~/.openclaw/openclaw.json`. Targets are defined in the `models.providers` section with:

- `baseUrl`: API base URL
- `apiKey`: Authentication key (or `${ENV_VAR}` to read from environment variable)
- `api`: API format (anthropic-messages, openai-completions, openai-responses)
- `models`: List of model configurations

**Security Note**: Instead of hardcoding API keys in the config file, use environment variable placeholders:
- `"apiKey": "${ANTHROPIC_API_KEY}"` will read from the `ANTHROPIC_API_KEY` environment variable

Example provider config:
```json
{
  "models": {
    "providers": {
      "my-provider": {
        "baseUrl": "https://api.example.com",
        "apiKey": "sk-xxx",
        "api": "openai-completions",
        "models": [
          { "id": "model-name", "api": "openai-completions" }
        ]
      }
    }
  }
}
```

## Output Metrics

- **TTFT** (Time To First Token): Latency before first token arrives (seconds)
- **TPS** (Tokens Per Second): Generation throughput
- **Total Time**: Full generation duration (seconds)
- **Input/Output Tokens**: Token counts from API usage data (or estimated at 4 chars/token if not provided by API)

Note: Token counts are reported by the API when available. If the API doesn't return token counts, they are estimated at 4 characters per token.

## Example Usage

```bash
# Check if a specific target is reachable
python3 main.py check --label my-provider

# Benchmark a single target
python3 main.py run --label my-provider --repeat 3

# Compare all targets
python3 main.py run --all --table
```
