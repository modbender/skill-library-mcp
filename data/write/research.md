# Research Reference

## When to Research
- Article on unfamiliar topic
- User requests "well-researched" or "thorough"
- Config `depth: "thorough"`
- Long-form content (> 1000 words)

## Research Workflow

1. **Create research notes**
   ```
   research/{piece-id}/
     sources.md      # links, citations
     notes.md        # key findings
     outline.md      # structure based on research
   ```

2. **Per-section research** (for long pieces)
   - Spawn sub-agent per section topic
   - Each returns: key points, sources, quotes
   - Compile into notes.md

3. **Research before writing**
   - Complete research phase BEFORE drafting
   - Reference notes during draft
   - Cite sources in content if required

## Research Depth by Config

| Depth | Research Actions |
|-------|------------------|
| `quick` | No research, use existing knowledge |
| `standard` | Quick web search, 2-3 sources |
| `thorough` | Deep research, 5+ sources, verify facts |

## For Books / Long Articles

Each chapter/section gets:
1. Research sub-agent
2. Research notes in `research/{piece-id}/section_N/`
3. Draft based on research
4. Audit
5. Next section

## Research Output Format

```markdown
# Research: [Topic]

## Key Points
- Point 1 (Source: X)
- Point 2 (Source: Y)

## Sources
1. [Title](URL) — relevance note
2. [Title](URL) — relevance note

## Quotes to Use
> "Quote" — Author, Source

## Questions to Address
- [ ] Question 1
- [ ] Question 2
```
