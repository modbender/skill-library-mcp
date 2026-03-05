---
name: rag
description: Complete RAG (Retrieval-Augmented Generation) system for OpenClaw. Indexes chat sessions, workspace code, documentation, and skills into local ChromaDB for semantic search. Enables finding past solutions, code patterns, and decisions instantly. Uses local embeddings (all-MiniLM-L6-v2) with no API keys required. Automatically ingests and updates knowledge base from ~/.openclaw/agents/main/sessions and workspace files.
---

# OpenClaw RAG Knowledge System

**Retrieval-Augmented Generation for OpenClaw – Search chat history, code, docs, and skills with semantic understanding**

## Overview

This skill provides a complete RAG (Retrieval-Augmented Generation) system for OpenClaw. It indexes your entire knowledge base – chat transcripts, workspace code, skill documentation – and enables semantic search across everything.

**Key features:**
- 🧠 Semantic search across all conversations and code
- 📚 Automatic knowledge base management
- 🔍 Find past solutions, code patterns, decisions instantly
- 💾 Local ChromaDB storage (no API keys required)
- 🚀 Automatic AI integration – retrieves context transparently

## Installation

### Prerequisites

- Python 3.7+
- OpenClaw workspace

### Setup

```bash
# Navigate to your OpenClaw workspace
cd ~/.openclaw/workspace/skills/rag-openclaw

# Install ChromaDB (one-time)
pip3 install --user chromadb

# That's it!
```

## Quick Start

### 1. Index Your Knowledge

```bash
# Index all chat history
python3 ingest_sessions.py

# Index workspace code and docs
python3 ingest_docs.py workspace

# Index skill documentation
python3 ingest_docs.py skills
```

### 2. Search the Knowledge Base

```bash
# Interactive search mode
python3 rag_query.py -i

# Quick search
python3 rag_query.py "how to send SMS via voip.ms"

# Search by type
python3 rag_query.py "porkbun DNS" --type skill
python3 rag_query.py "chromedriver" --type workspace
python3 rag_query.py "Reddit automation" --type session
```

### 3. Check Statistics

```bash
# See what's indexed
python3 rag_manage.py stats
```

## Usage Examples

### Finding Past Solutions

Hit a problem? Search for how you solved it before:

```bash
python3 rag_query.py "cloudflare bypass selenium"
python3 rag_query.py "voip.ms SMS configuration"
python3 rag_query.py "porkbun update DNS record"
```

### Searching Through Codebase

Find specific code or documentation:

```bash
python3 rag_query.py --type workspace "unifi gateway API"
python3 rag_query.py --type workspace "SMS client"
```

### Quick Reference

Access skill documentation without digging through files:

```bash
python3 rag_query.py --type skill "how to monitor UniFi"
python3 rag_query.py --type skill "Porkbun tool usage"
```

### Programmatic Use

From within Python scripts or OpenClaw sessions:

```python
import sys
sys.path.insert(0, '/home/william/.openclaw/workspace/skills/rag-openclaw')
from rag_query_wrapper import search_knowledge, format_for_ai

# Search and get structured results
results = search_knowledge("Reddit account automation")
print(f"Found {results['count']} relevant items")

# Format for AI consumption
context = format_for_ai(results)
print(context)
```

## Files Reference

| File | Purpose |
|------|---------|
| `rag_system.py` | Core RAG class (ChromaDB wrapper) |
| `ingest_sessions.py` | Index chat history |
| `ingest_docs.py` | Index workspace files & skills |
| `rag_query.py` | Search interface (CLI & interactive) |
| `rag_manage.py` | Document management (stats, delete, reset) |
| `rag_query_wrapper.py` | Simple Python API for programmatic use |
| `README.md` | Full documentation |

## How It Works

### Indexing

**Sessions:**
- Reads `~/.openclaw/agents/main/sessions/*.jsonl`
- Handles OpenClaw event format (session metadata, messages, tool calls)
- Chunks messages (20 per chunk, 5 message overlap)
- Extracts and formats thinking, tool calls, results

