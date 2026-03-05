# Multi-Agent ChromaDB: Hybrid Implementation

## Overview

Implement hybrid ChromaDB with shared + private areas for multi-agent setup.

## Agent List

| Agent ID | Workspace |
|----------|-----------|
| cody | workspace-cody |
| nova | workspace-orchestrator |
| content | workspace-contentwriter |
| data | workspace-data-analyst |
| marketing | workspace-marketing |
| researcher | workspace-researcher |
| scholar | workspace-research-aggregator |
| SEO | workspace-seo |
| social | workspace-social-media-manager |
| startup | workspace-startup-sam |
| orchestrator | workspace-orchestrator |

## Folder Structure

```
~/.openclaw/memory/
├── chroma_shared/           # Shared knowledge (all agents)
│   ├── preferences/
│   ├── projects/
│   └── common/
│
├── chroma_cody/            # Private (cody)
├── chroma_nova/             # Private (nova)
├── chroma_content/          # Private (content)
├── chroma_data/             # Private (data)
├── chroma_marketing/        # Private (marketing)
├── chroma_researcher/       # Private (researcher)
├── chroma_scholar/         # Private (scholar)
├── chroma_seo/              # Private (SEO)
├── chroma_social/           # Private (social)
├── chroma_startup/          # Private (startup)
└── chroma_orchestrator/    # Private (orchestrator)
```

## Implementation

### config.py updates

```python
import os
from pathlib import Path

# Get agent ID from environment
AGENT_ID = os.environ.get("AGENT_ID", "default")

# ChromaDB paths
MEMORY_BASE = Path("~/.openclaw/memory").expanduser()
CHROMA_SHARED = MEMORY_BASE / "chroma_shared"
CHROMA_PRIVATE = MEMORY_BASE / f"chroma_{AGENT_ID}"

def get_chroma_path(use_shared=True):
    """Get ChromaDB path - shared or private"""
    if use_shared:
        return CHROMA_SHARED
    return CHROMA_PRIVATE

def get_chroma_collection(collection_name):
    """Get ChromaDB collection with agent namespace"""
    import chromadb
    client = chromadb.PersistentClient(path=str(get_chroma_path()))
    return client(
.get_or_create_collection        name=f"{AGENT_ID}_{collection_name}"
    )
```

### CLI Updates

```bash
# Store in shared
overkill add "Shared fact" --tier shared

# Store private (default)
overkill add "Private note"

# Search shared
overkill search "query" --tier shared

# Search private (default)
overkill search "query"
```

### Storage Locations

| Memory Type | Location |
|-------------|----------|
| Preferences | chroma_shared |
| Projects | chroma_shared |
| Common knowledge | chroma_shared |
| Daily notes | chroma_{agent} |
| Personal learnings | chroma_{agent} |
| Habits | chroma_{agent} |
| Internal state | chroma_{agent} |

## Migration

```bash
# Create folders
mkdir -p ~/.openclaw/memory/chroma_{cody,nova,content,data,marketing,researcher,scholar,seo,social,startup,orchestrator}
mkdir -p ~/.openclaw/memory/chroma_shared
```

---

*Multi-agent ChromaDB hybrid implementation*
