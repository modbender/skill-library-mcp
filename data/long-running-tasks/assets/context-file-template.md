# Project Context File Template

Create this file in the project root (commonly named `CLAUDE.md` or `AGENTS.md`) so cold-start agents have the context they need without exploring the codebase.

```markdown
# [Project Name]

## Stack
- Language, framework, major dependencies
- Test framework and how to run tests
- Build system

## Architecture
- src/module/ — what it does
- src/other/ — what it does
- tests/ — test organization

## Commands
\`\`\`bash
# Run unit tests
<command>

# Run all tests
<command>

# Lint / type check
<command>
\`\`\`

## Commit Convention
<format description>

## Current Phase
What's being worked on now. Link to TODO.md for details.

## Environment
- Required env vars and where they're set
- Setup steps (venv activation, config files, etc.)
- Do not include secrets — reference where they're stored
```

## Guidelines

- Keep under 100 lines — agents read this on every cold start
- Include runnable commands, not just descriptions
- Update when phases change or architecture shifts
- Reference secret locations (e.g., "API key in ~/.zshrc"), never inline secrets