**Workspace:**
- Scans for `.py`, `.js`, `.ts`, `.md`, `.json`, `.yaml`, `.sh`, `.html`, `.css`
- Skips files > 1MB and binary files
- Chunks long documents for better retrieval

**Skills:**
- Indexes all `SKILL.md` files
- Organized by skill name for easy reference

### Search

ChromaDB uses `all-MiniLM-L6-v2` embeddings to convert text to vectors. Similar meanings cluster together, enabling semantic search by *meaning* not just *keywords*.

### Automatic Integration

When the AI responds, it automatically:
1. Searches the knowledge base for relevant context
2. Retrieves past conversations, code, or docs
3. Includes that context in the response

This happens transparently – the AI "remembers" your past work.

## Management

### View Statistics

```bash
python3 rag_manage.py stats
```

Output:
```
📊 OpenClaw RAG Statistics

Collection: openclaw_knowledge
Total Documents: 635

By Source:
  session-001: 23
  my-script.py: 5
  porkbun: 12

By Type:
  session: 500
  workspace: 100
  skill: 35
```

### Delete Documents

```bash
# Delete all sessions
python3 rag_manage.py delete --by-type session

# Delete specific file
python3 rag_manage.py delete --by-source "scripts/voipms_sms_client.py"

# Reset entire collection
python3 rag_manage.py reset
```

### Add Manual Document

```bash
python3 rag_manage.py add \
  --text "API endpoint: https://api.example.com/endpoint" \
  --source "api-docs:example.com" \
  --type "manual"
```

## Configuration

### Custom Session Directory

```bash
python3 ingest_sessions.py --sessions-dir /path/to/sessions
```

### Chunk Size Control

```bash
python3 ingest_sessions.py --chunk-size 30 --chunk-overlap 10
```

### Custom Collection

```python
from rag_system import RAGSystem
rag = RAGSystem(collection_name="my_knowledge")
```

## Data Types

| Type | Source Format | Description |
|------|--------------|-------------|
| `session` | `session:{key}` | Chat history transcripts |
| `workspace` | `relative/path/to/file` | Code, configs, docs |
| `skill` | `skill:{name}` | Skill documentation |
| `memory` | `MEMORY.md` | Long-term memory entries |
| `manual` | `{custom}` | Manually added docs |
| `api` | `api-docs:{name}` | API documentation |

## Performance

- **Embedding model**: `all-MiniLM-L6-v2` (79MB, cached locally)
- **Storage**: ~100MB per 1,000 documents
- **Indexing**: ~1,000 documents/minute
- **Search**: <100ms (after first query)

## Troubleshooting

### No Results Found

```bash
# Check what's indexed
python3 rag_manage.py stats

# Try broader query
python3 rag_query.py "SMS"  # instead of "voip.ms SMS API endpoint"
```

### Slow First Search

First search loads embeddings (~1-2 seconds). Subsequent searches are instant.

### Duplicate ID Errors

```bash
# Reset and re-index
python3 rag_manage.py reset
python3 ingest_sessions.py
python3 ingest_docs.py workspace
```

### ChromaDB Model Download

First run downloads embedding model (79MB). Takes 1-2 minutes. Let it complete.

## Best Practices

### Re-index Regularly

After significant work:
```bash
python3 ingest_sessions.py  # New conversations
python3 ingest_docs.py workspace  # New code/changes
```

### Use Specific Queries

```bash
# Better
python3 rag_query.py "voip.ms getSMS method"

# Too broad
python3 rag_query.py "SMS"
```

### Filter by Type

```bash
# Looking for code
python3 rag_query.py --type workspace "chromedriver"

# Looking for past conversations
python3 rag_query.py --type session "Reddit"
```

### Document Decisions

After important decisions, add them manually:

