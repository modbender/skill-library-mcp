# Querying the Archive

## Why This Matters

The archive isn't just storage — it's a searchable knowledge base of what your followed sources have said over time.

---

## Query Types

### By Person
- "What has @naval said about AI?"
- "When did @dhh last post about Rails?"
- "Show me @competitor's last 10 tweets"

### By Topic
- "What are people saying about React 19?"
- "Find all mentions of layoffs this quarter"
- "Who's talking about AI safety lately?"

### By Time
- "What did I miss yesterday?"
- "What was trending last week?"
- "Show me Q4 2025 archive for @company"

### Cross-reference
- "What did @personA and @personB both discuss?"
- "Show me contradictions between sources on [topic]"
- "When did [topic] first appear in my feeds?"

---

## Query Response Format

```markdown
## Query: "What has @naval said about AI?"

### Results (7 matches, last 6 months)

**2025-02-10** — Twitter thread
"AI is leverage. The people who understand both AI and leverage will do extremely well."
→ Full thread: [link]

**2025-01-15** — Podcast appearance (Lex Fridman)
Discussed AI replacing knowledge work. Key quote: "..."
→ Episode: [link], timestamp: 45:20

**2024-12-03** — Twitter
Brief comment on AI regulation
→ [link]

### Summary
Naval has posted about AI 7 times recently, focusing on:
- AI as leverage/amplifier
- Skepticism of AI regulation
- Opportunities for individuals vs companies
```

---

## Search Syntax

| Query | Meaning |
|-------|---------|
| `@person topic` | What person said about topic |
| `topic since:2025-01` | Topic mentions since date |
| `topic source:twitter` | Topic on specific platform |
| `"exact phrase"` | Literal match |
| `-keyword` | Exclude keyword |
| `topic1 AND topic2` | Both required |
| `topic1 OR topic2` | Either matches |

---

## Timeline Reconstruction

For investigations or deep research:

"Build a timeline of @company"

```markdown
## @company Timeline

2025-02-10: New product announced (Twitter)
2025-02-05: CTO departed (LinkedIn)
2025-01-20: Pricing increased 15% (website change)
2025-01-15: Series C closed (press release)
...
```

---

## Export Options

- **Markdown** — for notes/Obsidian
- **JSON** — for programmatic use
- **PDF** — for sharing/archival
- **Timeline** — visual representation
