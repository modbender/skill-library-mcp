# OpenClaw RAG Knowledge System

Full-featured Retrieval-Augmented Generation (RAG) system for OpenClaw - search across chat history, code, documentation, and skills with semantic understanding.

## Features

- **Semantic Search**: Find relevant context by meaning, not just keywords
- **Multi-Source Indexing**: Sessions, workspace files, skill documentation
- **Local Vector Store**: ChromaDB with built-in embeddings (no API keys required)
- **Automatic Integration**: AI automatically consults knowledge base when responding
- **Type Filtering**: Search by document type (session, workspace, skill, memory)
- **Management Tools**: Add/remove documents, view statistics, reset collection

## Quick Start

### Installation

```bash
# Install Python dependency
cd ~/.openclaw/workspace/rag
python3 -m pip install --user chromadb
```

**No API keys required** - This system is fully local:
- Embeddings: all-MiniLM-L6-v2 (downloaded once, 79MB)
- Vector store: ChromaDB (persistent disk storage)
- Data location: `~/.openclaw/data/rag/` (auto-created)

All operations run offline with no external dependencies besides the initial ChromaDB download.

### Index Your Data

```bash
# Index all chat sessions
python3 ingest_sessions.py

# Index workspace code and docs
python3 ingest_docs.py workspace

# Index skill documentation
python3 ingest_docs.py skills
```

### Search the Knowledge Base

```bash
# Interactive search mode
python3 rag_query.py -i

# Quick search
python3 rag_query.py "how to send SMS"

# Search by type
python3 rag_query.py "voip.ms" --type session
python3 rag_query.py "Porkbun DNS" --type skill
```

### Integration in Python Code

```python
import sys
sys.path.insert(0, '/home/william/.openclaw/workspace/rag')
from rag_query_wrapper import search_knowledge

# Search and get structured results
results = search_knowledge("Reddit account automation")
print(f"Found {results['count']} results")

# Format for AI consumption
from rag_query_wrapper import format_for_ai
context = format_for_ai(results)
print(context)
```

## Architecture

```
rag/
├── rag_system.py          # Core RAG class (ChromaDB wrapper)
├── ingest_sessions.py     # Load chat history from sessions
├── ingest_docs.py         # Load workspace files & skill docs
├── rag_query.py           # Search the knowledge base
├── rag_manage.py          # Document management
├── rag_query_wrapper.py   # Simple Python API
└── SKILL.md               # OpenClaw skill documentation
```

Data storage: `~/.openclaw/data/rag/` (ChromaDB persistent storage)

## Usage Examples

### Find Past Solutions

When you encounter a problem, search for similar past issues:

```bash
python3 rag_query.py "cloudflare bypass failed selenium"
python3 rag_query.py "voip.ms SMS client"
python3 rag_query.py "porkbun DNS API"
```

### Search Through Codebase

Find code and documentation across your entire workspace:

```bash
python3 rag_query.py --type workspace "chromedriver setup"
python3 rag_query.py --type workspace "unifi gateway API"
```

### Access Skill Documentation

Quick reference for any openclaw skill:

```bash
python3 rag_query.py --type skill "how to check UniFi"
python3 rag_query.py --type skill "Porkbun DNS management"
```

### Manage Knowledge Base

```bash
# View statistics
python3 rag_manage.py stats

# Delete all sessions
python3 rag_manage.py delete --by-type session

# Delete specific file
python3 rag_manage.py delete --by-source "scripts/voipms_sms_client.py"
```

## How It Works

### Document Ingestion

1. **Session transcripts**: Process chat history from `~/.openclaw/agents/main/sessions/*.jsonl`
   - Handles OpenClaw event format (session metadata, messages, tool calls)
   - Chunks messages into groups of 20 with overlap
   - Extracts and formats thinking, tool calls, and results

2. **Workspace files**: Scans workspace for code, docs, configs
   - Supports: `.py`, `.js`, `.ts`, `.md`, `.json`, `. yaml`, `.sh`, `.html`, `.css`
   - Skips files > 1MB and binary files
   - Chunking for long documents

3. **Skills**: Indexes all `SKILL.md` files
   - Captures skill documentation and usage examples
   - Organized by skill name

### Semantic Search

ChromaDB uses `all-MiniLM-L6-v2` embedding model (79MB) to convert text to vector representations. Similar meanings cluster together, enabling semantic search beyond keyword matching.

### Automatic RAG Integration

When the AI responds to a question that could benefit from context, it automatically:
1. Searches the knowledge base
2. Retrieves relevant past conversations, code, or docs
3. Includes that context in the response

This happens transparently - the AI just "knows" about your past work.

## Configuration

### Custom Session Directory

```bash
python3 ingest_sessions.py --sessions-dir /path/to/sessions
```

### Chunk Size Control

```bash
python3 ingest_sessions.py --chunk-size 30 --chunk-overlap 10
```

### Custom Collection Name

```python
from rag_system import RAGSystem
rag = RAGSystem(collection_name="my_knowledge")
```

## Data Types

