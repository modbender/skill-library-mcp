---
name: nano-web-search
description: AI-powered web search via NanoGPT API with multiple providers (linkup, tavily, exa, kagi, perplexity, valyu, brave). Supports searchResults, sourcedAnswer, and structured output formats.
homepage: https://nano-gpt.com
metadata: {"clawdbot":{"requires":{"bins":["python3","curl"],"packages":["requests"],"env":["NANOGPT_API_KEY"]},"primaryEnv":"NANOGPT_API_KEY"}}
---

# NanoGPT Web Search

AI-powered web search via NanoGPT API with multiple providers.

## Requirements

- `python3` - For payload building and output formatting
- `curl` - For HTTP requests
- `requests` Python package - For Python API usage

## Setup

Install the requests package:

```bash
pip install requests
```

Set your NanoGPT API key as an environment variable:

```bash
export NANOGPT_API_KEY="sk-nano-your-key-here"
```

Get your API key from [nano-gpt.com](https://nano-gpt.com).

## Usage

```bash
# Basic search
./search.sh "your query"

# With specific provider
./search.sh "AI trends 2025" --provider tavily

# Deep search
./search.sh "quantum computing" --depth deep

# Search with date filter
./search.sh "climate news" --from-date 2025-01-01 --to-date 2025-02-18

# Sourced answer (synthesized response with citations)
./search.sh "what is RAG" --output-type sourcedAnswer

# JSON output (for scripting)
./search.sh "python tutorials" --json
```

## Providers

- `linkup` (default) - $0.006 standard, $0.06 deep
- `tavily` - $0.008 standard, $0.016 deep
- `exa` - $0.005 base + per-page
- `kagi` - $0.002 web/news, $0.025 search
- `perplexity` - $0.005 flat
- `valyu` - ~$0.0015/result
- `brave` - $0.005 flat

## Options

- `--provider` - Search provider (default: linkup)
- `--depth` - Search depth: standard or deep
- `--output-type` - Output format: searchResults, sourcedAnswer, structured
- `--from-date` - Start date filter (YYYY-MM-DD)
- `--to-date` - End date filter (YYYY-MM-DD)
- `--include-domains` - Comma-separated domains to include
- `--exclude-domains` - Comma-separated domains to exclude
- `--max-results` - Max results (provider-specific)
- `--json` - Output raw JSON

## Python API

```python
from search import NanoWebSearch

# Pass API key explicitly (recommended)
search = NanoWebSearch(api_key="sk-nano-your-key")

# Or use NANOGPT_API_KEY environment variable
search = NanoWebSearch()

results = search.search("AI trends", provider="tavily", depth="deep")
for r in results['data']:
    print(f"{r['title']}: {r['url']}")
```
