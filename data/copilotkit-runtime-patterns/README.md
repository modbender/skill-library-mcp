# CopilotKit Runtime Patterns

A structured skill for CopilotKit server-side runtime configuration, optimized for agents and LLMs.

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
| 1 | Endpoint Setup | 3 | `endpoint-` |
| 2 | Agent Runners | 3 | `runner-` |
| 3 | Middleware | 3 | `middleware-` |
| 4 | Security | 3 | `security-` |
| 5 | Performance | 3 | `perf-` |

## Getting Started

```bash
pnpm install
pnpm build
pnpm validate
```
