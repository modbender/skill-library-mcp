# zettel-link

A suite of Python scripts for semantically searching and linking notes in an Obsidian directory based on embedding similarity.

## Scripts

```
scripts/
├── config.py # Configure the embedding model and provider
├── embed.py  # Embed notes, cached to .embeddings/embeddings.json
├── search.py # Semantic search over embedded notes
└── link.py   # All-pairs similarity → .embeddings/links.json
```

## Quick Start

Install it via npx skills command:

```bash
npx skills install https://github.com/hxy9243/skills/blob/main/zettel-link/
```

## Requirements

- uv 0.10.0+
- Python 3.10+
- One of:
  - [Ollama](https://ollama.com) with `mxbai-embed-large` (local, default)
  - [OpenAI API](https://platform.openai.com/) with `text-embedding-3-small`
  - [Google Gemini API](https://ai.google.dev/) with `text-embedding-004`

## Supported Providers

| Provider | Default Model            | API Key Env     |
|----------|--------------------------|-----------------|
| ollama   | mxbai-embed-large        | *(none)*        |
| openai   | text-embedding-3-small   | OPENAI_API_KEY  |
| gemini   | text-embedding-004       | GEMINI_API_KEY  |

## Security

To prevent suspicious environment scanning, `zettel-link` supports loading API keys from a local `.env` file within the skill directory.

1. Create a `.env` file in the skill root.
2. Add your keys:
   ```bash
   OPENAI_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   ```

The script will check the environment first, then fallback to the `.env` file.


## Idempotency

All scripts are safe to re-run:
- `embed.py` uses mtime-based caching — only re-embeds changed notes
- `search.py` and `link.py` are read-only against the cache
