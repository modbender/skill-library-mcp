# Data Pods v0.1 - Usage Reference

## Quick Start

```bash
# List pods
python pod.py list

# Create a pod
python pod.py create my-research --type scholar

# Add a note
python pod.py add my-research --title "Transformer Paper" --content "..." --tags "ai,research"

# Search
python pod.py query my-research --text "transformer"

# Export
python pod.py export my-research --output my-research.zip
```

## As OpenClaw Skill

```bash
# Create pod
python /home/claudio/.openclaw/workspace/skills/data-pods/scripts/pod.py create <name> --type <type>

# Add data
python /home/claudio/.openclaw/workspace/skills/data-pods/scripts/pod.py add <pod> --title "..." --content "..."

# Query
python /home/claudio/.openclaw/workspace/skills/data-pods/scripts/pod.py query <pod> --text "..."

# Export for sharing
python /home/claudio/.openclaw/workspace/skills/data-pods/scripts/pod.py export <pod> --output <path>.zip
```

## Pod Location
Default: `~/.openclaw/data-pods/`

## Tables
- `notes`: id, title, content, tags, created_at, updated_at
- `embeddings`: id, note_id, chunk_text, embedding (future vector store)
