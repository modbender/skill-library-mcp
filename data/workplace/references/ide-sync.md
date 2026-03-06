# IDE Sync Guide

## Overview

`workplace sync <ide>` generates context files so external coding tools (Cursor, Claude Code, OpenCode) can understand the project's workplace config, agents, and conventions.

## Cursor

### Output: `.cursor/rules/workplace.mdc`

```bash
mkdir -p .cursor/rules
```

Generate MDC format:

```mdc
---
description: Workplace context for {workplace_name}
globs:
alwaysApply: true
---

# {workplace_name}

## Project
- **Path:** {path}
- **Language:** {language}
- **Framework:** {framework}
- **Description:** {description}

## Structure
{structure.json summarized as tree}

## Agents
{for each agent in .workplace/agents/:}
### {name} — {role}
{agent instructions summary}

## Deployment
{summary of deploy/{dev,main,pre}.md}

## Conventions
- Inter-agent communication via .workplace/chat.md
- Agent definitions in .workplace/agents/*.md
- Structure tracking in .workplace/structure.json
```

### Implementation Steps

1. Read `.workplace/config.json`
2. Read `.workplace/structure.json` — convert to indented tree
3. Read each `.workplace/agents/*.md` — extract frontmatter + key instructions
4. Read `.workplace/deploy/*.md` — summarize
5. Write `.cursor/rules/workplace.mdc` with MDC frontmatter

## Claude Code

### Output: `CLAUDE.md` (project root)

If `CLAUDE.md` already exists, append a workplace section. If not, create it.

**Marker comments** to enable updates without clobbering user content:

```markdown
<!-- WORKPLACE:START -->
# Workplace: {workplace_name}

## Project
...

## Agents
...

## Structure
...
<!-- WORKPLACE:END -->
```

### Implementation Steps

1. Read `.workplace/config.json`
2. Read agents and structure (same as Cursor)
3. If `CLAUDE.md` exists:
   - Check for `<!-- WORKPLACE:START -->` marker
   - If found: replace content between START/END markers
   - If not found: append section at the end
4. If `CLAUDE.md` doesn't exist: create with workplace section
5. Write `CLAUDE.md`

## OpenCode

### Output: `opencode.jsonc` → instructions field

OpenCode uses a `instructions` field in its config. Add workplace context there.

### Implementation Steps

1. Read existing `opencode.jsonc` (or create minimal one)
2. Read workplace config, agents, structure
3. Build instructions string with workplace context
4. Update or create the `instructions` field
5. Write `opencode.jsonc` (preserve comments if possible — use sed/awk rather than JSON parse)

### Example

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": "## Workplace: my-app\n\nPath: /path/to/project\nAgents: coder, reviewer\n\n..."
}
```

## Sync All

`workplace sync all` runs sync for all three IDEs that are detected:

1. Check if `.cursor/` exists or `cursor` is installed → sync cursor
2. Check if `claude` CLI is installed → sync claude
3. Check if `opencode.jsonc` exists or `opencode` is installed → sync opencode

## Re-sync

Run `workplace sync <ide>` after:
- Adding or modifying agents
- Changing `config.json` settings
- Updating deploy docs
- Re-scanning structure

The sync command is idempotent — safe to run multiple times.

## Shared Context

All three IDEs get the same core information:

1. **Project identity** — name, path, language, framework, description
2. **File structure** — summarized from `structure.json`
3. **Agent roles** — who does what, handoff patterns
4. **Deploy info** — how to run in each environment
5. **Conventions** — chat.md protocol, agent file locations

The format adapts to each IDE's native config style.
