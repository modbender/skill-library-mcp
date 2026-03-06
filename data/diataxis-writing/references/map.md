# The Diataxis Map Model

Theory Source: https://diataxis.fr/map/

---

## Core Idea of the Map

Diataxis describes a **two-dimensional structure**, not a list. This is the key reason it's effective as a documentation organization guide.

```
                    ACTION                 COGNITION
                    ───────                ─────────
        ACQUISITION │                      │              │
        (Study)     │   Tutorial           │  Explanation │
                    │                      │              │
                    ─────────────────────────────────────
        APPLICATION │                      │              │
        (Work)      │   How-to Guide       │  Reference   │
                    │                      │              │
```

---

## Why Two-Dimensional Structure is Effective

### Problem: Limitations of One-Dimensional Lists

When documentation lacks clear structure, creators often try to organize content around product features. This leads to:

1. **Inconsistency** - Different documents use different organization methods
2. **Arbitrariness** - Why this list rather than another?
3. **Hard to maintain** - Structure broken when new features appear

### Diataxis Solution

Two-dimensional structure provides:
- **Clear expectations** (for readers) - Know the purpose of each documentation part
- **Clear guidance** (for authors) - Know how to write and organize

---

## Four Type Comparison

| Dimension | Tutorial | How-to | Reference | Explanation |
|-----------|----------|--------|-----------|-------------|
| **What they do** | Introduce, educate, lead | Guide | State, describe, inform | Explain, clarify, discuss |
| **Answers the question** | "Can you teach me to...?" | "How do I...?" | "What is...?" | "Why...?" |
| **Oriented to** | Learning | Goals | Information | Understanding |
| **Purpose** | To provide a learning experience | To help achieve a particular goal | To describe the machinery | To illuminate a topic |
| **Form** | A lesson | A series of steps | Dry description | Discursive explanation |
| **Analogy** | Teaching a child how to cook | A recipe in a cookery book | Information on the back of a food packet | An article on culinary social history |

---

## Boundary Blur Problem

### Natural Affinity Relationships

```
Tutorial ←→ How-to (both guide action)
     ↓           ↓
Serve study   Serve work
     ↑           ↑
Explanation ←→ Reference (both provide knowledge)
```

### Common Confusions

1. **Tutorial and How-to confusion** - Most common confusion
2. **How-to and Reference confusion** - Mixing facts into guidance
3. **Reference and Explanation confusion** - Mixing explanation into description
4. **Explanation and Tutorial confusion** - Mixing steps into discussion

### Consequences of Confusion

- Writing style and content make their way into inappropriate places
- Structural problems - hard to maintain documentation discipline
- Worst case: Tutorial and How-to completely collapse, unable to meet either need

---

## Documentation Need Cycle

Users experience different phases in their interaction with a product:

```
        ┌─────────────────┐
        │   Learning      │
        │  (Tutorial)     │
        │  Learning-oriented│
        └────────┬────────┘
                 │
                 ↓
        ┌─────────────────┐
        │   Working       │
        │  (How-to)       │
        │  Goal-oriented  │
        └────────┬────────┘
                 │
                 ↓
        ┌─────────────────┐
        │   Looking up    │
        │  (Reference)    │
        │  Information-oriented│
        └────────┬────────┘
                 │
                 ↓
        ┌─────────────────┐
        │   Reflecting    │
        │  (Explanation)  │
        │  Understanding-oriented│
        └────────┬────────┘
                 │
                 └──────→ Back to learning (new topic or deeper)
```

### Important Note

This cycle is **not literal sequence**:
- Users can enter documentation from any point
- Needs change from moment to moment
- But cycle concept corresponds to how people actually become expert in a craft

---

## Map Applications

### As an Author

Use the map to:
1. **Locate content** - Determine which type document should belong to
2. **Maintain purity** - Avoid type conflation
3. **Organize structure** - Build documentation set around four types

### As a Reader

Use the map to:
1. **Navigate quickly** - Find corresponding type based on needs
2. **Adjust expectations** - Understand purpose of each type
3. **Identify problems** - Discover type-confused documents

---

## Map Limitations

Map is a simplified model, real documentation may:
- Need complex hierarchical structure
- Target multiple user types
- Span multiple topic areas

Solution: Refer to [complex-hierarchies](complex-hierarchies.md)

---

## Usage Recommendations

### Planning Documentation Sets

1. Ensure all four types are covered
2. Check if any types are missing
3. Use map to discover structural problems

### Locating Single Document

1. Ask: Content type (action/cognition)?
2. Ask: User state (acquisition/application)?
3. Locate on map

### Refactoring Existing Documents

1. Identify current type
2. Identify target type
3. Move and reorganize content

---

**Version**: 1.0  
**Source**: https://diataxis.fr/map/  
**Compiled by**: Zhua Zhua
