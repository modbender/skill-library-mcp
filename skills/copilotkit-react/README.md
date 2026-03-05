# CopilotKit React Patterns

A structured skill for CopilotKit React best practices, optimized for agents and LLMs.

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
| 1 | Provider Setup | 4 | `provider-` |
| 2 | Agent Hooks | 5 | `agent-` |
| 3 | Tool Rendering | 5 | `tool-` |
| 4 | Context & State | 4 | `state-` |
| 5 | Chat UI | 4 | `ui-` |
| 6 | Suggestions | 3 | `suggestions-` |

## Getting Started

```bash
pnpm install
pnpm build
pnpm validate
```
