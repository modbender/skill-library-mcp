# Jina AI — Web Reader, Search & DeepSearch

[![ClawHub](https://img.shields.io/badge/ClawHub-Install-blue)](https://clawhub.ai/adhishthite/jina-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

OpenClaw skill for Jina AI APIs. Fetch clean markdown from URLs, search the web, or run deep multi-step research.

**Get your API key:** https://jina.ai/ → Dashboard → API Keys

---

## Features

| Feature | Description | Script |
|---------|-------------|--------|
| **Reader** | Convert any URL → clean markdown | `scripts/jina-reader.sh` |
| **Search** | Web search with LLM-friendly results | `scripts/jina-search.sh` |
| **DeepSearch** | Multi-step research agent | `scripts/jina-deepsearch.sh` |

---

## Installation

### Via ClawHub (recommended)

```bash
openclaw skill install adhishthite/jina-ai
```

### Manual

```bash
git clone https://github.com/adhishthite/jina-ai-skill.git
# Add to your OpenClaw skills directory
```

---

## Configuration

Set your Jina AI API key as an environment variable:

```bash
export JINA_API_KEY="your-api-key"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) for persistence.

---

## Usage

### Reader — Fetch URL as Markdown

```bash
# Basic usage
./scripts/jina-reader.sh https://example.com

# JSON output (includes url, title, content)
./scripts/jina-reader.sh https://example.com --json

# Python version (no external deps)
python3 scripts/jina-reader.py https://example.com
```

### Search — Web Search

```bash
# Basic search
./scripts/jina-search.sh "OpenAI GPT-5"

# JSON output
./scripts/jina-search.sh "Python tutorials" --json

# Site-specific search
./scripts/jina-search.sh "OpenAI site:reddit.com"
```

### DeepSearch — Multi-step Research

```bash
./scripts/jina-deepsearch.sh "What are the latest developments in quantum computing?"
```

DeepSearch performs multiple search + read + reasoning steps to answer complex questions. Can take 30-120 seconds depending on complexity.

---

## API Endpoints

| Endpoint | Base URL | Purpose |
|----------|----------|---------|
| Reader | `https://r.jina.ai/{url}` | Convert any URL → clean markdown |
| Search | `https://s.jina.ai/{query}` | Web search with LLM-friendly results |
| DeepSearch | `https://deepsearch.jina.ai/v1/chat/completions` | Multi-step research agent |

---

## License

MIT © Adhish Thite 2026
