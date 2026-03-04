# Local Memory Search

Lightweight semantic search for OpenClaw memory files. No external API needed.

## Usage

```bash
python3 search.py "your query"
```

Build index:
```bash
python3 search.py --build
```

## Features

- Searches MEMORY.md and memory/*.md
- TF-IDF based semantic matching
- Zero external dependencies
- Fast local execution
- Returns top snippets with file path and line numbers

## How It Works

1. Builds inverted index of all memory files
2. Uses TF-IDF scoring for relevance
3. Returns ranked results with context

## Requirements

- Python 3.8+
- No pip packages needed (uses stdlib only)
