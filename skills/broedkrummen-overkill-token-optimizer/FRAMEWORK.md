# Overkill Token Optimizer - Framework

## Overview

Combine CLI output compression (oktk) with session/memory token optimization for maximum savings.

---

## What It Does

| Optimization | Savings | Type |
|-------------|---------|------|
| **oktk CLI compression** | 60-90% | Command output |
| **Mem0 token reduction** | 80% | Memory context |
| **Session reset** | 100% | When >100k tokens |
| **Session indexing** | Variable | Old conversations |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              OVERKILL TOKEN OPTIMIZER               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │              CLI OUTPUT                      │   │
│  │         (oktk - 60-90% savings)            │   │
│  │                                              │   │
│  │  git/docker/kubectl → compress → AI        │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │           MEMORY CONTEXT                    │   │
│  │      (Mem0 + Tiers - 80% savings)        │   │
│  │                                              │   │
│  │  Memory search → Mem0 → AI                 │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │            SESSION MANAGEMENT               │   │
│  │      (Reset & Summarize - 100%)            │   │
│  │                                              │   │
│  │  Token count → Reset → Summarize            │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Integration

### oktk (CLI Compression)

Works at the command level:
```bash
# Before
git status
# Output: 500 lines → 5000 tokens

# After (oktk)
oktk git status
# Output: 10 lines → 100 tokens
```

### Memory System (Context Compression)

Works at the memory level:
```bash
# Before
Context: All memories → 50000 tokens

# After (Mem0)
Context: Relevant memories only → 10000 tokens
```

---

## Combined Savings

| Scenario | Without | With | Savings |
|----------|---------|------|---------|
| Git status + context | 5500 | 150 | **97%** |
| Docker + context | 8000 | 800 | **90%** |
| Full session | 200000 | 20000 | **90%** |

---

## Implementation

### 1. Install oktk

```bash
# Install oktk CLI
curl -sSL https://get.oktk.io | sh
```

### 2. Configure Compression

```yaml
# .oktk.yaml
commands:
  git: true
  docker: true
  kubectl: true
npm: true

fallback: passthrough
debug: false
```

### 3. Token Tracking

```python
def get_token_usage():
    """Get current token usage"""
    # From session_status or estimate
    pass

def should_optimize():
    """Check if optimization needed"""
    return get_token_usage() > 50000
```

### 4. Hybrid Search

```python
def smart_search(query):
    """Use hybrid search when tokens are high"""
    if should_optimize():
        return hybrid_search(query)  # Semantic + keyword
    return semantic_search(query)  # Just semantic
```

---

## CLI Commands

```bash
# Token stats
token-optimizer stats

# Check optimization level
token-optimizer check

# Compress command (manual)
oktk <command>

# Reset session
token-optimizer reset --confirm

# Index sessions
token-optimizer index
```

---

## Summary

| Component | Savings | Purpose |
|-----------|---------|---------|
| oktk | 60-90% | CLI output compression |
| Mem0 | 80% | Memory context |
| Hybrid search | 20-40% | Better retrieval |
| Reset | 100% | Session restart |

**Combined: Up to 97% token savings!**

---

*Overkill Token Optimizer Framework v1.0*
