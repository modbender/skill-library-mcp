# CopilotKit Agent Patterns

A structured skill for CopilotKit agent architecture and implementation, optimized for agents and LLMs.

## Structure

- `rules/` - Individual rule files (one per rule)
  - `_sections.md` - Section metadata (titles, impacts, descriptions)
  - `_template.md` - Template for creating new rules
  - `{prefix}-{name}.md` - Individual rule files
- `metadata.json` - Document metadata (version, organization, abstract)
- __`AGENTS.md`__ - Compiled output (generated)

## Categories

| # | Category | Rules | Prefix |
|---|----------|-------|--------|
| 1 | Agent Architecture | 4 | `architecture-` |
| 2 | AG-UI Protocol | 5 | `agui-` |
| 3 | State Management | 4 | `state-` |
| 4 | Human-in-the-Loop | 4 | `hitl-` |
| 5 | Generative UI Emission | 3 | `genui-` |

## Getting Started

```bash
pnpm install
pnpm build
pnpm validate
```