| Type | Source | Description |
|------|--------|-------------|
| **session** | `session:{key}` | Chat history transcripts |
| **workspace** | `relative/path` | Code, configs, docs |
| **skill** | `skill:{name}` | Skill documentation |
| **memory** | `MEMORY.md` | Long-term memory entries |
| **manual** | `{custom}` | Manually added docs |
| **api** | `api-docs:{name}` | API documentation |

## Performance

- **Embedding model**: `all-MiniLM-L6-v2` (79MB, cached locally)
- **Storage**: ~100MB per 1,000 documents
- **Indexing time**: ~1,000 docs/min
- **Search time**: <100ms (after first query loads embeddings)

## Troubleshooting

### No Results Found

- Check if anything is indexed: `python3 rag_manage.py stats`
- Try broader queries or different wording
- Try without filters: remove `--type` if using it

### Slow First Search

The first search after ingestion loads embeddings (~1-2 seconds). Subsequent searches are much faster.

### Memory Issues

Reset collection if needed:
```bash
python3 rag_manage.py reset
```

### Duplicate ID Errors

If you see "Expected IDs to be unique" errors:
1. Reset the collection
2. Re-run ingestion
3. The fix includes `chunk_index` in ID generation

### ChromaDB Download Stuck

On first run, ChromaDB downloads the embedding model (~79MB). This takes 1-2 minutes. Let it complete.

## Automatic Updates

### Setup Scheduled Indexing

The RAG system includes an automatic update script that runs daily:

```bash
# Manual test
bash /home/william/.openclaw/workspace/scripts/rag-auto-update.sh
```

**What it does:**
- Detects new/updated chat sessions and re-indexes them
- Re-indexes workspace files (captures code changes)
- Updates skill documentation
- Maintains state to avoid re-processing unchanged files
- Runs via cron at 4:00 AM UTC daily

**Configuration:**
```bash
# View cron job
openclaw cron list

# Edit schedule (if needed)
openclaw cron update <job-id> --schedule "{\"expr\":\"0 4 * * *\"}"
```

**State tracking:** `~/.openclaw/workspace/memory/rag-auto-state.json`
**Log file:** `~/.openclaw/workspace/memory/rag-auto-update.log`

## Moltbook Integration

Share RAG updates and announcements with the Moltbook community.

### Quick Post

```bash
# Post from draft
python3 scripts/moltbook_post.py --file drafts/moltbook-post-rag-release.md

# Post directly
python3 scripts/moltbook_post.py "Title" "Content"
```

### Examples

**Release announcement:**
```bash
python3 scripts/moltbook_post.py --file drafts/moltbook-post-rag-release.md --submolt general
```

**Quick update:**
```bash
python3 scripts/moltbook_post.py "RAG Update" "Fixed path portability issues"
```

### Configuration

To use Moltbook posting, configure your API key:

```bash
# Set environment variable
export MOLTBOOK_API_KEY="your-key-here"

# Or create credentials file
mkdir -p ~/.config/moltbook
cat > ~/.config/moltbook/credentials.json << EOF
{
  "api_key": "moltbook_sk_YOUR_KEY_HERE"
}
EOF
```

Full documentation: `scripts/MOLTBOOK_POST.md`

**Note:** Moltbook posting is optional - core RAG functionality requires no configuration or API keys.

### Rate Limits

- Posts: 1 per 30 minutes
- Comments: 1 per 20 seconds

### Best Practices

### Automatic Update Enabled

The RAG system now automatically updates daily - no manual re-indexing needed.

After significant work, you can still manually update:
```bash
bash /home/william/.openclaw/workspace/scripts/rag-auto-update.sh
```

### Use Specific Queries

Better results with focused queries:
```bash
# Good
python3 rag_query.py "voip.ms getSMS API method"

# Less specific
python3 rag_query.py "API"
```

### Filter by Type

When you know the data type:
```bash
# Looking for code
python3 rag_query.py --type workspace "chromedriver"

# Looking for past conversations
python3 rag_query.py --type session "SMS"
```

### Document Decisions

After important decisions, add to knowledge base:
```bash
python3 rag_manage.py add \
  --text "Decision: Use Playwright not Selenium for Reddit automation. Reason: Better Cloudflare bypass handles. Date: 2026-02-11" \
  --source "decision:reddit-automation" \
  --type "decision"
```

## Limitations

- Files > 1MB are automatically skipped (performance)
- First search is slower (embedding load)
- Requires ~100MB disk space per 1,000 documents
- Python 3.7+ required

## License

MIT License - Free to use and modify

## Contributing

Contributions welcome! Areas for improvement:
- API documentation indexing from external URLs
- File system watch for automatic re-indexing
- Better chunking strategies for long documents
- Integration with external vector stores (Pinecone, Weaviate)

## Documentation Files

- **CHANGELOG.md** - Version history and changes
- **SKILL.md** - OpenClaw skill integration guide
- **package.json** - Skill metadata (no credentials required)
- **LICENSE** - MIT License

## Author

Nova AI Assistant for William Mantly (Theta42)

## Repository

https://openclaw-rag-skill.projects.theta42.com
Published on: clawhub.com