# Integration Analysis: RAG-Search + Knowledge Graph

## Installed Skills

| Skill | Purpose | Relevance |
|-------|---------|-----------|
| **rag-search** | RAG for backend retrieval | ⚠️ Specific (occupational health) |
| **knowledge-graph** | File-based knowledge graph | ✅ High |

---

## Analysis

### rag-search
- **Purpose**: RAG backend for specific documents
- **Issue**: Very specific to occupational health documents (GBZ standards)
- **Verdict**: Not generally useful for memory system - too specialized

### knowledge-graph
- **Purpose**: File-based knowledge graph with atomic facts
- **Structure**: `life/areas/<kind>/<slug>/items.json`
- **Features**: 
  - Add facts with categories
  - Supersede old facts (versioning)
  - Auto-generate summaries
  - Consistent IDs

---

## Knowledge Graph Integration

### Current System
Our system already has:
- Git-Notes (structured knowledge)
- Strategy notes
- Diary entries

### What knowledge-graph Adds

| Feature | Our System | knowledge-graph |
|---------|------------|-----------------|
| Atomic facts | Scattered | ✅ Centralized |
| Versioning | No | ✅ Supersede old |
| Summaries | Manual | ✅ Auto-generate |
| Categories | Tags | ✅ Structured |

### Integration Strategy

#### Option 1: Keep Separate
Keep knowledge-graph as separate tier for structured facts.

#### Option 2: Integrate (Recommended)
Add knowledge-graph as new tier: **CURIATED**

```
Tier: CURATED (knowledge-graph)
  - Atomic facts (life/areas/**)
  - Entity summaries
  - Version history
```

### Implementation

```python
# Add to search tiers
def search_knowledge_graph(query: str) -> list[dict]:
    """Search knowledge graph facts"""
    kg_path = Path("~/.clowdbot/life/areas").expanduser()
    results = []
    
    # Search all entities
    for entity_path in kg_path.rglob("items.json"):
        with open(entity_path) as f:
            facts = json.load(f)
            for fact in facts:
                if query.lower() in fact["content"].lower():
                    results.append({
                        "content": fact["fact"],
                        "entity": fact["entity"],
                        "category": fact["category"],
                        "score": simple_match(query, fact["fact"])
                    })
    
    return results
```

### CLI Commands

```bash
# Add fact to knowledge graph
overkill kg add --entity "people/kasper" --category "preference" --fact "Prefers TypeScript"

# Supersede fact
overkill kg supersede --entity "people/kasper" --old <fact-id> --fact "New fact"

# Generate summary
overkill kg summarize --entity "people/kasper"

# Search knowledge graph
overkill kg search "preference"
```

---

## Recommendation

### Keep rag-search? 
**No** - Too specialized, flagged as suspicious.

### Integrate knowledge-graph?
**Yes** - Adds:
- Structured atomic facts
- Versioning (supersede)
- Auto-summaries
- Entity categories

### New Tier: KNOWLEDGE-GRAPH

```
┌─────────────────────────────────────┐
│           KNOWLEDGE GRAPH            │
│                                     │
│  Entities: people/** , projects/**  │
│  Facts: items.json (atomic)         │
│  Summaries: summary.md              │
│                                     │
│  Weight: 0.3 (high value)          │
└─────────────────────────────────────┘
```

---

## Summary

| Skill | Action | Reason |
|-------|--------|--------|
| rag-search | ❌ Remove | Too specific, flagged |
| knowledge-graph | ✅ Integrate | Adds structured KG |

---

*Analysis for overkill-memory-system v1.6*