```bash
python3 rag_manage.py add \
  --text "Decision: Use Playwright for Reddit automation. Reason: Cloudflare bypass handles" \
  --source "decision:reddit-automation" \
  --type "decision"
```

## Limitations

- Files > 1MB automatically skipped (performance)
- Python 3.7+ required
- ~100MB disk per 1,000 documents
- First search slower (embedding load)

## Integration with OpenClaw

This skill integrates seamlessly with OpenClaw:

1. **Automatic RAG**: AI automatically retrieves relevant context when responding
2. **Session history**: All conversations indexed and searchable
3. **Workspace awareness**: Code and docs indexed for reference
4. **Skill accessible**: Use from any OpenClaw session or script

## Security Considerations

**⚠️ Important Privacy Note:** This RAG system indexes local data, which may contain:
- API keys, tokens, or credentials in session transcripts
- Private messages or personal information
- Tool results with sensitive data
- Workspace configuration files

**Recommended:**
- Review session files before ingestion if concerned about privacy
- Consider redacting sensitive data from session files
- Use `rag_manage.py reset` to delete the entire index when needed
- The ChromaDB persistence at `~/.openclaw/data/rag/` can be deleted to remove all indexed data
- The auto-update script only runs local ingestion - no remote code fetching

**Path Portability:**
All scripts now use dynamic path resolution (`os.path.expanduser()`, `Path(__file__).parent`) for portability across different user environments. No hard-coded absolute paths remain in the codebase.

**Network Calls:**
- The embedding model (all-MiniLM-L6-v2) is downloaded by ChromaDB on first use via pip
- No custom network calls, HTTP requests, or sub-process network operations
- No telemetry or data uploaded to external services (ChromaDB telemetry disabled)
- All processing and storage is local-only

## Example Workflow

**Scenario:** You're working on a new automation but hit a Cloudflare challenge.

```bash
# Search for past Cloudflare solutions
python3 rag_query.py "Cloudflare bypass selenium"

# Result shows relevant past conversation:
# "Used undetected-chromedriver but failed. Switched to Playwright which handles challenges better."

# Now you know the solution before trying it!
```

## Moltbook Integration

Post RAG skill announcements and updates to Moltbook social network.

### Quick Post

```bash
# Post from draft file
python3 scripts/moltbook_post.py --file drafts/moltbook-post-rag-release.md

# Post directly
python3 scripts/moltbook_post.py "Title" "Content"
```

### Usage Examples

**Post release announcement:**
```bash
cd ~/.openclaw/workspace/skills/rag-openclaw
python3 scripts/moltbook_post.py --file drafts/moltbook-post-rag-release.md --submolt general
```

**Post quick update:**
```bash
python3 scripts/moltbook_post.py "RAG Update" "Fixed path portability issues"
```

**Post to submolt:**
```bash
python3 scripts/moltbook_post.py "Feature Drop" "New semantic search" "aiskills"
```

### Configuration

**To use Moltbook posting (optional feature):**

Set environment variable:
```bash
export MOLTBOOK_API_KEY="your-key"
```

Or create credentials file:
```bash
mkdir -p ~/.config/moltbook
cat > ~/.config/moltbook/credentials.json << EOF
{
  "api_key": "moltbook_sk_YOUR_KEY_HERE"
}
EOF
```

**Note:** Moltbook posting is optional for publishing RAG announcements. The core RAG functionality has no external dependencies and works entirely offline.

### Rate Limits

- **Posts:** 1 per 30 minutes
- **Comments:** 1 per 20 seconds

If rate-limited, wait for `retry_after_minutes` shown in error.

### Documentation

See `scripts/MOLTBOOK_POST.md` for full documentation and API reference.

## Repository

https://openclaw-rag-skill.projects.theta42.com

**Published:** clawhub.com
**Maintainer:** Nova AI Assistant
**For:** William Mantly (Theta42)

## License

MIT License - Free to use and modify