---
name: telnyx-rag
description: Semantic search and Q&A over workspace files using Telnyx Storage + AI embeddings. Index your memory, knowledge, and skills for natural language retrieval and AI-powered answers.
metadata: {"openclaw":{"emoji":"🧠","requires":{"bins":["python3"],"env":["TELNYX_API_KEY"]},"primaryEnv":"TELNYX_API_KEY"}}
---

# Telnyx RAG Memory

Semantic search and RAG-powered Q&A over your OpenClaw workspace using Telnyx's native embedding, similarity search, and inference APIs.

## Requirements

- **Your own Telnyx API Key** — each user/agent uses their own key
- **Python 3.8+** — stdlib only, no external dependencies
- Get your API key at [portal.telnyx.com](https://portal.telnyx.com/#/app/api-keys)

## Bucket Naming Convention

Use a consistent naming scheme so anyone can adopt this:

```
openclaw-{agent-id}
```

| Agent | Bucket |
|-------|--------|
| Chief (main) | `openclaw-main` |
| Bob the Builder | `openclaw-builder` |
| Voice agent | `openclaw-voice` |
| Your agent | `openclaw-{your-id}` |

**Why?**
- **Predictable**: anyone can find any agent's bucket
- **Collision-free**: scoped to agent, not person or team
- **Discoverable**: `openclaw-*` prefix groups all agent buckets in Telnyx Storage UI

## Quick Start

```bash
cd ~/skills/telnyx-rag

# Set YOUR Telnyx API key (each user/agent uses their own)
echo 'TELNYX_API_KEY=KEY...' > .env

# Run setup with validation
./setup.sh --check    # Validate requirements first
./setup.sh           # Full setup (uses bucket from config.json)

# Search your memory
./search.py "What are my preferences?"

# Ask questions (full RAG pipeline)
./ask.py "What is the porting process?"
```

## What It Does

- **Indexes** your workspace files (MEMORY.md, memory/*.md, knowledge/, skills/)
- **Chunks** large files intelligently (markdown by headers, JSON/Slack by threads)
- **Embeds** content automatically using Telnyx AI
- **Searches** using natural language queries with retry logic
- **Answers questions** using a full RAG pipeline (retrieve → rerank → generate)
- **Prioritizes** results from memory/ (your primary context)
- **Incremental sync** — only uploads changed files
- **Orphan cleanup** — removes deleted files from bucket

## Setup Options

### Option 1: Environment Variable
```bash
export TELNYX_API_KEY="KEY..."
./setup.sh
```

### Option 2: .env File
```bash
echo 'TELNYX_API_KEY=KEY...' > .env
./setup.sh
```

### Validation Mode
```bash
./setup.sh --check    # Validate requirements without making changes
```

### Custom Bucket Name
```bash
./setup.sh my-custom-bucket
```

## Usage

### Ask Questions (RAG Pipeline)

```bash
# Basic question answering
./ask.py "What is Telnyx's porting process?"

# Show retrieved context alongside answer
./ask.py "How do I deploy?" --context

# Use a different model
./ask.py "Explain voice setup" --model meta-llama/Meta-Llama-3.1-8B-Instruct

# More/fewer context chunks
./ask.py "meeting decisions" --num 12

# JSON output for scripting
./ask.py "API usage limits" --json

# Search a different bucket
./ask.py "project timeline" --bucket work-memory
```

### Search Memory

```bash
# Basic search with improved error handling
./search.py "What are David's communication preferences?"

# Search specific bucket
./search.py "meeting notes" --bucket my-other-bucket

# More results with timeout control
./search.py "procedures" --num 10 --timeout 45

# JSON output (for scripts)
./search.py "procedures" --json
```

### Sync Files (with Chunking)

```bash
# Incremental sync with auto-chunking
./sync.py

# Override chunk size (tokens)
./sync.py --chunk-size 600

# Quiet mode for cron jobs
./sync.py --quiet

# Remove orphaned files (including stale chunks)
./sync.py --prune

# Sync + trigger embedding
./sync.py --embed

# Check status
./sync.py --status

# List indexed files (shows chunks too)
./sync.py --list
```

### Watch Mode
```bash
# Watch for changes and auto-sync with chunking
./sync.py --watch
```

### Trigger Embedding

```bash
# Trigger embedding for current bucket
./embed.sh
# OR
./sync.py --embed

# Check embedding status
./sync.py --embed-status <task_id>
```

**Why is this needed?** Uploading files to Telnyx Storage doesn't automatically generate embeddings. The embedding process converts your files into searchable vectors. Without this step, `search.py` and `ask.py` won't return results.

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "bucket": "openclaw-memory",
  "region": "us-central-1",
  "workspace": ".",
  "patterns": [
    "MEMORY.md",
    "memory/*.md",
    "knowledge/*.json",
    "skills/*/SKILL.md"
  ],
  "priority_prefixes": ["memory/", "MEMORY.md"],
  "default_num_docs": 5,
  "chunk_size": 800,
  "ask_model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
  "ask_num_docs": 8,
  "retrieve_num_docs": 20
}
```

### Config Fields

| Field | Default | Description |
|-------|---------|-------------|
| `bucket` | `openclaw-{agent-id}` | Telnyx Storage bucket name (see naming convention) |
| `region` | `us-central-1` | Storage region |
| `workspace` | `.` | Root directory to scan for files |
| `patterns` | (see above) | Glob patterns for files to index |
| `priority_prefixes` | `["memory/", "MEMORY.md"]` | Sources to rank higher in results |
| `exclude` | `["*.tmp", ...]` | Patterns to exclude |
| `chunk_size` | `800` | Target tokens per chunk (~4 chars/token) |
| `ask_model` | `Meta-Llama-3.1-70B-Instruct` | LLM model for ask.py |
| `ask_num_docs` | `8` | Final context chunks for LLM |
| `retrieve_num_docs` | `20` | Initial retrieval count (before reranking) |

## How It Works

```
┌─────────────────┐     ┌──────────────────────────────────┐
│  Your Workspace │     │     Telnyx Cloud                 │
│  ├── memory/    │     │                                  │
│  ├── knowledge/ │──┐  │  Storage: your-bucket/           │
│  └── skills/    │  │  │     └── file__chunk-001.md       │
└─────────────────┘  │  │     └── file__chunk-002.md       │
                     │  │              │                    │
   Smart Chunking ◀──┘  │              ▼ embed             │
   ├── Markdown: split   │     Telnyx AI Embeddings        │
   │   on ## headers     │              │                  │
   ├── JSON/Slack: split │              ▼                  │
   │   by thread/time    │     Similarity Search           │
   └── Metadata tags     │              │                  │
                         └──────────────┼──────────────────┘
                                        │
   ask.py Pipeline:                     │
   ┌─────────────────────────────────┐  │
   │ 1. Retrieve top-20 chunks ◀────┘  │
   │ 2. Rerank (TF-IDF + priority)     │
   │ 3. Deduplicate adjacent chunks    │
   │ 4. Build prompt with top-8        │
   │ 5. Call Telnyx Inference LLM      │
   │ 6. Return answer + sources        │
   └─────────────────────────────────┘
