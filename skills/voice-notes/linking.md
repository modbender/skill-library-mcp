# Linking System

## Link Types

| Type | Syntax | Use Case |
|------|--------|----------|
| Parent-child | `[[parent]]` / `[[child]]` | Note split into sections |
| Peer | `[[related]]` | Same topic, different angle |
| Evolution | `[[supersedes:old]]` | Thinking changed |

## When to Link

| Situation | Action |
|-----------|--------|
| Same topic, different angle | Peer link |
| Newer version of idea | Evolution link |
| Detail from larger note | Parent-child |
| Contradictory thoughts | Link both, note conflict |

## Link Syntax

Use wiki-style: `[[note-slug]]`

In `index.md`, maintain link map:
```markdown
## Link Map
[[note-a]] <-> [[note-b]] - peers
[[note-c]] -> [[note-d]] - c supersedes d
[[note-e]] contains [[note-f]] - e contains f
```

## Breaking Up Large Notes

When note exceeds ~100 lines:

1. Identify natural sections
2. Create child notes
3. Parent becomes overview:

```markdown
# Big Topic

See details:
- [[big-topic-part-a]]
- [[big-topic-part-b]]

## Summary
{Brief overview}
```

## Automatic Detection

When processing new note:
1. Extract key concepts
2. Search existing notes
3. Suggest or auto-add links
4. Update index.md link map

## Orphan Check

Periodically verify:
- Notes with no links -> missed connections?
- Dead links -> archived/renamed?
- Isolated clusters -> could connect?
