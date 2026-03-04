---
name: skill-build-helper
description: Create or optimize an OpenClaw skill. Use when the user wants to build a new skill, improve an existing one, review a SKILL.md, or prepare a skill for ClawHub publishing.
metadata: {"openclaw":{"requires":{"bins":["jq"]}}}
---

# Skill Builder

A meta-skill for creating and optimizing OpenClaw skills following official best practices. Guides you through a structured workflow from intent to publish-ready skill.

## Workflow

### 1. Understand intent

Determine the mode:

| Mode | Trigger |
|------|---------|
| **Create** | User wants a new skill |
| **Optimize** | User wants to improve or review an existing skill |

**If creating**: Ask the user for 2-3 concrete usage examples (what would they say to trigger this skill, what should happen). These examples drive the description and workflow design.

**If optimizing**: Read the existing `SKILL.md` and note its current structure before proceeding.

### 2. Scaffold the directory

Create the skill directory under `~/workspace/skills/`:

```
<skill-name>/
├── SKILL.md          (required — agent instructions)
├── README.md         (recommended for published skills)
├── scripts/          (if deterministic code is needed)
└── references/       (if large docs needed on-demand)
```

**Naming rules**:
- Lowercase, hyphens only (no underscores, no spaces)
- Max 64 characters
- Verb-led when possible (e.g., `workout-track`, `skill-builder`)
- Folder name must match the `name` field in frontmatter

### 3. Write the SKILL.md

The SKILL.md is the core file — it contains the agent's instructions for executing the skill.

#### Frontmatter (YAML)

Three fields:

```yaml
---
name: <skill-name>
description: <what it does>. Use when <trigger context>.
metadata: {"openclaw":{"requires":{"bins":["list","of","binaries"]}}}
---
```

- **`name`**: Must match folder name exactly
- **`description`**: Primary trigger mechanism. Include "Use when..." to help the agent decide when to activate. Be specific to avoid overlap with other skills
- **`metadata`**: Declare runtime dependencies. Load `{baseDir}/references/frontmatter-spec.md` for the full reference if needed

#### Body structure

Write the body following these rules:

1. **Opening line**: One sentence explaining what the skill does
2. **`## Workflow`**: Numbered H3 steps (`### 1. Step name`) — imperative form
3. **Tables** for structured data (fields to extract, flags, mappings)
4. **Code blocks** with exact commands — use `exec` tool JSON format:
   ```json
   {
     "tool": "exec",
     "command": "<shell command here>"
   }
   ```
5. **`## Examples`**: Table with realistic input/output pairs (minimum 3 rows)
6. **Error handling section**: What to do when things fail — always present, never retry silently

#### Key rules

- Keep SKILL.md under **500 lines** — move detailed docs to `references/`
- Use **`{baseDir}`** for paths within the skill directory (e.g., `{baseDir}/scripts/run.sh`)
- **No hardcoded secrets** — read from env vars, `.env`, or `openclaw.json` via `jq`
- **Imperative form** throughout ("Extract the URL", not "The URL is extracted")
- **Confirmation before state changes** — show a summary and ask before writing to DB, sending messages, etc.

### 4. Write the README.md

User-facing documentation with these sections:

```markdown
# <Skill Name>

<What it does — 1-2 lines>

## Requirements

- <binary or service 1>
- <binary or service 2>

## Setup

<Step-by-step setup instructions>

## Usage

<2-3 natural language examples showing what the user would say>

## Install

\`\`\`bash
clawhub install <author>/<skill-name>
\`\`\`
```

### 5. Quality check

Load `{baseDir}/references/checklist.md` and validate every item:

- [ ] Frontmatter has `name` + `description`
- [ ] `name` matches folder name
- [ ] Description includes "Use when..." trigger phrases
- [ ] No hardcoded secrets or API keys
- [ ] `{baseDir}` used for all internal paths
- [ ] Metadata declares runtime dependencies (`requires.bins`, `requires.env`)
- [ ] Error handling section is present
- [ ] Examples section with at least 3 rows
- [ ] SKILL.md is under 500 lines
- [ ] README.md present for published skills
- [ ] Confirmation step before any state-changing operation

Report the results as a checklist to the user, noting any failures.

### 6. Optimize (existing skills only)

When reviewing an existing skill:

1. Read the current SKILL.md
2. Run the quality check from Step 5
3. List each issue found with a concrete fix
4. Ask the user which fixes to apply
5. Apply approved fixes

Do not rewrite an entire SKILL.md — make targeted, minimal edits.

## Examples

| User says | Mode | Action |
|-----------|------|--------|
| "I want to create a skill that tracks my reading list" | Create | Scaffold `reading-track/`, gather examples, write SKILL.md + README.md |
| "Can you review my sm-saver skill?" | Optimize | Read `sm-saver/SKILL.md`, run checklist, report issues |
| "Build a skill for checking server status" | Create | Scaffold `server-check/`, gather examples, write SKILL.md + README.md |
| "Improve the reminder skill for ClawHub" | Optimize | Read `reminder/SKILL.md`, run checklist, add README.md if missing |