```

## Smart Chunking

Large files are automatically split into semantic chunks before upload:

### Markdown Files
- Split on `##` and `###` headers first
- If a section is still too large, split by paragraph boundaries
- Each chunk gets a metadata header with source, chunk index, and title

### JSON / Slack Exports
- Messages grouped by token budget per chunk
- Extracts: channel name, date range, authors
- Metadata includes Slack-specific fields

### Chunk Naming
Chunks use deterministic filenames:
```
knowledge/meetings.md  →  knowledge/meetings__chunk-001.md
                          knowledge/meetings__chunk-002.md
                          knowledge/meetings__chunk-003.md
```

### Chunk Metadata
Each chunk includes a YAML-style header:
```
---
source: knowledge/meetings.md
chunk: 2/5
title: Q4 Planning Discussion
---

(chunk content here)
```

For Slack exports, additional fields:
```
---
source: slack/general.json
chunk: 3/12
title: general
channel: general
date_range: 2024-01-15 to 2024-01-16
authors: alice, bob, charlie
---
```

### Chunk Lifecycle
- When a source file changes, old chunks are deleted and new ones uploaded
- Chunk mappings tracked in `.sync-state.json`
- `--prune` cleans up orphaned chunks from deleted files

## Reranking (ask.py)

The RAG pipeline uses a multi-signal reranking strategy:

1. **Semantic similarity** — Telnyx embedding distance (certainty score)
2. **Keyword overlap** — TF-IDF weighted term matching with the query
3. **Priority boost** — Chunks from `priority_prefixes` sources ranked higher
4. **Deduplication** — Adjacent chunks from the same source with >80% token overlap are merged

