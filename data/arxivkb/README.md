# arxivkb

An arXiv paper crawler with local semantic search (FAISS), topic management, and optional LLM summarization. All embedding is done locally — no cloud APIs required.

Powers the **🔬 ArXiv** app in [PrivateApp](https://github.com/camopel/PrivateApp).

## Install

```bash
python3 scripts/install.py
```

This will:
- Install Python dependencies (`faiss-cpu`, `pdfplumber`, `arxiv`, `numpy`, `tiktoken`)
- Pull the default embedding model via Ollama (`nomic-embed-text`)
- Create the data directory at `~/workspace/arxivkb/`
- Set up a SQLite database with default arXiv categories
- Schedule a daily ingest cron (systemd timer on Linux, launchd on macOS)

## Usage

### Manage topics (arXiv categories)

```bash
# Browse available categories
akb topics browse
akb topics browse "machine learning"

# List enabled categories
akb topics list

# Enable categories
akb topics add cs.AI cs.CV cs.RO stat.ML

# Disable a category
akb topics delete cs.AI
```

### Ingest papers

```bash
# Ingest papers from the last 7 days
akb ingest --days 7

# Dry run (show what would be fetched)
akb ingest --days 3 --dry-run

# Expire old papers
akb expire --days 30
```

### Search papers

```bash
# Semantic search (requires embedding model)
python3 scripts/search.py "transformer attention mechanism" --top 10

# Paper details
akb paper 2310.00001
```

### Stats

```bash
akb stats
```

## Data Directory

Papers are stored in `~/workspace/arxivkb/`:
- `arxivkb.db` — SQLite database (papers, chunks, categories)
- `pdfs/` — Downloaded PDF files
- `faiss/` — FAISS vector index files
- `config.json` — Per-user configuration

## Embedding Models

By default, ArXivKB uses `nomic-embed-text` via [Ollama](https://ollama.ai). Make sure Ollama is running:

```bash
ollama serve
ollama pull nomic-embed-text
```

Alternative models can be configured in `~/workspace/arxivkb/config.json`.

## Background Service

The installer schedules daily paper ingestion:

```bash
# Linux — systemd timer
systemctl --user status akb-crawler.timer
systemctl --user start akb-crawler.service   # run now

# macOS — launchd
launchctl list | grep arxivkb
```

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) for local embeddings
- ~2GB RAM during ingest/search
- ~500MB disk base + ~1.5KB per chunk
- macOS or Linux

## License

MIT
