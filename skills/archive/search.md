# Search Patterns

## Query Types

### By Concept (most common)
User: "What do I have about pricing strategies?"
→ Search content + tags + summaries semantically
→ Return: title, summary, when archived, why saved

### By Time
User: "Something I saved last week about APIs"
→ Filter by date range + topic
→ Fuzzy match: "last week" = 7-14 days ago

### By Project
User: "Everything for ClawMsg project"
→ Filter by project field
→ Return grouped by type

### By Author/Source
User: "Papers by Hinton"
→ Search author field
→ Include: co-authored, cited by

### By Type
User: "All videos I've archived"
→ Filter by type field
→ Sort by date

## Response Format

**For single match:**
```
Found: [Title]
Saved: [date] | Why: [context]
Summary: [2-3 lines]
[Link or path]
```

**For multiple matches:**
```
Found 5 items about "pricing":

1. **[Title]** (article, 3 weeks ago)
   Why: [context]

2. **[Title]** (video, 2 months ago)
   Why: [context]

[...]
Want details on any of these?
```

## No Results
If nothing found:
1. Try broader semantic search
2. Suggest: "Nothing exact. Related: [similar topics you have]"
3. Never say "I don't remember" — check first

## Search Performance
- memory.md (HOT) → always checked first
- index.md → for tag/project filtering
- items/ → full content search when needed