Initial retrieval fetches `retrieve_num_docs` (default 20), reranking selects the best `ask_num_docs` (default 8) for the LLM prompt.

## New Features (v2)

### Smart Chunking
- **Semantic splitting**: Headers for markdown, threads for Slack JSON
- **Metadata headers**: Source, chunk index, title in every chunk
- **Configurable size**: `--chunk-size` flag or `chunk_size` in config
- **Deterministic names**: Reproducible chunk filenames

### RAG Q&A Pipeline (`ask.py`)
- **End-to-end**: Query → retrieve → rerank → generate → answer
- **Telnyx Inference**: Uses Telnyx LLM API for generation
- **Source references**: Every answer includes source file citations
- **Context mode**: `--context` shows retrieved chunks
- **JSON output**: `--json` for structured responses

### Reranking
- **Multi-signal scoring**: Combines embedding similarity + keyword overlap + priority
- **Deduplication**: Removes near-identical adjacent chunks
- **Configurable**: Retrieve 20, use best 8 (tunable)

### Incremental Sync (v1)
- **File hashing**: Tracks SHA-256 hashes in `.sync-state.json`
- **Skip unchanged**: Only uploads modified files
- **Progress tracking**: Shows progress bars for large syncs

### Smart Cleanup
- **`--prune`**: Removes files from bucket that were deleted locally
- **Chunk-aware**: Cleans up orphaned chunks too
- **State tracking**: Maintains sync history and chunk mappings

### Improved Reliability
- **Retry logic**: 3 attempts with exponential backoff
- **Better errors**: Parses Telnyx API error responses
- **Timeout control**: Configurable request timeouts
- **Quiet mode**: `--quiet` flag for cron jobs

## OpenClaw Integration

Add to your `TOOLS.md`:

```markdown
## Semantic Memory & Q&A

Ask questions about your workspace:
\`\`\`bash
cd ~/skills/telnyx-rag && ./ask.py "your question"
\`\`\`

Search memory semantically:
\`\`\`bash
cd ~/skills/telnyx-rag && ./search.py "your query"
\`\`\`
```

### Automated Sync

Add to your heartbeat or cron:
```bash
# Quiet sync with orphan cleanup
cd ~/skills/telnyx-rag && ./sync.py --quiet --prune

# Sync with embedding
cd ~/skills/telnyx-rag && ./sync.py --quiet --embed
```

## Troubleshooting

### Setup Issues

**"Python version too old"**
- Requires Python 3.8+
- Check: `python3 --version`

**"API key test failed"**
- Verify key: `echo $TELNYX_API_KEY`
- Get new key at [portal.telnyx.com](https://portal.telnyx.com/#/app/api-keys)

### Sync Issues

**"Bucket not found"**
```bash
./sync.py --create-bucket
```

**"No results found"**
- Wait 1-2 minutes after sync (embeddings take time)
- Check files uploaded: `./sync.py --list`
- Trigger embedding: `./sync.py --embed`

**"Files not syncing"**
- Check `.sync-state.json` for corruption
- Force re-sync: `rm .sync-state.json && ./sync.py`

### Ask Issues

**"LLM generation failed"**
- Check API key has inference permissions
- Try a different model: `./ask.py "query" --model meta-llama/Meta-Llama-3.1-8B-Instruct`

**"No relevant documents found"**
- Ensure files are synced and embedded
- Try broader query terms

## API Reference

### From Python

```python
from ask import ask
from search import search_memory

# Ask a question (full RAG pipeline)
answer = ask("What is the deployment process?")
print(answer)

# With options
answer = ask(
    "project timeline",
    num_final=5,
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    show_context=True,
    output_json=True,
)
print(answer)

# Basic search
results = search_memory("What do I know about X?", num_docs=5)
print(results)
```

### From Bash

```bash
# Ask and capture answer
answer=$(./ask.py "What are the API limits?" --json)

# Search and capture JSON
results=$(./search.py "query" --json)
```

## Performance Tips

1. **Tune chunk_size** — Smaller chunks (400-600) for precise retrieval, larger (800-1200) for more context
2. **Use `--quiet`** for cron jobs to reduce output
3. **Enable `--prune`** periodically to clean up deleted files
4. **Watch mode** is great for development: `./sync.py --watch`
5. **Batch embedding** by syncing first, then embedding: `./sync.py && ./sync.py --embed`

## Credits

Built for [OpenClaw](https://github.com/openclaw/openclaw) using [Telnyx Storage](https://telnyx.com/products/cloud-storage) and AI APIs.
