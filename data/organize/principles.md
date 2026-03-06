# Organization Principles

Fundamentals that apply across all organization decisions.

## Naming

### Consistency Over Cleverness
- Same type of thing → same naming pattern
- Predictable > memorable
- If someone can guess the name, it's good

### Common Patterns
| Type | Pattern | Example |
|------|---------|---------|
| Dates | YYYY-MM-DD prefix | 2024-01-15-meeting-notes.md |
| Versions | vX.Y.Z suffix | design-v1.2.0.fig |
| Status | prefix | draft-, final-, archived- |
| Type | suffix | -spec, -test, -config |

### Avoid
- Spaces (use hyphens or underscores)
- Special characters
- Ambiguous abbreviations
- Numbers without context (v1 vs version-1-initial)

## Hierarchy

### Depth vs Breadth
- Max 3-4 levels deep (deeper = harder to navigate)
- 5-15 items per folder (fewer = overstructured, more = cluttered)
- If navigating feels like work, restructure

### Grouping Principles
| Group by | When |
|----------|------|
| Project | Work spans multiple types |
| Type | Same processing for all items |
| Date | Temporal access pattern |
| Status | Workflow-based access |
| Owner | Multi-person collaboration |

### Escape Hatches
- `_archive/` for old but kept items
- `_temp/` or `_scratch/` for work in progress
- `_reference/` for external/imported items

## Access Optimization

### Frequency-Based Placement
- Daily access → top level or pinned
- Weekly access → one level deep
- Monthly access → can be deeper
- Rarely accessed → archive

### Search vs Navigate
- Will they search by name? → naming matters most
- Will they browse? → hierarchy matters most
- Both? → optimize for most common pattern

## Scale Patterns

### Signs Structure Won't Scale
- Folder has 50+ items
- Deeply nested (5+ levels)
- Inconsistent naming within same level
- "Misc" or "Other" folders growing

### Future-Proofing
- Leave room for growth (don't over-partition early)
- Use patterns that extend naturally
- Document your structure decisions
