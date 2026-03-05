---
name: data-pods
description: Create and manage modular portable database pods (SQLite + metadata + embeddings). Includes document ingestion with embeddings for semantic search. Full automation - just ask.
---

# Data Pods

## Overview
Create and manage portable, consent-scoped database pods. Handles document ingestion with embeddings and semantic search.

## Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Ingestion  │ ──► │   DB Pods   │ ──► │  Generation │
│  (ingest)   │     │  (storage)  │     │   (query)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Triggers
- "create a pod" / "new pod"
- "list my pods" / "what pods do I have"
- "add to pod" / "add note" / "add content"
- "query pod" / "search pod"
- "ingest documents" / "add files"
- "semantic search" / "find相关内容"
- "export pod" / "pack pod"

## Core Features

### 1. Create Pod
When user asks to create a pod:
1. Ask for pod name and type (scholar/health/shared/projects)
2. Run: `python3 .../scripts/pod.py create <name> --type <type>`
3. Confirm creation

### 2. Add Content (Manual)
When user asks to add content:
1. Ask for pod name, title, content, tags
2. Run: `python3 .../scripts/pod.py add <pod> --title "<title>" --content "<content>" --tags "<tags>"`
3. Confirm

### 3. Ingest Documents (Automated)
When user wants to ingest files:
1. Ask for pod name and folder path
2. Run: `python3 .../scripts/ingest.py ingest <pod> <folder>`
3. Supports: PDF, TXT, MD, DOCX, PNG, JPG
4. Auto-embeds text (if sentence-transformers installed)

### 4. Semantic Search
When user wants to search:
1. Ask for pod name and query
2. Run: `python3 .../scripts/ingest.py search <pod> "<query>"`
3. Returns ranked results with citations

### 5. Query (Basic)
When user asks to search notes:
1. Run: `python3 .../scripts/pod.py query <pod> --text "<query>"`

### 6. Export
When user asks to export:
1. Run: `python3 .../scripts/podsync.py pack <pod>`

## Dependencies
```bash
pip install PyPDF2 python-docx pillow pytesseract sentence-transformers
```

## Storage Location
`~/.openclaw/data-pods/`

## Key Commands
```bash
# Create pod
python3 .../scripts/pod.py create research --type scholar

# Add note
python3 .../scripts/pod.py add research --title "..." --content "..." --tags "..."

# Ingest folder
python3 .../scripts/ingest.py ingest research ./documents/

# Semantic search
python3 .../scripts/ingest.py search research "transformers"

# List documents
python3 .../scripts/ingest.py list research

# Query notes
python3 .../scripts/pod.py query research --text "..."
```

## Notes
- Ingestion auto-chunks large documents
- Embeddings enable semantic search
- File hash prevents duplicate ingestion
- All data stored locally in SQLite
