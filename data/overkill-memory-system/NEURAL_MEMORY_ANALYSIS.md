# Deep Analysis: neural-memory Integration

## Overview

**neural-memory** is a brain-inspired memory system using neural graphs and spreading activation. Very similar to what we've built - but with different implementation!

---

## What Makes It Unique

### 1. Spreading Activation
Instead of vector search, memories are retrieved through "activation spreading":
```
Query: "auth bug"
  → Activate "auth" neurons
  → Spread to connected neurons
  → Activate "bug" neurons
  → Return connected chain
```

### 2. Neural Graph Structure
```
┌─────────────────────────────────────────┐
│           MEMORY NEURONS                │
│                                         │
│    [Auth]──────[Bug]──────[Fix]        │
│       │            │           │        │
│       └────────────┼───────────┘        │
│                    │                    │
│              [CAUSED_BY]                │
│                    │                    │
│              [Outage]                   │
│                    │                    │
│              [Tuesday]                   │
└─────────────────────────────────────────┘
```

### 3. Memory Types
- **fact**: Factual information
- **decision**: Decisions made
- **insight**: Ideas and insights
- **todo**: Tasks with expiry
- **experience**: Experiences

---

## Our Current Architecture

```
QUERY → UltraHot → Cache → Compiled → Emotion → Bloom → Mem0 → Tiers → Rank → Results
              │
              └──────── Brain Regions (Hippocampus, Amygdala, VTA, Basal Ganglia, Insula)
```

### What's Similar

| neural-memory | Our System |
|--------------|------------|
| Spreading activation | Brain regions (6 regions) |
| Facts/decisions | Memory tiers |
| Multi-hop recall | Parallel tier search |
| Decay/consolidation | Vestige (FSRS-6) |

---

## Integration Options

### Option 1: Keep Separate (Recommended)
- neural-memory has different use case (code indexing, causal chains)
- Our system is more comprehensive
- Use neural-memory for specific tasks (codebase Q&A)

### Option 2: Replace ChromaDB
- Replace vector search with spreading activation
- More "brain-like" retrieval
- Risk: Less proven, more complex

### Option 3: Add as Additional Layer
- Add neural-memory as extra retrieval option
- Toggle between vector search and spreading activation
- Best of both worlds

---

## What neural-memory Adds

| Feature | Value for Us | Complexity |
|---------|--------------|------------|
| **Code indexing** | HIGH | Medium |
| **Causal chains** | HIGH | High |
| **Visual graph** | MEDIUM | High |
| **Different retrieval** | MEDIUM | High |

---

## Implementation Plan (If Integrated)

### 1. Add neural_memory.py

```python
import asyncio
from neural_memory import Brain
from neural_memory.storage import InMemoryStorage
from neural_memory.engine.encoder import MemoryEncoder
from neural_memory.engine.retrieval import ReflexPipeline

class NeuralMemoryClient:
    def __init__(self):
        self.storage = InMemoryStorage()
        self.brain = Brain.create("overkill")
        self.encoder = MemoryEncoder(self.storage, self.brain.config)
        self.pipeline = ReflexPipeline(self.storage, self.brain.config)
    
    async def remember(self, content: str, mem_type: str = "fact"):
        """Store a memory"""
        await self.encoder.encode(content)
    
    async def recall(self, query: str, depth: int = 2):
        """Recall through spreading activation"""
        result = await self.pipeline.query(query)
        return result.context
    
    async def index_code(self, path: str):
        """Index codebase"""
        # nmem index src/
        pass
```

### 2. CLI Commands

```bash
# Remember (like our add)
overkill neural remember "Fixed auth bug"

# Recall (like our search)
overkill neural recall "auth bug"

# Index code
overkill neural index /path/to/code

# Context injection
overkill neural context
```

### 3. Integration

```python
async def hybrid_search(query):
    # ... existing search ...
    
    # Add neural memory option
    if use_neural:
        neural_results = await neural_client.recall(query)
        results.extend(neural_results)
    
    return rank_with_neuroscience(results)
```

---

## Pros/Cons

### Pros
- Brain-like retrieval (spreading activation)
- Code indexing
- Causal chain tracing
- Visual tools

### Cons
- Requires `pip install neural-memory`
- More complex
- Overlaps with what we built
- Not as proven as ChromaDB

---

## Recommendation

### For overkill-memory-system v1.6:

**Keep neural-memory as optional addon** - not integrated into core.

Reason:
1. We already have similar functionality (brain regions)
2. Our system is more comprehensive
3. Adds complexity without major benefit
4. Use neural-memory for specific use cases (code indexing)

### Future:
- Could add "code indexing" as separate feature
- Could add causal chain tracking to ACC
- Not urgent

---

## Summary

| Aspect | neural-memory | Our System |
|--------|---------------|------------|
| Retrieval | Spreading activation | Parallel tiers + ranking |
| Storage | Neural graph | Multi-tier |
| Brain-like | Yes | Yes (6 regions) |
| Code indexing | Yes | Via file-search |
| Complexity | High | Medium |

**Verdict**: Complementary, not essential. Keep as optional tool.

---

*Deep analysis - overkill-memory-system*
