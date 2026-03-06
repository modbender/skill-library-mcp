# Session Handoff

Create comprehensive handoff documents that enable fresh AI agents to seamlessly continue work with zero ambiguity. Solves the long-running agent context exhaustion problem.

## What's Inside

- CREATE workflow (scaffold, complete, validate, confirm)
- RESUME workflow (find handoffs, check staleness, load and verify, begin work)
- Handoff chaining for long-running projects
- Validation scripts with quality scoring (0-100)
- Staleness detection (FRESH, SLIGHTLY_STALE, STALE, VERY_STALE)
- Handoff template with required sections
- Resume checklist for picking up previous work

## When to Use

- User requests handoff, memory, or context save
- Context window approaches capacity
- Major task milestone completed
- Work session ending
- Resuming work with an existing handoff
- Triggered by: "save state", "create handoff", "context is full", "I need to pause", "resume from", "continue where we left off", "load handoff", "save progress"

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/tools/session-handoff
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/tools/session-handoff .cursor/skills/session-handoff
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/tools/session-handoff ~/.cursor/skills/session-handoff
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/tools/session-handoff .claude/skills/session-handoff
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/tools/session-handoff ~/.claude/skills/session-handoff
```

---

Part of the [Tools](..) skill category.
