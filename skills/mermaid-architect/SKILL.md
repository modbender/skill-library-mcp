---
name: mermaid-architect
description: Generate beautiful, hand-drawn Mermaid diagrams with robust syntax (quoted labels, ELK layout). Use this skill when the user asks for "diagram", "flowchart", "sequence diagram", or "visualize this process".
---

# Mermaid Architect

## Usage
- **Role**: Diagram Architect & Designer.
- **Trigger**: "Draw this", "Make a diagram", "Visualize".
- **Output**: Mermaid code block (`mermaid`) + Explanation.

## Capabilities
1.  **Flowcharts**: Process mapping, decision trees.
2.  **Sequence Diagrams**: API calls, user interactions.
3.  **Class Diagrams**: OOP structures, database schemas.
4.  **State Diagrams**: Lifecycle management.

## Guidelines
- Always use **quoted strings** for node labels when they contain parentheses, commas, or colons.
- Use safe node IDs: no spaces; use camelCase, PascalCase, or underscores. Avoid reserved IDs: `end`, `subgraph`, `graph`, `flowchart`.
- Prefer `TD` (Top-Down) for hierarchies, `LR` (Left-Right) for timelines.
- Use `subgraph id [Label]` with an explicit ID and label (no spaces in ID).
- See [references/syntax-guide.md](references/syntax-guide.md) for full safe-syntax rules.

## Reference Materials
- [Syntax Guide](references/syntax-guide.md)
- [Example: Microservices](assets/examples/microservice-arch.mmd)
- [Example: Sequence API](assets/examples/sequence-api.mmd)
- [Example: State Lifecycle](assets/examples/state-lifecycle.mmd)

## Validation
Run the validator on one or more `.mmd` files:
```bash
scripts/validate-mmd assets/examples/*.mmd
```
