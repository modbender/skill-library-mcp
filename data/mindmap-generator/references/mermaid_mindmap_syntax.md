# Mermaid Mindmap Syntax — Quick Reference

> For the mindmap-generator OpenClaw skill. Full docs: https://mermaid.js.org/syntax/mindmap.html

---

## Basic Structure

Mermaid mindmaps use **indentation** to define hierarchy:

```
mindmap
  root((Central Topic))
    Branch A
      Leaf 1
      Leaf 2
    Branch B
      Leaf 3
```

- Each level is indented further than its parent
- The root node is the first node (typically uses circle shape)
- No connectors or arrows needed — hierarchy is implicit

---

## Node Shapes

| Syntax | Shape | Best Used For |
|---|---|---|
| `id((text))` | Circle | Root node |
| `id(text)` | Rounded rectangle | Categories, groups |
| `id[text]` | Square | Action items, tasks |
| `id)text(` | Cloud | Ideas, open questions |
| `id))text((` | Bang/explosion | Urgent items, blockers |
| `id{{text}}` | Hexagon | Decisions |
| `Plain text` | Default (rounded) | Details, notes |

---

## Icons

Add icons using `::icon()` after a node:

```
mindmap
  root((Project))
    Research
    ::icon(fa fa-book)
    Development
    ::icon(fa fa-code)
```

Requires Font Awesome or Material Design Icons to be available.

---

## CSS Classes

Add custom styling with `:::className`:

```
mindmap
  root((Project))
    Urgent Task
    :::urgent
    Normal Task
```

Classes must be defined by the site/application rendering the mindmap.

---

## Markdown Strings

Use backtick-wrapped strings for rich text:

```
mindmap
  root((Project))
    id1["`**Bold text** with
    multiple lines`"]
    id2["`Regular *italic* text`"]
```

---

## Layout Options

Default is radial layout. Tidy Tree is also available:

```
---
config:
  layout: tidy-tree
---
mindmap
  root((Topic))
    A
    B
    C
```

---

## Best Practices for Agent-Generated Mindmaps

1. **Keep labels short** — 3-6 words per node
2. **Max 7 branches** from root (Miller's Law)
3. **Max 3-4 levels** deep for mobile readability
4. **Use shapes intentionally** — don't make every node a different shape
5. **Root always circle** `(( ))` — visual anchor
6. **Avoid special characters** in node text: `(`, `)`, `[`, `]`, `{`, `}` break parsing unless they're shape delimiters
7. **Test rendering** — some emoji work in Mermaid, some don't. Stick to: ✅ ⏳ ❌ ⚠️ 💡
8. **Consistent indentation** — use 2 or 4 spaces, don't mix tabs

---

## Common Pitfalls

- **No colon in node text** — `Task: Do thing` may break. Use `Task - Do thing`
- **No parentheses in plain text** — `Review (draft)` breaks parsing. Use `Review draft`
- **Empty nodes** — every node needs text content
- **Inconsistent indentation** — Mermaid will guess parent, but may guess wrong
